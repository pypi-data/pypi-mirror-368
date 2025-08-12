import os
import json
import requests
import boto3
from urllib.parse import urlparse

def load_tfstate(tfstate_path):
    if tfstate_path.startswith("s3://"):
        return load_from_s3(tfstate_path)
    elif tfstate_path.startswith("http://") or tfstate_path.startswith("https://"):
        return load_from_http(tfstate_path)
    else:
        if not os.path.exists(tfstate_path):
            raise FileNotFoundError(f"Local tfstate file not found: {tfstate_path}")
        with open(tfstate_path) as f:
            return json.load(f)

def load_from_http(url):
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def load_from_s3(s3_uri):
    parsed = urlparse(s3_uri)
    bucket = parsed.netloc
    key = parsed.path.lstrip("/")
    s3 = boto3.client("s3")
    obj = s3.get_object(Bucket=bucket, Key=key)
    return json.loads(obj["Body"].read().decode())
