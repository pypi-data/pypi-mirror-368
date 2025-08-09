#!/usr/bin/env python3
import sys
import os
import argparse
import logging
import json
import tabulate
import time
import requests
import tqdm
import datetime

from .lib.api_client import APIClient
from .lib.spark_stage_analyzer import SparkStageAnalyzer
from .lib.s3_uploader import S3Uploader
from .lib.utils import print_error_box
from .config_cli import extract_databricks_driver_id, extract_databricks_app_id

def setup_logging(verbose=False, debug=False):
    """Set up logging with appropriate verbosity level"""
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.CRITICAL
    
    class TqdmLoggingHandler(logging.Handler):
        def emit(self, record):
            if record.name == 'urllib3.connectionpool' and 'Retrying' in record.getMessage():
                return
            if 'Failed to establish a new connection' in record.getMessage():
                return
            if 'Invalid URL' in record.getMessage():
                return
            if 'No host supplied' in record.getMessage():
                return
            if 'Failed to parse' in record.getMessage():
                return
            if 'Cookie format may be invalid' in record.getMessage():
                return
            try:
                msg = self.format(record)
                tqdm.tqdm.write(msg)
            except Exception:
                self.handleError(record)
    
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    log_format = '%(levelname)s: %(message)s'
    formatter = logging.Formatter(log_format)
    
    handler = TqdmLoggingHandler()
    handler.setFormatter(formatter)
    
    logging.getLogger('urllib3').setLevel(logging.ERROR)
    logging.getLogger('requests').setLevel(logging.ERROR)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)
    
    return logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Spark Application Analysis Tool')
    parser.add_argument('--show-readme', action='store_true',
                        help='Display the README documentation')
    parser.add_argument('-l', '--local', action='store_true', 
                        help='Run in local mode using localhost configuration')
    parser.add_argument('-b', '--browser', action='store_true',
                        help='Run in browser mode (when cookies are needed for authentication)')
    parser.add_argument('-s', '--stage_id', type=str, default=None,
                        help='Stage ID to analyze')
    parser.add_argument('-a', '--app_id', type=str, default=None,
                        help='Application ID to analyze')
    parser.add_argument('--opt-out', type=str, default="",
                        help='Comma-separated list of fields to opt out of (name,description,details)')
    parser.add_argument('--upload-url', type=str, default=None,
                        help='URL to upload the JSON output to (will use gzip compression)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose logging (INFO level)')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable debug logging (DEBUG level, includes all requests/responses)')
    parser.add_argument('--env', type=str, choices=['staging', 'production'], default='production',
                        help='Environment to use (staging requires SPARK_ANALYZER_STAGING_* env vars, production is default)')
    parser.add_argument('--cost-estimator-id', type=str, default=None,
                        help='Cost estimator user ID (provided when you signed up for the service)')
    parser.add_argument('--server-url', type=str, default=None,
                        help='Custom Spark History Server URL (e.g., http://localhost:18080)')
    parser.add_argument('--batch-size', type=int, default=50,
                        help='Number of stages to process in each batch (default: 50)')
    parser.add_argument('--live-app', action='store_true',
                        help='Indicate this is a live/running application (enables reverse processing and stage validation to handle race conditions)')
    
    args = parser.parse_args()
    
    if not args.live_app:
        try:
            import configparser
            config = configparser.ConfigParser()
            config_paths = ["configs/config.ini"]
            
            for path in config_paths:
                if os.path.exists(path):
                    config.read(path)
                    if 'processing' in config and 'live_app' in config['processing']:
                        try:
                            args.live_app = config.getboolean('processing', 'live_app')
                            logging.debug(f"Live app setting from config: {args.live_app}")
                        except (ValueError, configparser.Error):
                            logging.warning("Invalid live_app setting in config, using default: False")
                            args.live_app = False
                    break
        except Exception as e:
            logging.debug(f"Could not read live_app from config: {str(e)}")
            args.live_app = False
    
    return args

def upload_output(data: dict, upload_url: str) -> bool:
    """Upload JSON data to the specified URL using gzip compression."""
    try:
        json_data = json.dumps(data)
        headers = {
            'Content-Type': 'application/json',
            'Content-Encoding': 'gzip',
            'Accept-Encoding': 'gzip'
        }
        
        logging.debug(f"Uploading data to {upload_url} (size: {len(json_data)} bytes)")
        
        response = requests.post(
            upload_url,
            data=json_data,
            headers=headers,
            stream=True
        )
        
        response.raise_for_status()
        logging.info(f"Successfully uploaded to {upload_url}")
        return True
        
    except requests.exceptions.ConnectionError as e:
        print_error_box(
            "CONNECTION ERROR", 
            f"Could not connect to {upload_url}",
            f"Check your internet connection\nVerify the URL is correct and accessible"
        )
        logging.debug(f"Connection error details: {str(e)}")
        return False
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        print_error_box(
            f"HTTP ERROR {status_code}", 
            f"Server returned error: {e.response.text[:200]}",
            f"Check if the URL is correct\nVerify you have permission to upload to this endpoint"
        )
        logging.debug(f"HTTP error details: {str(e)}")
        return False
    except Exception as e:
        print_error_box(
            "UPLOAD ERROR", 
            f"Error uploading data: {str(e)}",
            "Try again later or use a different upload method"
        )
        logging.debug(f"Upload error details: {str(e)}")
        return False

