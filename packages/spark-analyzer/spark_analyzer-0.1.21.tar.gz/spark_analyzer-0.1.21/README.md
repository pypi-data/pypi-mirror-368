# Spark Analyzer

A tool for analyzing Spark History Server data to identify optimization opportunities by classifying stages by workflow type and storage format.

[Sign up for your Unique Cost Estimator ID](https://www.onehouse.ai/spark-analysis-tool) to get started. After analysis upload, you'll receive a confirmation that "Onehouse has received and is now processing your Spark job metadata. You will receive your custom report of Spark optimization opportunities shortly."

## What the Analyzer Does

- **E, T, L Detection**: Automatically detects and categorizes Extract, Transform, and Load operations in your Spark jobs.
- **Stage-Level Metrics**: Deep insights into each stage of your Spark pipeline, with detailed performance metrics.
- **Rapid Analysis**: Receive a comprehensive analysis directly in your inbox.
- **End-to-End Process**: After analysis, Onehouse processes your Spark job metadata and delivers a custom report of optimization opportunities to your inbox.

## Data Collection and Privacy

### What Data is Collected

The Spark Analyzer collects the following information from your Spark History Server:

#### Application-Level Data
- Application ID
- Application name
- Application start and end times
- Total number of executors and cores
- Executor metrics (CPU, memory usage, add/remove times)

#### Stage-Level Data
- Stage ID and attempt information
- **Stage names** (e.g., "show at Console.scala:14", "parquet at DataFrameWriter.scala:401")
- **Stage descriptions** (if available)
- **Stage details** (stack traces and execution plans)
- Task counts and executor assignments
- Performance metrics (duration, CPU time, etc.)
- Submission and completion timestamps

#### Derived Metrics
- Workflow type classification (Extract, Transform, Load)
- Storage format detection (Parquet, Delta, Hudi, Iceberg)
- Resource utilization calculations
- Performance bottleneck analysis

### Privacy Protection Options

#### 1. Data Hashing for Sensitive Fields

You can opt out of sharing potentially sensitive information by using the `--opt-out` parameter with the configuration wizard. When you opt out of a field, the actual content is replaced with a secure hash protecting your privacy:

```bash
# Hash all potentially sensitive fields
spark-analyzer-configure --opt-out name,description,details

# Hash only stage names
spark-analyzer-configure --opt-out name

# Hash only stage descriptions
spark-analyzer-configure --opt-out description
```

**Available Privacy Options:**
- `name`: Stage names are replaced with `name_hash_[numeric_hash]`
- `description`: Stage descriptions are replaced with `description_hash_[numeric_hash]` 
- `details`: Stage details (stack traces, execution plans) are replaced with `details_hash_[numeric_hash]`

**Example of Hashing:**
- **Original**: `"stage_name": "show at Console.scala:14"`
- **Hashed**: `"stage_name": "name_hash_1002607082777652347"`



### Data Usage and Retention

- **Purpose**: Analysis data is uploaded to Onehouse's secure cloud environment for cost estimation and optimization recommendations
- **Processing**: Data is processed to generate personalized optimization reports
- **Delivery**: Results are delivered to your registered email address
- **Retention**: Analysis data is retained for report generation and service improvement
- **Security**: Data is transmitted over HTTPS and stored in secure cloud infrastructure

### Data Minimization

The analyzer implements data minimization principles:

- **Selective Collection**: Only collects data necessary for performance analysis
- **Configurable Privacy**: Allows granular control over what information is shared
- **Hash Preservation**: Maintains analytical value while protecting sensitive content

### Compliance Considerations

- **Hashing Algorithm**: Uses Python's built-in `hash()` function for consistent, irreversible hashing
- **No PII Collection**: Does not intentionally collect personally identifiable information
- **Stage Content**: Stage names/descriptions may contain file paths, table names, or query fragments that could be considered sensitive in your environment
- **Privacy Logging**: Privacy options (opt-out choices) are logged to standard application logs during execution

### Recommendations for Enterprise Use

1. **Enable Privacy Options**: Use `--opt-out name,description,details` for maximum privacy protection
2. **Start Conservatively**: Begin with all privacy options enabled, then adjust based on your comfort level
3. **InfoSec Review**: Have your security team review the privacy options and hashing mechanisms
4. **Test with Sample Data**: Run initial analysis on non-sensitive test workloads
5. **Gradual Adoption**: Start with most privacy-protective settings, then adjust based on organizational requirements

## Limitations

### Databricks Support
- **Single Application Analysis**: Currently, Databricks environments only support analyzing one application at a time.
- **Future Enhancement**: Support for multiple application analysis in Databricks will be available in future releases.
- **Workaround**: For multiple applications, run the analyzer separately for each application.

## Installation

The package is available through Onehouse's private package repository and can be installed using pip. We recommend using a virtual environment:

```bash
# Create and activate a virtual environment (recommended)
python3 -m venv myenv
source myenv/bin/activate  # On Windows, use: myenv\Scripts\activate

# Install the package
pip install spark-analyzer
```

Note: If you see an "externally-managed-environment" error, it means you're trying to install directly into your system Python. Always use a virtual environment as shown above.

### Alternative: Using pipx (for System-wide Installation)

If you want to install the tool system-wide (not recommended for development), you can use `pipx`:

```bash
# Install pipx first
brew install pipx  # on macOS
pipx ensurepath    # ensure pipx is in your PATH

# Install spark-analyzer
pipx install spark-analyzer
```

Note: `pipx` creates an isolated environment for the application, which is safer than installing directly into your system Python.

## Configuration and Usage

After installation, you need to configure and run the tool using the configuration wizard:

```bash
# Basic configuration
spark-analyzer-configure

# Configuration with privacy protection
spark-analyzer-configure --opt-out name,description,details
```

This command will:
- Guide you through setting up your connection mode and other settings
- Ask if you want to run the analyzer immediately after configuration
- Run the analyzer with the appropriate settings if you choose to

The configuration wizard will help you with:
1. Setting up your Cost Estimator User ID (required for analysis upload)
2. Choosing connection mode (local or browser)
3. Configuring Spark History Server URL
4. Setting up browser cookies (if using browser mode)

### Manual Configuration

If you prefer to configure manually, you can edit the configuration files directly:

1. Create the config directory:
   ```bash
   mkdir -p ~/.spark_analyzer/configs
   ```

2. Create and edit the configuration file:
   ```bash
   # Create config.ini
   touch ~/.spark_analyzer/configs/config.ini
   ```

3. Add your configuration:
   ```ini
   [server]
   base_url = http://localhost:18080/api/v1  # or your Spark History Server URL

   [cost_estimator]
   user_id = your-unique-cost-estimator-id-here
   ```

4. For browser mode, create a cookies file:
   ```bash
   touch ~/.spark_analyzer/configs/raw_cookies.txt
   ```
   Then add your browser cookies to this file.

### Privacy Options

The Spark Analyzer provides comprehensive privacy protection options. For detailed information about data collection and privacy controls, see the **[Data Collection and Privacy](#data-collection-and-privacy)** section above.

Quick reference for privacy options:

```bash
# Hash all potentially sensitive fields
spark-analyzer-configure --opt-out name,description,details

# Hash only stage names
spark-analyzer-configure --opt-out name

# Hash only stage descriptions  
spark-analyzer-configure --opt-out description
```

### Connection Modes

The tool supports two modes of operation:

#### 1. Local Mode

Use this when you have direct access to the Spark History Server (either through port forwarding or an SSH tunnel).

1. Run the configuration wizard:
   ```bash
   # Basic local mode configuration
   spark-analyzer-configure
   
   # Local mode with privacy protection
   spark-analyzer-configure --opt-out name,description,details
   ```
   Choose "Local mode" when prompted.

2. Or manually set the base URL in `~/.spark_analyzer/configs/config.ini`:
   ```ini
   [server]
   # For historical applications with standard installation
   base_url = http://localhost:18080/api/v1
   
   # For port forwarding scenarios
   # base_url = http://localhost:8080/onehouse-spark-code/history-server/api/v1
   
   # For live applications
   # base_url = http://localhost:4040/api/v1
   ```

3. Run the tool:
   ```bash
   # For completed applications
   spark-analyzer-configure
   
   # For live/running applications
   spark-analyzer-configure --live-app
   ```

#### 2. Browser Mode

Use this when accessing Spark History Server through a browser (e.g., EMR's browser-based interface).

> **Note**: For EMR, you see both live (running spark applications) and completed applications in the same Spark History Server URL/endpoint, where the live application will be present under the incompleted applications. This tool allows you to select both completed and live applications to analyze. Make sure you choose the correct Application ID from the list.

1. Run the configuration wizard:
   ```bash
   # Basic browser mode configuration
   spark-analyzer-configure
   
   # Browser mode with privacy protection
   spark-analyzer-configure --opt-out name,description,details
   ```
   Choose "Browser mode" when prompted. The wizard will:
   - Ask for your Spark History Server URL
   - Automatically configure the base URL with the correct API endpoint
   - Guide you through setting up cookies

2. To get your browser cookies:
   - Open the Spark History Server in your browser
   - Open developer tools (F12 or right-click > Inspect)
   - Go to the Network tab and click on any request
   - Find the "Cookie" header in the Request Headers
   - Copy the entire cookie string
   - If using the wizard: Paste when prompted

3. Run the tool:
   ```bash
   # For completed applications
   spark-analyzer-configure
   
   # For live/running applications
   spark-analyzer-configure --live-app
   ```

#### Databricks URL Instructions

For Databricks environments, you need to copy the full URL from the Spark UI:

1. **Navigate to your Spark application** in Databricks
2. **Click on the Spark UI link** for your application
3. **Right-click on "Open in new tab"** and select "Copy link address"
4. **Paste the entire URL** when prompted by the configuration wizard

The URL should look like this:
```
https://your-workspace.cloud.databricks.com/sparkui/application-id/driver-id?o=workspace-id
```

**Note**: For security and to ensure fresh authentication, cookie files are automatically cleared after each analysis run. You'll need to provide fresh cookies for each new application you want to analyze.

### S3 Upload for Cost Estimation

The tool automatically uploads analysis results to Onehouse's secure cloud environment for cost estimation and optimization recommendations. Your unique Cost Estimator User ID ensures results are associated with your account.
