#!/usr/bin/env python3
import os
import sys
import logging
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich import print as rprint
from typing import Optional
import configparser
import requests
from pathlib import Path
import time
import subprocess
from typer.models import OptionInfo
from urllib.parse import urlparse, urljoin

app = typer.Typer(help="Spark Analyzer Configuration Tool")
console = Console()

def setup_logging(debug=False):
    """Setup logging configuration."""
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def print_error_box(title: str, message: str, help_text: str):
    """Print a formatted error box using rich."""
    console.print(Panel(
        f"[bold red]{title}[/bold red]\n\n{message}\n\n[bold]How to fix this:[/bold]\n{help_text}",
        title="❌ Error",
        border_style="red"
    ))

def test_history_server_url(url: str) -> bool:
    """Test connection to Spark History Server using curl, matching setup.sh behavior."""
    console.print("")
    console.print("[yellow]Testing connection to Spark History Server...[/yellow]")
    try:
        # Use curl with same flags as setup.sh, but use PIPE for stdout only
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", f"{url}/applications"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,  # equivalent to 2>/dev/null
            text=True,
            check=False  # don't raise on non-zero exit codes
        )
        
        if result.stdout.strip() == "200":
            console.print("[green]✅ Successfully connected to Spark History Server[/green]")
            return True
        else:
            print_error_box(
                "SPARK HISTORY SERVER NOT FOUND",
                f"Could not connect to Spark History Server at {url}",
                "> 1. Verify your Spark History Server URL is correct\n"
                "> 2. Check that the server is running and accessible\n"
                "> 3. Try accessing the URL in your browser\n"
                "> 4. If using a custom path, make sure it's correct\n"
                "> 5. Check your network connection and any VPN settings"
            )
            return False
    except subprocess.CalledProcessError:
        print_error_box(
            "SPARK HISTORY SERVER NOT FOUND",
            f"Could not connect to Spark History Server at {url}",
            "> 1. Verify your Spark History Server URL is correct\n"
            "> 2. Check that the server is running and accessible\n"
            "> 3. Try accessing the URL in your browser\n"
            "> 4. If using a custom path, make sure it's correct\n"
            "> 5. Check your network connection and any VPN settings"
        )
        return False
    except FileNotFoundError:
        print_error_box(
            "CURL NOT FOUND",
            "The curl command is not available on your system",
            "> 1. Install curl on your system\n"
            "> 2. For macOS: brew install curl\n"
            "> 3. For Linux: apt-get install curl or yum install curl"
        )
        return False

def parse_databricks_url(url: str) -> tuple[str, str]:
    from urllib.parse import urlparse, urljoin
    
    if '?' in url:
        url = url.split('?')[0]
    
    parsed = urlparse(url)
    
    path_components = parsed.path.split('/')
    
    filtered_components = [comp for comp in path_components if comp and comp != 'compute']
    
    truncated_components = []
    for comp in filtered_components:
        truncated_components.append(comp)
        if comp.startswith('driver-'):
            break
    
    clean_path = '/' + '/'.join(truncated_components)

    base_url = f"{parsed.scheme}://{parsed.netloc}{clean_path}"
    
    if base_url.endswith('/'):
        base_url = base_url[:-1]
    
    api_url = f"{base_url}/api/v1"
    
    return base_url, api_url

def extract_databricks_app_id(url: str) -> Optional[str]:
    from urllib.parse import urlparse
    
    if '?' in url:
        url = url.split('?')[0]
    
    parsed = urlparse(url)
    
    path_components = parsed.path.split('/')
    
    filtered_components = [comp for comp in path_components if comp and comp != 'compute']
    
    if len(filtered_components) >= 3 and filtered_components[0] == 'sparkui':
        app_id = filtered_components[1]
        if '-' in app_id and app_id.replace('-', '').replace('_', '').isalnum():
            return app_id
    
    return None

def extract_databricks_driver_id(url: str) -> Optional[str]:
    from urllib.parse import urlparse
    
    if '?' in url:
        url = url.split('?')[0]
    
    parsed = urlparse(url)
    
    path_components = parsed.path.split('/')
    
    filtered_components = [comp for comp in path_components if comp and comp != 'compute']
    
    if len(filtered_components) >= 3 and filtered_components[0] == 'sparkui':
        for comp in filtered_components:
            if comp.startswith('driver-'):
                driver_id = comp[7:]
                if driver_id.isdigit():
                    return driver_id
    
    return None