def get_user_input(prompt, validator=None):
    """Get user input with proper interrupt handling"""
    try:
        while True:
            try:
                user_input = input(prompt).strip()
                if validator and not validator(user_input):
                    continue
                return user_input
            except KeyboardInterrupt:
                print("\n🛑 Analysis interrupted by user.")
                sys.exit(0)
    except KeyboardInterrupt:
        print("\n🛑 Analysis interrupted by user.")
        sys.exit(0)

def save_local_output(data: dict, app_id: str, output_dir: str = "spark_analysis_output") -> bool:
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"spark_analysis_{app_id}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Analysis data saved locally: {os.path.abspath(filepath)}")
        logging.info(f"Successfully saved analysis data to {filepath}")
        return True
        
    except Exception as e:
        print_error_box(
            "LOCAL SAVE ERROR",
            f"Failed to save analysis data locally: {str(e)}",
            "Check write permissions for the output directory\nEnsure sufficient disk space is available"
        )
        logging.debug(f"Local save error details: {str(e)}")
        return False

def process_app_id(app_id, applications, client, spark_stage_analyzer, s3_uploader, args, s3_upload_enabled, processed_app_ids, successful_upload_app_ids, failed_upload_app_ids, summary_app_ids, app_index=0, app_count=1):
    print(f"\n🔄 Processing application {app_id} ({app_index + 1}/{app_count})...")
    application_name = next((app['name'] for app in applications if app['id'] == app_id), None)
    if application_name:
        print(f"📝 Application name: {application_name}")
        
    application_start_time_ms = None
    application_end_time_ms = None
    application = next((app for app in applications if app['id'] == app_id), None)
    if not application.get('attempts'):
        raise ValueError(f"No attempts found in application {application.get('id', 'unknown')}")
    attempt = application['attempts'][0]
    application_start_time_ms = attempt.get('startTimeEpoch')
    application_end_time_ms = attempt.get('endTimeEpoch')
    logging.debug(f"Application {app_id} start time: {application_start_time_ms}, end time: {application_end_time_ms}")
    
    if len(application.get('attempts', [])) > 1:
        latest_attempt_id = client._get_latest_attempt_id(app_id)
        if latest_attempt_id:
            if args and args.debug:
                print(f"📊 Application has {len(application['attempts'])} attempts - using latest attempt ID: {latest_attempt_id}")
            logging.info(f"Application {app_id} has {len(application['attempts'])} attempts, using latest: {latest_attempt_id}")
        else:
            if args and args.debug:
                print(f"📊 Application has {len(application['attempts'])} attempts - using base application ID")
            logging.info(f"Application {app_id} has {len(application['attempts'])} attempts, using base app ID")
    elif len(application.get('attempts', [])) == 1:
        attempt_id = str(application['attempts'][0].get('attemptId', 0))
        if attempt_id != "0":
            if args and args.debug:
                print(f"📊 Application has attempt ID: {attempt_id}")
            logging.info(f"Application {app_id} has single attempt with ID: {attempt_id}")
    
    try:
        print("🔄 Fetching stages...")
        stages = client.get_stages(app_id)
        print(f"📋 Found {len(stages)} stages")
        if len(stages) == 0:
            print_error_box(
                "NO STAGES FOUND",
                f"Application {app_id} has no stages to analyze.",
                "This could be because:\n" +
                "1. The application is still running\n" +
                "2. The application hasn't started any stages yet\n" +
                "3. The application has completed but no stages were recorded\n\n" +
                "Please try analyzing a different application."
            )
            return 'zero_stages'
        if app_id not in summary_app_ids:
            summary_app_ids.append(app_id)
    except Exception as e:
        print_error_box(
            "STAGE FETCH ERROR",
            f"Failed to fetch stages for application {app_id}",
            "This application might be incomplete, still running, or there was a connection issue.\nTry analyzing a different application or check your network/server."
        )
        logging.debug(f"Stage fetch error details: {str(e)}")
        return 'connection_error'

    print("🔄 Fetching executor metrics...")
    try:
        executor_metrics = client.get_all_executor_metrics(app_id)
        print(f"📋 Found {len(executor_metrics)} executors (including historical)")
    except Exception as e:
        print_error_box(
            "EXECUTOR METRICS ERROR",
            f"Failed to fetch executor metrics for application {app_id}",
            "Proceeding with limited executor information\nSome executor details may be missing in the analysis"
        )
        logging.debug(f"Executor metrics error details: {str(e)}")
        executor_metrics = []

    total_executors = len([e for e in executor_metrics if e["id"] != "driver"])
    total_cores = sum(e.get("totalCores", 0) for e in executor_metrics if e["id"] != "driver")
    presigned_urls = None
    batch_filenames = []
    proceed_with_processing = True

    if s3_upload_enabled and len(stages) > 0 and not os.environ.get('SPARK_ANALYZER_SAVE_LOCAL_MODE') == '1':
        batch_size = 1000
        total_batches = (len(stages) + batch_size - 1) // batch_size
        print(f"🔄 Preparing {total_batches} batches for S3 upload (up to {batch_size} stages each)...")
        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(stages))
            batch_range = f"{start_idx}-{end_idx-1}"
            batch_filename = f"stages_{app_id}_batch{batch_range}.json"
            batch_filenames.append(batch_filename)

        print(f"🔄 Requesting pre-signed URLs for {len(batch_filenames)} batches upfront...")
        try:
            presigned_urls = s3_uploader.get_presigned_urls(app_id, batch_filenames)
        except Exception as e:
            presigned_urls = None
            if args.debug:
                logging.debug(f"Pre-signed URL error details: {str(e)}")

        if not presigned_urls or len(presigned_urls) != len(batch_filenames):
            print_error_box(
                "UPLOAD PREPARATION ERROR",
                f"Unable to prepare analysis upload for application {app_id}",
                "Verify your cost estimator user ID is correct\nContact Onehouse support if the problem persists\nRun with --debug for more details"
            )
            if args.debug:
                logging.error(f"Failed to get pre-signed URLs: got {len(presigned_urls) if presigned_urls else 0}, expected {len(batch_filenames)}")
            print(f"The analysis could not be uploaded for application {app_id}. Please re-run the tool or contact Onehouse support if the issue persists.")
            proceed_with_processing = False
            failed_upload_app_ids.append(app_id)
        else:
            successful_upload_app_ids.append(app_id)

    if not proceed_with_processing:
        return 'upload_error'

    print("🔄 Analyzing stages and generating output...")
    proto_output = {
        "application_id": app_id,
        "total_executors": total_executors,
        "total_cores": total_cores,
        "application_start_time_ms": application_start_time_ms or 0,
        "application_end_time_ms": application_end_time_ms or 0,
        "executors": [
            {
                "executor_id": e["id"],
                "is_active": e.get("isActive", False),
                "total_cores": e.get("totalCores", 0),
                "add_time": e.get("addTime", ""),
                "remove_time": e.get("removeTime", "")
            }
            for e in executor_metrics
            if e["id"] != "driver"
        ],
        "stages": []  
    }

    if args.live_app:
        stages_sorted = sorted(stages, key=lambda x: int(x.get('stageId', 0)), reverse=True)
        print(f"🔄 Processing {len(stages_sorted)} stages in reverse order...")
        
        BATCH_SIZE = min(args.batch_size, 50)  
        print(f"🔄 Using batch size {BATCH_SIZE} for live app processing...")
    else:
        stages_sorted = sorted(stages, key=lambda x: int(x.get('stageId', 0)))
        print(f"🔄 Processing {len(stages_sorted)} stages in normal order (completed app)...")
        
        BATCH_SIZE = max(args.batch_size, 100)  
        print(f"🔄 Using batch size {BATCH_SIZE} for completed app processing...")
    
    total_batches = (len(stages_sorted) + BATCH_SIZE - 1) // BATCH_SIZE
    
    failed_stages = 0
    skipped_stages = 0
    
    with tqdm.tqdm(total=len(stages_sorted), desc="Processing stages", unit="stage", dynamic_ncols=True, leave=True) as pbar:
        for batch_idx in range(total_batches):
            start_idx = batch_idx * BATCH_SIZE
            end_idx = min(start_idx + BATCH_SIZE, len(stages_sorted))
            batch_stages = stages_sorted[start_idx:end_idx]
            
            for stage in batch_stages:
                try:
                    stage_id = stage.get('stageId')
                    if stage_id is None:
                        logging.debug("Found stage with missing stageId, skipping")
                        skipped_stages += 1
                        pbar.update(1)
                        continue
                    
                    if args.live_app:
                        stage_exists = client.check_stage_exists(app_id, stage_id)
                        if not stage_exists:
                            logging.info(f"Stage {stage_id} not found (likely removed), skipping")
                            skipped_stages += 1
                            pbar.update(1)
                            continue
                        else:
                            logging.debug(f"Stage {stage_id} validation passed")
                    
                    stage_data = spark_stage_analyzer.format_stage_for_proto(stage, app_id, executor_metrics)
                    if stage_data:
                        proto_output["stages"].append(stage_data)
                    else:
                        failed_stages += 1
                        logging.debug(f"Stage {stage_id} processing returned None")
                        
                except ValueError as e:
                    failed_stages += 1
                    stage_id = stage.get('stageId', 'unknown')
                    error_msg = str(e)
                    
                    if "Databricks API returned non-JSON response" in error_msg:
                        logging.warning(f"Stage {stage_id}: Databricks API issue - {error_msg}")
                        if args.debug:
                            logging.debug(f"Stage {stage_id} failed due to Databricks API response issue. This may indicate session timeout or rate limiting.")
                    elif "Server returned non-JSON response" in error_msg:
                        logging.warning(f"Stage {stage_id}: Server returned non-JSON response - {error_msg}")
                        if args.debug:
                            logging.debug(f"Stage {stage_id} failed due to server returning non-JSON response.")
                    else:
                        logging.warning(f"Stage {stage_id}: API error - {error_msg}")
                        if args.debug:
                            logging.debug(f"Stage {stage_id} failed due to API error: {error_msg}")
                    
                    pbar.update(1)
                    continue
                        
                except Exception as e:
                    failed_stages += 1
                    stage_id = stage.get('stageId', 'unknown')
                    logging.warning(f"Stage {stage_id}: Unexpected error - {str(e)}")
                    if args.debug:
                        logging.debug(f"Stage {stage_id} failed due to unexpected error: {str(e)}")
                        import traceback
                        logging.debug(f"Exception traceback: {traceback.format_exc()}")
                
                pbar.update(1)
            
            if args.live_app and batch_idx < total_batches - 1:
                time.sleep(1)

    if failed_stages > 0:
        print(f"⚠️  {failed_stages} stages encountered errors and were skipped")
        logging.info(f"Failed stages for application {app_id}: {failed_stages} out of {len(stages)}")
    
    if skipped_stages > 0 and args.live_app:
        print(f"⚠️  {skipped_stages} stages were skipped (likely removed during live app processing)")
        logging.info(f"Skipped stages for live application {app_id}: {skipped_stages} out of {len(stages)}")
    elif skipped_stages > 0:
        print(f"⚠️  {skipped_stages} stages were skipped due to processing errors")
        logging.info(f"Skipped stages for application {app_id}: {skipped_stages} out of {len(stages)}")

    if os.environ.get('SPARK_ANALYZER_SAVE_LOCAL_MODE') == '1':
        success = save_local_output(proto_output, app_id)
        if success:
            successful_upload_app_ids.append(app_id)
        else:
            failed_upload_app_ids.append(app_id)
    elif s3_upload_enabled and presigned_urls and len(presigned_urls) == len(batch_filenames):
        for presigned_url in presigned_urls:
            json_data = json.dumps(proto_output)
            success = s3_uploader.upload_json_data(presigned_url, json_data)
            if not success:
                logging.error(f"Failed to upload {batch_filename} to S3")

        success = s3_uploader.signal_application_completion(app_id, batch_filenames)
        if not success:
            print(f"\n❌ Error: Failed to signal completion for application {app_id}. Upload may be incomplete.")
            logging.error(f"Failed to signal completion for application {app_id}")
        else:
            print(f"\n✅ Signaled completion for application {app_id}!")

    print(f"\n✅ Stage analysis complete for {app_id}!")
    processed_app_ids.append(app_id)
    
    if args and args.browser:
        clear_cookie_files(args)
    
    return 'success'

