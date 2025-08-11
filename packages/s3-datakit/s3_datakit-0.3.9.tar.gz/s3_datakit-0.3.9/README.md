# S3 DataKit 🧰

A Python toolkit to simplify common operations between Amazon S3 and Pandas DataFrames.

## Key Features

* **List** files in an S3 bucket.
* **Upload** local files to S3.
* **Download** files from S3 directly to a local path or a Pandas DataFrame.
* Supports **CSV** and **Stata (.dta)** when reading into DataFrames.

## Installation
```bash
pip install s3-datakit
```
or
```bash
uv add s3-datakit
```

## Credential Configuration
This package uses `boto3` to interact with AWS. `boto3` will automatically search for credentials in the following order:

1.  Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, etc.).
2.  The AWS CLI credentials file (`~/.aws/credentials`).
3.  IAM roles (if running on an EC2 instance or ECS container).

For local development, the easiest method is to use a `.env` file.

**1. Install `python-dotenv` in your project (not as a library dependency):**
```bash
pip install python-dotenv
```

**2. Create a `.env` file in your project's root:**
```
AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY
AWS_DEFAULT_REGION=your-region # e.g., us-east-1
```

**3. Load the variables in your script *before* using `s3datakit`:**
```python
from dotenv import load_dotenv
import s3datakit as s3dk

# Load environment variables from .env
load_dotenv()

# Now you can use the package's functions
s3dk.list_s3_files(bucket="my-bucket")
```

## Usage

### List Files

```python
import s3datakit as s3dk

file_list = s3dk.list_s3_files(bucket="my-data-bucket")
if file_list:
    print(file_list)
```

### Upload a File

You can specify the full destination path in S3. If `s3_path` is not provided, the original filename from `local_path` is used as the S3 object key.

```python
import s3datakit as s3dk

# Upload with a specific S3 path
s3dk.upload_s3_file(
    local_path="reports/report.csv",
    bucket="my-data-bucket",
    s3_path="final-reports/report_2025.csv"
)

# Upload using the local filename as the S3 key
# This will upload 'reports/report.csv' to 's3://my-data-bucket/report.csv'
s3dk.upload_s3_file(
    local_path="reports/report.csv",
    bucket="my-data-bucket"
)
```

### Download a File

The `download_s3_file` function is versatile. You can download a file to a local path or load it directly into a Pandas DataFrame.

The download_s3_file function accepts the following parameters:

`bucket (str): Required.` The name of the S3 bucket where the file is located.

`s3_path (str): Required.` The full path (key) of the file within the bucket.
local_path (str, optional): The local path where the file will be saved. If you don't provide this, the file will be saved in a data/ directory in your current working folder, using its original S3 filename.

`to_df (bool, optional, default: False):` If set to True, the function will attempt to read the downloaded file into a Pandas DataFrame. This is useful for .csv and Stata .dta files.

`replace (bool, optional, default: False):` If True, it will overwrite a local file if it already exists. By default, it skips the download if the file is already present to save time and bandwidth.

`low_memory (bool, optional, default: True):` When reading a CSV into a DataFrame (to_df=True), this is passed to pandas.read_csv to process the file in chunks, which can reduce memory usage for large files.

`sep (str, optional, default: ","):`**` The separator or delimiter to use when reading a CSV file into a DataFrame. For example, use '\t' for tab-separated files.

**Option 1: Download to a local path**

By default, if `local_path` is not provided, files are saved to a `data/` directory in the current working directory.

```python
import s3datakit as s3dk

# Download to a specific path
local_file = s3dk.download_s3_file(
    bucket="my-data-bucket",
    s3_path="final-reports/report_2025.csv",
    local_path="downloads/report.csv"
)
print(f"File downloaded to: {local_file}")

# Download to the default 'data/' directory, overwriting if it exists
s3dk.download_s3_file(
    bucket="my-data-bucket",
    s3_path="final-reports/report_2025.csv",
    replace=True
)
```

**Option 2: Download directly to a Pandas DataFrame**
```python
import s3datakit as s3dk

df = s3dk.download_s3_file(
    bucket="my-data-bucket",
    s3_path="stata-data/survey.dta",
    to_df=True
)
print(df.head())
```