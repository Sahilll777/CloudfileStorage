# utils/s3_helper.py
import os
import boto3
import io
from botocore.exceptions import ClientError

AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "ap-south-1")
BUCKET_NAME = "securecloud-file-storage-sahil"

# Create boto3 S3 client (credentials auto-read from env or ~/.aws/credentials)
s3_client = boto3.client("s3", region_name=AWS_REGION)


# -------------------------------------------------------------
# 1️⃣ Upload raw bytes safely
# -------------------------------------------------------------
def upload_bytes(data: bytes, s3_key: str):
    """Upload raw bytes to S3 safely."""
    try:
        fileobj = io.BytesIO(data)
        s3_client.upload_fileobj(fileobj, BUCKET_NAME, s3_key)
        return True
    except ClientError as e:
        print("❌ S3 Upload Error:", e)
        raise


# -------------------------------------------------------------
# 2️⃣ Generate presigned URL for downloading
# -------------------------------------------------------------
def generate_presigned_url(s3_key: str, expires=900):
    try:
        return s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET_NAME, "Key": s3_key},
            ExpiresIn=expires,
        )
    except ClientError as e:
        print("❌ Presigned URL Error:", e)
        raise


# -------------------------------------------------------------
# 3️⃣ Delete S3 object
# -------------------------------------------------------------
def delete_s3_object(s3_key: str):
    try:
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=s3_key)
        return True
    except ClientError as e:
        print("❌ Delete Error:", e)
        raise