def run_analysis():
    """Main analysis function that orchestrates the entire process."""
    args = parse_arguments()
    logger = setup_logging(args.verbose, args.debug)
    
    try:
        print("🚀 Spark History Server Analyzer")
        print("===============================")
        
        print("⚙️  Initializing components...")
        
        if args.server_url:
            client = APIClient(base_url=args.server_url, args=args)
            print(f"ℹ️  Using custom server URL: {args.server_url}")
        else:
            client = APIClient(args=args)
        
        spark_stage_analyzer = SparkStageAnalyzer(client)
        
        use_staging = args.env == 'staging'
        s3_uploader = S3Uploader(config_file="config.ini", use_staging=use_staging, args=args)
        
        if os.environ.get('SPARK_ANALYZER_SAVE_LOCAL_MODE') == '1':
            s3_upload_enabled = False
            print("💾 Running in local save mode - analysis data will be saved locally")
            client = APIClient(args=args)
        else:
            s3_upload_enabled = s3_uploader.is_upload_enabled()
            
            # Check if --opt-out is used without proper configuration
            if args.opt_out and not args.cost_estimator_id:
                print_error_box(
                    "CONFIGURATION REQUIRED",
                    "To use --opt-out, please run the configuration wizard first.",
                    "Run: spark-analyzer-configure --opt-out name,description,details\n\n" +
                    "This will guide you through the setup process with privacy protection enabled."
                )
                sys.exit(1)
            
            if not s3_upload_enabled:
                current_env = "staging" if s3_uploader.is_staging_mode() else "production"
                staging_requested = s3_uploader.was_staging_explicitly_requested()
                
                if staging_requested:
                    print_error_box(
                        "CONFIGURATION ERROR",
                        "Environment requested but not properly configured.",
                        "Make sure all required environment variables are set:\n" +
                        "- SPARK_ANALYZER_STAGING_API_URL\n" +
                        "- SPARK_ANALYZER_STAGING_API_KEY\n" + 
                        "- SPARK_ANALYZER_STAGING_API_SECRET\n" + 
                        "- SPARK_ANALYZER_STAGING_ORG_ID\n" + 
                        "- SPARK_ANALYZER_STAGING_USER_ID\n" + 
                        "- SPARK_ANALYZER_STAGING_COST_ESTIMATOR_USER_ID"
                    )
                else:
                    config_path = s3_uploader.get_config_file_path() or "~/.spark_analyzer/configs/config.ini"
                    print_error_box(
                        "CONFIGURATION ERROR",
                        "Cost estimator user ID not configured.",
                        f"Add the following to {config_path}:\n\n" +
                        "[cost_estimator]\n" +
                        "user_id = YOUR_USER_ID_HERE\n\n" +
                        "Or run with the --cost-estimator-id option:\n" +
                        "spark-analyzer --cost-estimator-id YOUR_USER_ID_HERE\n\n" +
                        "You should have received this ID when you signed up"
                    )
                sys.exit(1)

        opt_out_fields = set()
        if args.opt_out:
            opt_out_fields = set(args.opt_out.split(","))
            spark_stage_analyzer.set_opt_out_fields(opt_out_fields)
            logging.info(f"Using opt-out fields: {opt_out_fields}")

        app_ids = []
        applications = None
        
        if args.app_id:
            app_ids = [args.app_id]
            logging.info(f"Using provided application ID: {args.app_id}")
        else:
            is_databricks = (
                ("databricks.com" in client.base_url and "sparkui" in client.base_url) or
                ("azuredatabricks.net" in client.base_url and "sparkui" in client.base_url) or
                (hasattr(client, 'original_url') and "databricks.com" in client.original_url and "sparkui" in client.original_url) or
                (hasattr(client, 'original_url') and "azuredatabricks.net" in client.original_url and "sparkui" in client.original_url)
            )
            
            if is_databricks:
                print(f"🔍 Detected Databricks URL - fetching application data...")
                logging.info("Detected Databricks URL, fetching application data")
                
                try:
                    logging.debug("Fetching applications data for Databricks")
                    applications = client.get_applications()
                    logging.debug(f"Fetched {len(applications) if applications else 0} applications for Databricks")
                    
                    if applications and len(applications) > 0:
                        app_id = applications[0]['id']
                        app_ids = [app_id]
                        print(f"✅ Found application: {app_id}")
                        
                        # Check if this application has multiple attempts
                        if len(applications[0].get('attempts', [])) > 1:
                            latest_attempt_id = client._get_latest_attempt_id(app_id)
                            if latest_attempt_id:
                                if args and args.debug:
                                    print(f"📊 Application has {len(applications[0]['attempts'])} attempts - using latest attempt ID: {latest_attempt_id}")
                            else:
                                if args and args.debug:
                                    print(f"📊 Application has {len(applications[0]['attempts'])} attempts - using base application ID")
                        elif len(applications[0].get('attempts', [])) == 1:
                            # Check if single attempt has non-zero attempt ID
                            attempt_id = str(applications[0]['attempts'][0].get('attemptId', 0))
                            if attempt_id != "0":
                                if args and args.debug:
                                    print(f"📊 Application has attempt ID: {attempt_id}")
                                logging.info(f"Application {app_id} has single attempt with ID: {attempt_id}")
                        
                        logging.info(f"Using application ID: {app_id}")
                    else:
                        print_error_box(
                            "DATABRICKS APPLICATION NOT FOUND",
                            "No applications found in Databricks.",
                            "The application might have been deleted or the URL might be incorrect.\n" +
                            "Please check the Databricks URL."
                        )
                        sys.exit(1)
                            
                except Exception as e:
                    user_url = client.original_url if hasattr(client, 'original_url') else "unknown"
                    logging.warning(f"Failed to fetch applications data for Databricks URL: {str(e)}")
                    print_error_box(
                        "DATABRICKS API ERROR",
                        f"Failed to fetch applications from: {user_url}",
                        "1. Please check your Databricks cookies and try again\n"
                        "2. Make sure you're logged into Databricks in your browser\n"
                        "3. Verify the Databricks URL is correct"
                    )
                    sys.exit(1)
            else:
                try:
                    print("🔄 Fetching available applications...")
                    max_app_fetch_retries = 1
                    fetch_attempt = 0
                    
                    print("⏳ Connecting to Spark History Server...")
                    
                    while fetch_attempt < max_app_fetch_retries:
                        try:
                            applications = client.get_applications()
                            break
                        except requests.exceptions.ConnectionError as e:
                            fetch_attempt += 1
                            if fetch_attempt < max_app_fetch_retries:
                                retry_delay = 2 ** fetch_attempt
                                logging.debug(f"Connection error - retrying in {retry_delay}s (attempt {fetch_attempt}/{max_app_fetch_retries})")
                                if fetch_attempt == 1:
                                    print("⚠️  Connection to server failed, retrying...")
                                time.sleep(retry_delay)
                            else:
                                raise
                        except requests.exceptions.Timeout as e:
                            fetch_attempt += 1
                            if fetch_attempt < max_app_fetch_retries:
                                retry_delay = 2 ** fetch_attempt
                                logging.debug(f"Timeout error - retrying in {retry_delay}s (attempt {fetch_attempt}/{max_app_fetch_retries})")
                                if fetch_attempt == 1:
                                    print("⚠️  Server response timed out, retrying...")
                                time.sleep(retry_delay)
                            else:
                                raise

                    if not applications:
                        print_error_box(
                            "NO APPLICATIONS FOUND",
                            "No applications were found in the Spark History Server",
                            "Check if the Spark History Server has any applications\n"
                            "Verify your connection settings\n"
                            "Make sure Spark History Server is running and accessible\n"
                            "If using browser mode, verify your cookies are valid\n"
                            "If using Databricks mode, verify your Databricks cookies are valid"
                        )
                        sys.exit(1)

                    if len(applications) == 0:
                        print("⚠️  The Spark History Server contains no applications.")
                        print("   You need to specify an application ID manually.")
                        while True:
                            app_to_analyze = get_user_input("\n🔍 Enter the application id(s) to analyze, separated by commas without spaces (required): ")
                            if not app_to_analyze:
                                print("\n❌ Error: Application ID is required.")
                                print("Please enter at least one application ID to proceed.")
                                continue
                            app_ids = [aid.strip() for aid in app_to_analyze.split(',') if aid.strip()]
                            if not app_ids:
                                print("\n❌ Error: No valid application IDs provided.")
                                print("Please enter at least one application ID to proceed.")
                                continue
                            break
                    else:
                        print(f"📋 Found {len(applications)} applications")
                        valid_app_ids = {app['id'] for app in applications}
                        
                        app_table = []
                        for app in applications:
                            app_id = app.get('id', 'N/A')
                            app_name = app.get('name', 'N/A')
                            attempts_count = len(app.get('attempts', []))
                            
                            # Add attempt information to the display (debug mode only)
                            if args and args.debug:
                                if attempts_count > 1:
                                    latest_attempt_id = client._get_latest_attempt_id(app_id)
                                    if latest_attempt_id:
                                        app_display = f"{app_id} (latest attempt: {latest_attempt_id})"
                                    else:
                                        app_display = f"{app_id} ({attempts_count} attempts)"
                                elif attempts_count == 1:
                                    # Check if single attempt has non-zero attempt ID
                                    attempt_id = str(app['attempts'][0].get('attemptId', 0))
                                    if attempt_id != "0":
                                        app_display = f"{app_id} (attempt: {attempt_id})"
                                    else:
                                        app_display = app_id
                                else:
                                    app_display = app_id
                            else:
                                app_display = app_id
                            
                            app_table.append([app_display, app_name])
                        
                        headers = ["Application ID", "Application Name"]
                        print("\nAvailable Applications:")
                        print(tabulate.tabulate(app_table, headers=headers, tablefmt="grid"))
                        
                        # Show a note about multiple attempts if any exist
                        multi_attempt_apps = [app for app in applications if len(app.get('attempts', [])) > 1]
                        if multi_attempt_apps and args and args.debug:
                            print("\n💡 Note: Applications with multiple attempts will automatically use the latest attempt.")
                        
                        while True:
                            app_to_analyze = get_user_input("\n🔍 Enter the application id(s) to analyze, separated by commas without spaces (required): ")
                            if not app_to_analyze:
                                print("\n❌ Error: Application ID is required.")
                                print("Please enter at least one application ID from the list above.")
                                continue
                            
                            entered_app_ids = [aid.strip() for aid in app_to_analyze.split(',') if aid.strip()]
                            if not entered_app_ids:
                                print("\n❌ Error: No valid application IDs provided.")
                                print("Please enter at least one application ID from the list above.")
                                continue
                            
                            # Handle cases where user might have entered the full display string
                            clean_app_ids = []
                            for aid in entered_app_ids:
                                # Extract just the app ID part if user entered the full display string
                                if " (latest attempt:" in aid:
                                    clean_aid = aid.split(" (latest attempt:")[0]
                                elif " (" in aid and " attempts)" in aid:
                                    clean_aid = aid.split(" (")[0]
                                else:
                                    clean_aid = aid
                                clean_app_ids.append(clean_aid)
                            
                            invalid_ids = [aid for aid in clean_app_ids if aid not in valid_app_ids]
                            if invalid_ids:
                                print(f"\n❌ Invalid application ID(s): {', '.join(invalid_ids)}")
                                print("Please enter only valid application IDs from the list above.")
                                continue
                            
                            app_ids = clean_app_ids
                            break

                except requests.exceptions.ConnectionError as e:
                    user_url = client.original_url if hasattr(client, 'original_url') else "unknown"
                    print_error_box(
                        "CONNECTION ERROR",
                        f"Failed to connect to the Spark History Server at: {user_url}",
                        "1. Check that the server is running and accessible\n"
                        "2. Verify your network connection and any VPN settings\n"
                        "3. Confirm the server URL in your configuration file\n"
                        "4. Fix the connection issue before proceeding"
                    )
                    
                    logging.debug(f"Connection error details: {str(e)}")
                    sys.exit(1)

                except requests.exceptions.Timeout as e:
                    user_url = client.original_url if hasattr(client, 'original_url') else "unknown"
                    print_error_box(
                        "CONNECTION TIMEOUT",
                        f"The request to the Spark History Server timed out: {user_url}",
                        "1. The server might be slow or processing a large amount of data\n"
                        "2. Try again later or with a longer timeout setting\n"
                        "3. Consider using port forwarding with SSH if connecting to a remote server\n"
                        "4. Fix the connection issue before proceeding"
                    )
                    
                    logging.debug(f"Timeout error details: {str(e)}")
                    sys.exit(1)

                except Exception as e:
                    # Get the original URL that the user provided
                    user_url = client.original_url if hasattr(client, 'original_url') else "unknown"
                    
                    print_error_box(
                        "APPLICATION FETCH ERROR",
                        f"Failed to fetch Spark applications",
                        "1. Check your connection settings and History Server URL\n"
                        "2. Verify the server is running and accessible\n"
                        "3. Run with --debug flag for more detailed error information\n"
                        "4. Fix the connection issue before proceeding"
                    )
                    
                    logging.debug(f"Application fetch error details: {str(e)}")
                    sys.exit(1)

        if app_ids and len(app_ids) > 0:
            skipped_zero_stage_apps = []
            processed_app_ids = []
            summary_app_ids = []
            successful_upload_app_ids = []
            failed_upload_app_ids = []

            for app_index, app_id in enumerate(app_ids):
                if app_index > 0:
                    import time
                    print("⏳ Waiting 2 seconds before processing next application...")
                    time.sleep(2)
                
                while True:
                    result = process_app_id(app_id, applications, client, spark_stage_analyzer, s3_uploader, args, s3_upload_enabled, processed_app_ids, successful_upload_app_ids, failed_upload_app_ids, summary_app_ids, app_index, len(app_ids))
                    if result == 'success':
                        break
                    if result == 'zero_stages':
                        while True:
                            retry = get_user_input("\nWould you like to try another application ID? (y/n): ")
                            if retry.lower().strip() in ['y', 'yes']:
                                break
                            elif retry.lower().strip() in ['n', 'no']:
                                sys.exit(0)
                            else:
                                print("\n❌ Error: Please enter 'y' for yes or 'n' for no.")
                        while True:
                            new_app_id = get_user_input("\n🔍 Enter another application ID to analyze (required): ")
                            if not new_app_id.strip():
                                print("\n❌ Error: Application ID is required.")
                                continue
                            if not any(app['id'] == new_app_id.strip() for app in applications):
                                print(f"\n❌ Error: Application {new_app_id} not found in the list of available applications.")
                                continue
                            app_id = new_app_id.strip()
                            new_result = process_app_id(new_app_id.strip(), applications, client, spark_stage_analyzer, s3_uploader, args, s3_upload_enabled, processed_app_ids, successful_upload_app_ids, failed_upload_app_ids, summary_app_ids, app_index, len(app_ids))
                            if new_result == 'zero_stages':
                                continue
                            break
                        if new_result == 'success' or new_result == 'upload_error':
                            break
                        continue
                    elif result == 'connection_error':
                        while True:
                            retry = get_user_input("\nConnection error occurred. Would you like to try another application ID? (y/n): ")
                            if retry.lower().strip() in ['y', 'yes']:
                                break
                            elif retry.lower().strip() in ['n', 'no']:
                                sys.exit(0)
                            else:
                                print("\n❌ Error: Please enter 'y' for yes or 'n' for no.")
                        while True:
                            new_app_id = get_user_input("\n🔍 Enter another application ID to analyze (required): ")
                            if not new_app_id.strip():
                                print("\n❌ Error: Application ID is required.")
                                continue
                            if not any(app['id'] == new_app_id.strip() for app in applications):
                                print(f"\n❌ Error: Application {new_app_id} not found in the list of available applications.")
                                continue
                            app_id = new_app_id.strip()
                            break
                        continue
                    else:
                        break

            if skipped_zero_stage_apps:
                print("\nThe following application IDs had 0 stages and were skipped:")
                for skipped_id in skipped_zero_stage_apps:
                    print(f"  - {skipped_id}")
                print("")
                while True:
                    overall_retry = get_user_input("Would you like to re-enter a different application ID for any of the skipped apps? (y/n): ")
                    if overall_retry.lower().strip() in ['n', 'no']:
                        break
                    elif overall_retry.lower().strip() in ['y', 'yes']:
                        for skipped_id in skipped_zero_stage_apps:
                            while True:
                                retry = get_user_input(f"Would you like to re-enter a different application ID for {skipped_id}? (y/n): ")
                                if retry.lower().strip() in ['y', 'yes']:
                                    while True:
                                        new_app_id = get_user_input("\n🔍 Enter a replacement application ID to analyze (required): ")
                                        if not new_app_id.strip():
                                            print("\n❌ Error: Application ID is required.")
                                            continue
                                        if not any(app['id'] == new_app_id.strip() for app in applications):
                                            print(f"\n❌ Error: Application {new_app_id} not found in the list of available applications.")
                                            continue
                                        if new_app_id.strip() in processed_app_ids:
                                            print(f"\n❌ Error: Application {new_app_id} has already been processed.")
                                            continue
                                        print(f"\n🔄 Processing replacement application {new_app_id.strip()}...")
                                        result = process_app_id(new_app_id.strip(), applications, client, spark_stage_analyzer, s3_uploader, args, s3_upload_enabled, processed_app_ids, successful_upload_app_ids, failed_upload_app_ids, summary_app_ids, 0, 1)
                                        if result == 'zero_stages' or result == 'connection_error':
                                            continue
                                        break
                                    break
                                elif retry.lower().strip() in ['n', 'no']:
                                    break
                                else:
                                    print("\n❌ Error: Please enter 'y' for yes or 'n' for no.")
                        break
                    else:
                        print("\n❌ Error: Please enter 'y' for yes or 'n' for no.")

            # Skip S3 completion signaling if in save-local mode
            if s3_upload_enabled and successful_upload_app_ids and not os.environ.get('SPARK_ANALYZER_SAVE_LOCAL_MODE') == '1':
                print("🔄 Finalizing upload process...")
                try:
                    if s3_uploader.signal_all_jobs_completion(successful_upload_app_ids):
                        print("✅ Upload finalized successfully")
                        print("\n📬 Onehouse has received and is now processing your Spark job metadata.")
                        print("📊 You will receive your custom report of Spark optimization opportunities shortly.")
                    else:
                        print("ℹ️  Upload partially complete - your data was saved but processing may be delayed")
                except Exception as e:
                    print("ℹ️  Upload partially complete - your data was saved but processing may be delayed")
                    if args.debug:
                        logging.debug(f"Completion signal error details: {str(e)}")
            
            print("\n" + "─" * 50)
            print("📋 PROCESS SUMMARY")
            print("─" * 50)
            
            print("✅ Analysis: Complete - Successfully analyzed the following Spark application(s):")
            for app_id in summary_app_ids:
                print(f"   - {app_id}")
            print("")
            if os.environ.get('SPARK_ANALYZER_SAVE_LOCAL_MODE') == '1':
                if successful_upload_app_ids:
                    print(f"💾 Local Save: Data was successfully saved locally for {len(successful_upload_app_ids)} application(s):")
                    for app_id in successful_upload_app_ids:
                        print(f"   - {app_id}")
                    print("")
                if failed_upload_app_ids:
                    print(f"❌ Local Save: Data could NOT be saved locally for {len(failed_upload_app_ids)} application(s):")
                    for app_id in failed_upload_app_ids:
                        print(f"   - {app_id} (see error above)")
                    print("")
                if not failed_upload_app_ids:
                    print("✅ All data saved locally successfully.")
            elif s3_upload_enabled or args.upload_url:
                if successful_upload_app_ids:
                    print(f"✅ Upload: Data was successfully uploaded for {len(successful_upload_app_ids)} application(s):")
                    for app_id in successful_upload_app_ids:
                        print(f"   - {app_id}")
                    print("")
                if failed_upload_app_ids:
                    print(f"❌ Upload: Data could NOT be uploaded for {len(failed_upload_app_ids)} application(s):")
                    for app_id in failed_upload_app_ids:
                        print(f"   - {app_id} (see error above)")
                    print("")
                if not failed_upload_app_ids:
                    print("✅ All uploads completed successfully.")
            else:
                print("ℹ️ Upload: Not configured - No upload destinations were specified")
            print("─" * 50)
        else:
            print("\n❌ No applications selected for analysis. Exiting.")
            
    except KeyboardInterrupt:
        print("\n🛑 Analysis interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print_error_box(
            "UNEXPECTED ERROR",
            f"An unexpected error occurred: {str(e)}",
            "Try running with --debug flag for more detailed information\nCheck your configuration and try again"
        )
        if args.debug:
            import traceback
            traceback.print_exc()
        logging.debug(f"Unexpected error details: {str(e)}")
        sys.exit(1)

