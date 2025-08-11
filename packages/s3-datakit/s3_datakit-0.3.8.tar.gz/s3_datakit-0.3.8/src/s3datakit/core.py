import os
import base64
import hashlib
from pathlib import Path
from typing import Optional, Union, List

import pandas as pd
import boto3
from botocore.exceptions import ClientError


# =========================
# File reading utilities
# =========================
def _read_file_to_df(file_path: str, low_memory: bool = True, sep: Optional[str] = ',') -> pd.DataFrame:
    """Read a CSV or Stata file into a Pandas DataFrame."""
    if file_path.endswith(".csv"):
        return pd.read_csv(file_path, low_memory=low_memory, sep=sep)
    if file_path.endswith(".dta"):
        return pd.read_stata(file_path)
    raise ValueError(f"Unsupported file format for DataFrame: {file_path}")


# =========================
# Local file hashing
# =========================
def _hash_file_md5(path: str, chunk_size: int = 1024 * 1024) -> str:
    """Return the MD5 hash of a file in hexadecimal (used for single-part ETag comparison)."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()

def _hash_file_sha256_b64(path: str, chunk_size: int = 1024 * 1024) -> str:
    """Return the SHA-256 hash of a file in base64 (used for S3 ChecksumSHA256 comparison)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return base64.b64encode(h.digest()).decode("utf-8")


# =========================
# S3 metadata helpers
# =========================
def _head_object(s3, bucket: str, key: str) -> dict:
    """Wrapper for S3 head_object call."""
    return s3.head_object(Bucket=bucket, Key=key)

def _file_matches_s3(bucket: str, key: str, local_path: str, s3=None) -> bool:
    """
    Returns True if the local file matches the S3 object exactly.

    Priority of checks:
      1. Compare S3 ChecksumSHA256 (exact match if object was uploaded with checksum).
      2. Compare ETag (if single-part upload, no '-' in ETag).
      3. Compare file size (last resort, not guaranteed to detect all differences).
    """
    if s3 is None:
        s3 = boto3.client("s3")

    try:
        head = _head_object(s3, bucket, key)
    except ClientError:
        return False

    # 1) Native SHA256 checksum (best option)
    s3_sha256 = head.get("ChecksumSHA256")
    if s3_sha256:
        local_sum = _hash_file_sha256_b64(local_path)
        return local_sum == s3_sha256

    # 2) Single-part ETag (equals MD5 of content)
    etag = head.get("ETag", "").strip('"')
    if etag and "-" not in etag:
        local_md5 = _hash_file_md5(local_path)
        return local_md5 == etag

    # 3) Fallback: compare file size only
    try:
        local_size = os.path.getsize(local_path)
    except OSError:
        return False
    return local_size == head.get("ContentLength", -1)


# =========================
# Public S3 API
# =========================
def list_s3_files(bucket: str,
                  file_type: Optional[str] = None,
                  show_metadata: bool = True) -> List[str]:
    """
    List all object keys in an S3 bucket.
    
    :param bucket: Name of the S3 bucket.
    :param show_metadata: If True, prints metadata for each object.
    :return: List of object keys.
    """
    s3 = boto3.client('s3')
    #keys: List[str] = []
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket)

    for page in pages:
        for obj in page.get('Contents', []):
            key = obj['Key']
            if file_type==None or key.endswith(file_type):

                if show_metadata:
                    size_mb = obj['Size'] / (1024 * 1024)
                
                    if size_mb > 0.01:
                        print(f"------\nFile: {key}")
                        print(f"Size: {size_mb:.2f} MB")
                        print(f"LastModified: {obj['LastModified']}")
    return None

def upload_s3_file(
    bucket: str,
    s3_path: Optional[str] = None,
    local_path: Optional[str] = None,
    use_checksum: bool = True,
    extra_args: Optional[dict] = None,
) -> bool:
    """
    Upload a file to S3.

    If use_checksum=True, requests S3 to calculate and store a SHA256 checksum.
    This allows exact match verification later via head_object.
    """
    if local_path is None:
        raise ValueError("local_path is required")

    if s3_path is None:
        s3_path = os.path.basename(local_path)

    s3_client = boto3.client('s3')

    extra_args = dict(extra_args or {})
    if use_checksum:
        # This will make S3 compute and store the checksum: available in HeadObject as ChecksumSHA256
        extra_args.setdefault("ChecksumAlgorithm", "SHA256")

    try:
        s3_client.upload_file(local_path, bucket, s3_path, ExtraArgs=extra_args or None)
        return True
    except (ClientError, FileNotFoundError) as e:
        print(f"❌ Error uploading file: {e}")
        return False


def download_s3_file(
    bucket: str,
    s3_path: str,
    local_path: Optional[str] = None,
    to_df: bool = False,
    low_memory: bool = True,
    replace: bool = False,
    sep: str = ','
) -> Union[pd.DataFrame, str]:
    """
    Download a file from S3, skipping download if the local file matches exactly.

    Exact match is verified via:
      - ChecksumSHA256 (if available), or
      - Single-part ETag MD5, or
      - File size (last resort)
    """
    if local_path is None:
        filename = os.path.basename(s3_path)
        local_path = f"data/{filename}"

    path_obj = Path(local_path)
    s3 = boto3.client('s3')

    if path_obj.exists() and not replace:
        try:
            if _file_matches_s3(bucket, s3_path, str(path_obj), s3=s3):
                print(f"ℹ️ Local file matches S3 object. Skipping download: '{local_path}'.")
                return _read_file_to_df(str(path_obj), low_memory=low_memory, sep=sep) if to_df else str(path_obj)
            else:
                print("ℹ️ Local file differs from S3 object. Re-downloading.")
        except ClientError as e:
            print(f"⚠️ Could not verify file against S3 ({e}). Proceeding with download.")

    path_obj.parent.mkdir(parents=True, exist_ok=True)

    try:
        print(f"⬇️ Downloading from S3: {s3_path}")
        s3.download_file(bucket, s3_path, str(path_obj))
        print("✅ Download complete.")
    except ClientError as e:
        print(f"❌ Error during download: {e}")
        raise

    return _read_file_to_df(str(path_obj), low_memory=low_memory, sep=sep) if to_df else str(path_obj)


# =========================
# Optional: conditional GET by ETag
# =========================
def download_if_changed_via_etag(
    bucket: str,
    s3_path: str,
    local_path: str,
) -> bool:
    """
    Example: perform a conditional GET to avoid downloading unchanged objects.

    If the stored ETag matches the current S3 ETag, S3 will return 304 Not Modified
    without transferring the file contents.
    Returns True if the file was downloaded (changed), False if not.
    """
    s3 = boto3.client("s3")
    try:
        # Get current ETag without downloading
        head = s3.head_object(Bucket=bucket, Key=s3_path)
        etag = head.get("ETag", "").strip('"')
    except ClientError as e:
        print(f"❌ head_object failed: {e}")
        raise

    try:
        # Will raise ClientError with HTTPStatusCode=304 if not modified
        s3.download_file(bucket, s3_path, local_path, ExtraArgs={"IfNoneMatch": etag})
        print("✅ Downloaded (file changed).")
        return True
    except ClientError as e:
        if e.response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 304:
            print("ℹ️ Not modified (304). Skipped download.")
            return False
        print(f"❌ Conditional download error: {e}")
        raise