@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    config_dir: Optional[str] = typer.Option(
        None,
        "--config-dir",
        "-c",
        help="Directory to store configuration files"
    ),
    opt_out: Optional[str] = typer.Option(
        None,
        "--opt-out",
        help="Comma-separated list of fields to opt out of (name,description,details)"
    ),
    save_local: bool = typer.Option(
        False,
        "--save-local",
        help="Save analysis data locally instead of uploading to Onehouse"
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        help="Enable debug logging (DEBUG level, includes all requests/responses)"
    ),
    live_app: bool = typer.Option(
        False,
        "--live-app",
        help="Indicate this is a live/running application (enables reverse processing and stage validation to handle race conditions)"
    )
):
    # Setup logging based on debug flag
    setup_logging(debug)
    if debug:
        logging.debug("Debug logging enabled")
    """Spark Analyzer Configuration Tool."""
    if ctx.invoked_subcommand is None:
        # If no subcommand was specified, run configure with the provided arguments
        ctx.invoke(configure, config_dir=config_dir, opt_out=opt_out, save_local=save_local, debug=debug, live_app=live_app)

@app.command()
def configure(
    config_dir: Optional[str] = None,
    opt_out: Optional[str] = None,
    save_local: bool = False,
    debug: bool = False,
    live_app: bool = False
):
    """Interactive configuration for Spark Analyzer."""
    if isinstance(config_dir, OptionInfo):
        config_dir = None
    
    console.print("[bold blue]==============================================[/bold blue]")
    console.print("[bold blue]       Spark Analyzer Configuration Wizard    [/bold blue]")
    console.print("[bold blue]==============================================[/bold blue]")
    console.print("")
    
    # Determine config directory
    if config_dir is not None:
        config_dir = Path(config_dir)
    else:
        config_dir = Path("configs")  # Use local configs directory
    
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "config.ini"
    
    # Cost Estimator User ID
    console.print("[bold blue]Cost Estimator User ID:[/bold blue]")
    console.print("You should have received this ID when you signed up for the service.")
    console.print("")
    
    while True:
        cost_estimator_id = Prompt.ask(
            "\nEnter your Cost Estimator User ID",
            default=""
        )
        if not cost_estimator_id:
            console.print("[red]Error: Cost Estimator User ID is required.[/red]")
            console.print("You must provide a Cost Estimator User ID to proceed.")
            console.print("")
            continue
        break
    
    # Connection Mode
    console.print("")
    console.print("[bold blue]Connection Mode:[/bold blue]")
    console.print("1) Local mode (direct connection to Spark History Server)")
    console.print("2) Browser mode (connects through browser cookies for EMR, Databricks, or other web-based applications)")
    
    while True:
        connection_mode = Prompt.ask(
            "\nChoose connection mode",
            choices=["1", "2"],
            default="1"
        )
        if connection_mode not in ["1", "2"]:
            console.print("")
            console.print("[red]Error: Invalid option. Please choose 1 or 2[/red]")
            console.print("")
            continue
        break
    
    # History Server URL
    if connection_mode == "1":
        console.print("")
        console.print("[bold blue]Spark History Server URL:[/bold blue]")
        console.print("Enter the full URL to your Spark History Server.")
        console.print("Examples:")
        console.print("  - Standard local: http://localhost:18080")
        console.print("  - Port forwarded: http://localhost:8080/onehouse-spark-code/history-server")
        console.print("  - If '/api/v1' is part of your URL: http://localhost:8080/onehouse-spark-code/history-server/api/v1")
        console.print("  - Live application: http://localhost:4040")
        
        while True:
            history_server_url = Prompt.ask(
                "\nEnter Spark History Server URL",
                default="http://localhost:18080"
            )
            
            # If user just pressed Enter, use default
            if not history_server_url:
                console.print("")
                console.print("[yellow]Using default URL: http://localhost:18080[/yellow]")
                console.print("")
                history_server_url = "http://localhost:18080"
            
            # Validate URL format
            if not history_server_url.startswith(("http://", "https://")):
                console.print("")
                console.print("[red]Error: URL must start with http:// or https://[/red]")
                console.print("Please enter a valid URL (e.g., http://localhost:18080)")
                console.print("Or press Enter to use the default URL: http://localhost:18080")
                console.print("")
                continue
            
            # Process URL
            history_server_url = history_server_url.rstrip("/")
            if not history_server_url.endswith("/api/v1"):
                history_server_url = f"{history_server_url}/api/v1"
                console.print(f"[yellow]Note: Adding /api/v1 to the URL for API access: {history_server_url}[/yellow]")
            
            # Test connection
            if test_history_server_url(history_server_url):
                break
    elif connection_mode == "2":
        console.print("")
        console.print("[bold blue]Spark History Server URL:[/bold blue]")
        console.print("Enter the full URL to your Spark History Server or Databricks Spark UI.")
        console.print("Examples:")
        console.print("  - Standard Spark History Server: https://your-spark-history-server-url/")
        console.print("  - Port forwarded: https://your-spark-history-server-url/path-to-history-server")
        console.print("  - Databricks: Copy the entire link from 'Open in new tab' in Spark UI")
        console.print("")
        
        while True:
            history_server_url = Prompt.ask(
                "\nEnter Spark History Server or Databricks Spark UI URL"
            )
            if not history_server_url:
                console.print("")
                console.print("[red]Error: URL is required for browser mode.[/red]")
                console.print("Please enter a valid Spark History Server or Databricks Spark UI URL.")
                console.print("")
                continue
            
            # Check if it's a Databricks URL and provide specific guidance
            if "databricks.com" in history_server_url or "azuredatabricks.net" in history_server_url:
                if "sparkui" not in history_server_url:
                    console.print("")
                    console.print("[yellow]⚠️  Databricks URL detected but doesn't contain 'sparkui'[/yellow]")
                    console.print("For Databricks, you need to copy the link from the Spark UI:")
                    console.print("1. Go to your Databricks job/application")
                    console.print("2. Click on the Spark UI link")
                    console.print("3. Right-click on 'Open in new tab' and copy the link address")
                    console.print("4. The URL should contain '/sparkui/' in the path")
                    console.print("")
                    if not Confirm.ask("Do you want to continue with this URL anyway?"):
                        continue
            
            # Validate URL format
            if not history_server_url.startswith(("http://", "https://")):
                console.print("")
                console.print("[red]Error: URL must start with http:// or https://[/red]")
                console.print("Please enter a valid URL.")
                console.print("")
                continue
            
            if ("databricks.com" in history_server_url or "azuredatabricks.net" in history_server_url) and "sparkui" in history_server_url:
                try:
                    base_url, api_url = parse_databricks_url(history_server_url)
                    history_server_url = api_url
                except Exception as e:
                    console.print("")
                    console.print(f"[red]Error parsing Databricks URL: {str(e)}[/red]")
                    console.print("Please check the URL format and try again.")
                    console.print("")
                    continue
            else:
                history_server_url = history_server_url.rstrip("/")
                if not history_server_url.endswith("/api/v1"):
                    history_server_url = f"{history_server_url}/api/v1"
                    console.print(f"[yellow]Note: Adding /api/v1 to the URL for API access: {history_server_url}[/yellow]")
            
            break
    
    # Create config file
    config = configparser.ConfigParser()
    config["server"] = {"base_url": history_server_url}
    config["cost_estimator"] = {"user_id": cost_estimator_id}
    config["processing"] = {"live_app": str(live_app).lower()}
    
    with open(config_file, "w") as f:
        config.write(f)
    
    console.print(f"\n[green]✅ Configuration saved to {config_file}[/green]")
    
    # Handle browser mode cookies
    if connection_mode == "2":
        is_databricks = ("databricks.com" in history_server_url or "azuredatabricks.net" in history_server_url) and "sparkui" in history_server_url
        
        if is_databricks:
            cookies_file = config_dir / "databricks_cookies.txt"
            console.print("")
            console.print("[bold blue]Databricks Cookie Setup:[/bold blue]")
            console.print("For Databricks, you need to copy cookies from your browser.")
            console.print("")
            console.print("Steps to get Databricks cookies:")
            console.print("1. Open your Databricks workspace in your browser")
            console.print("2. Navigate to the Spark UI for your application")
            console.print("3. Open developer tools (F12 or right-click > Inspect)")
            console.print("4. Go to the Network tab and click on any request")
            console.print("5. Find the 'Cookie' header in the Request Headers")
            console.print("6. Copy the entire cookie string")
            console.print("")
            console.print("Note: Make sure you're logged into Databricks and have access to the Spark UI.")
            console.print("")
        else:
            cookies_file = config_dir / "raw_cookies.txt"
            console.print("")
            console.print("[bold blue]Browser Cookie Setup:[/bold blue]")
            console.print("For browser mode, you need to copy cookies from your browser.")
            console.print("")
            console.print("Steps to get cookies:")
            console.print("1. Open the Spark History Server in your browser")
            console.print("2. Open developer tools (F12 or right-click > Inspect)")
            console.print("3. Go to the Network tab and click on any request")
            console.print("4. Find the 'Cookie' header in the Request Headers")
            console.print("5. Copy the entire cookie string")
            console.print("")
        
        if Confirm.ask("Would you like to enter cookies now?"):
            # Create empty file if it doesn't exist
            cookies_file.touch()
            
            # Try to use vim first, fall back to nano if vim is not available
            editor = "vim"
            try:
                subprocess.run(["which", "vim"], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                editor = "nano"
                try:
                    subprocess.run(["which", "nano"], check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    console.print("[red]Error: Neither vim nor nano is available on your system.[/red]")
                    console.print("Please install one of them to edit cookies:")
                    console.print("  - For macOS: brew install vim")
                    console.print("  - For Linux: apt-get install vim or yum install vim")
                    sys.exit(1)
            
            # Open the editor
            if is_databricks:
                console.print(f"\nOpening {editor} to edit Databricks cookies...")
                console.print("Paste your Databricks cookies, save and exit the editor when done.")
            else:
                console.print(f"\nOpening {editor} to edit cookies...")
                console.print("Paste your cookies, save and exit the editor when done.")
            console.print("")
            
            try:
                subprocess.run([editor, str(cookies_file)], check=True)
                if cookies_file.stat().st_size > 0:
                    if is_databricks:
                        console.print(f"[green]✅ Databricks cookies saved to {os.path.abspath(cookies_file)}[/green]")
                    else:
                        console.print(f"[green]✅ Cookies saved to {os.path.abspath(cookies_file)}[/green]")
                else:
                    if is_databricks:
                        console.print("[yellow]⚠️  Cookie file is empty. Databricks mode authentication may fail.[/yellow]")
                    else:
                        console.print("[yellow]⚠️  Cookie file is empty. Browser mode authentication may fail.[/yellow]")
            except subprocess.CalledProcessError as e:
                console.print(f"[red]Error: Failed to open editor: {str(e)}[/red]")
                sys.exit(1)
        else:
            console.print("")
            console.print("[bold red]Configuration Incomplete[/bold red]")
            console.print("Browser mode requires cookies for authentication.")
            console.print("")
            sys.exit(1)
    
    # Setup complete
    console.print("")
    console.print("[bold green]==============================================[/bold green]")
    console.print("[bold green]       Configuration completed successfully!   [/bold green]")
    console.print("[bold green]==============================================[/bold green]")
    console.print("")
    
    # Ask if user wants to run now
    if Confirm.ask("\nWould you like to run the analyzer now?"):
        console.print("\n[blue]Running Spark Analyzer...[/blue]")
        
        original_args = os.environ.get('SPARK_ANALYZER_ORIGINAL_ARGS', '')
        original_args_str = f"{original_args} " if original_args else ""
        
        # Add opt-out flag if provided
        if opt_out:
            original_args_str = f"--opt-out {opt_out} {original_args_str}"
        
        if debug:
            original_args_str = f"--debug {original_args_str}"
        
        env = os.environ.copy()
        env['SPARK_ANALYZER_FROM_CONFIG'] = '1'
        
        # Set save-local mode via environment variable instead of command line flag
        if save_local:
            env['SPARK_ANALYZER_SAVE_LOCAL_MODE'] = '1'
        
        if connection_mode == "1":
            if history_server_url != "http://localhost:18080/api/v1":
                # Custom URL
                if cost_estimator_id:
                    subprocess.run(f"spark-analyzer {original_args_str}--server-url '{history_server_url}' --cost-estimator-id '{cost_estimator_id}'", shell=True, env=env)
                else:
                    subprocess.run(f"spark-analyzer {original_args_str}--server-url '{history_server_url}'", shell=True, env=env)
            else:
                # Default URL
                if cost_estimator_id:
                    subprocess.run(f"spark-analyzer {original_args_str}--local --cost-estimator-id '{cost_estimator_id}'", shell=True, env=env)
                else:
                    subprocess.run(f"spark-analyzer {original_args_str}--local", shell=True, env=env)
        elif connection_mode == "2":
            if cost_estimator_id:
                subprocess.run(f"spark-analyzer {original_args_str}--browser --cost-estimator-id '{cost_estimator_id}'", shell=True, env=env)
            else:
                subprocess.run(f"spark-analyzer {original_args_str}--browser", shell=True, env=env)

@app.command()
def show():
    """Show current configuration."""
    config_dir = Path("configs")  # Use local configs directory
    config_file = config_dir / "config.ini"
    
    if not config_file.exists():
        print_error_box(
            "CONFIGURATION NOT FOUND",
            f"No configuration file found at {config_file}",
            "Run 'spark-analyzer-configure configure' to set up your configuration"
        )
        sys.exit(1)
    
    config = configparser.ConfigParser()
    config.read(config_file)
    
    console.print("[bold blue]Current Configuration:[/bold blue]")
    console.print("=" * 50)
    
    for section in config.sections():
        console.print(f"\n[bold]{section}[/bold]")
        for key, value in config[section].items():
            console.print(f"  {key}: {value}")
    
    cookies_file = config_dir / "raw_cookies.txt"
    if cookies_file.exists():
        console.print("\n[bold]Browser Cookies:[/bold]")
        console.print(f"  File: {cookies_file}")
        console.print("  Status: [green]Configured[/green]")
    else:
        console.print("\n[bold]Browser Cookies:[/bold]")
        console.print("  Status: [yellow]Not configured[/yellow]")

if __name__ == "__main__":
    app() 