def show_readme():
    """Display the README documentation."""
    try:
        try:
            from importlib.resources import files
            readme_file = files('spark_analyzer').joinpath('README.md')
            readme_content = readme_file.read_text(encoding='utf-8')
        except ImportError:
            import pkg_resources
            readme_content = pkg_resources.resource_string('spark_analyzer', 'README.md').decode('utf-8')
        
        print(readme_content)
    except Exception as e:
        print_error_box(
            "README ERROR",
            f"Failed to display README: {str(e)}",
            "The README file could not be found or read.\n"
            "You can view the documentation online at:\n"
            "https://pypi.org/project/spark-analyzer/"
        )
        sys.exit(1)

def main():
    args = parse_arguments()
    if args.show_readme:
        show_readme()
        sys.exit(0)
    run_analysis()

def clear_cookie_files(args):
    """Clear cookie files after analysis to ensure fresh cookies for next run."""
    if not args or not args.browser:
        return
    
    # Determine which cookie files to clear based on the environment
    cookie_files_to_clear = []
    
    # Add environment-specific cookie files
    if hasattr(args, 'env') and args.env:
        env_suffix = f"_{args.env}" if args.env != "production" else ""
        cookie_files_to_clear.extend([
            f"configs/databricks_cookies{env_suffix}.txt",
            f"configs/raw_cookies{env_suffix}.txt"
        ])
    
    # Add default cookie files
    cookie_files_to_clear.extend([
        "configs/databricks_cookies.txt",
        "configs/raw_cookies.txt"
    ])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_cookie_files = []
    for cookie_file in cookie_files_to_clear:
        if cookie_file not in seen:
            seen.add(cookie_file)
            unique_cookie_files.append(cookie_file)
    
    cleared_files = []
    for cookie_file in unique_cookie_files:
        if os.path.exists(cookie_file):
            try:
                with open(cookie_file, 'w') as f:
                    f.write('')
                cleared_files.append(cookie_file)
                logging.debug(f"Cleared cookie file: {cookie_file}")
            except Exception as e:
                logging.debug(f"Could not clear cookie file {cookie_file}: {str(e)}")
    
    if cleared_files:
        print(f"\n🧹 Cleared {len(cleared_files)} cookie file(s) for fresh authentication on next run")
        logging.info(f"Cleared cookie files: {cleared_files}")

if __name__ == "__main__":
    main() 