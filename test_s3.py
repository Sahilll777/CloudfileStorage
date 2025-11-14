import boto3
from config import AWS_CONFIG

s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_CONFIG['aws_access_key_id'],
    aws_secret_access_key=AWS_CONFIG['aws_secret_access_key'],
    region_name=AWS_CONFIG['region_name']
)

# List buckets
buckets = s3.list_buckets()
print("Buckets:")
for b in buckets['Buckets']:
    print(b['Name'])
