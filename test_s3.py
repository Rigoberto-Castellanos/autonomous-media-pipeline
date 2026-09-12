import os
import boto3
from dotenv import load_dotenv


load_dotenv()

bucket = os.getenv("S3_BUCKET_NAME")
region = os.getenv("AWS_DEFAULT_REGION", "us-east-2")

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=region,
)

with open("cloud_test.txt", "w") as f:
    f.write("AWS S3 pipeline integration verified!")

try:
    print(f"Uploading cloud_test.txt to s3://{bucket}...")
    s3.upload_file("cloud_test.txt", bucket, "cloud_test.txt")
    print("SUCCESS: File uploaded to AWS S3!")
except Exception as e:
    print(f"FAILED: {e}")
