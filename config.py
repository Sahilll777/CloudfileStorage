# config.py
import os

# ---------------- JWT Configuration ----------------
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_ME_IN_ENV")

# ---------------- MySQL Configuration ----------------
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DB", "cloud_storage"),
    "auth_plugin": "mysql_native_password"
}

# ---------------- AWS S3 Configuration ----------------
AWS_CONFIG = {
    "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
    "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
    "region_name": os.getenv("AWS_REGION", "ap-south-1"),
    "bucket_name": os.getenv("AWS_BUCKET_NAME", "securecloud-file-storage-sahil")
}

# Debug check
if __name__ == "__main__":
    print("MySQL Config:", MYSQL_CONFIG)
    print("JWT Secret:", JWT_SECRET_KEY[:5] + "...")
    print("AWS Keys Loaded:", bool(AWS_CONFIG["aws_access_key_id"]))
