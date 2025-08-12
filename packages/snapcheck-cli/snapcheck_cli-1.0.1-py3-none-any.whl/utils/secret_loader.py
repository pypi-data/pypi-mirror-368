import os
import json
import boto3
import requests
from botocore.exceptions import NoCredentialsError

class SecretLoader:
    def __init__(self, profile):
        self.profile = profile
        self.source = profile.get("secrets_source", "env").lower()

    def get(self, key_name):
        if self.source == "env":
            return os.getenv(key_name)
        elif self.source == "vault":
            return self._get_from_vault(key_name)
        elif self.source == "aws_secrets_manager":
            return self._get_from_aws_sm(key_name)
        elif self.source == "github":
            return self._get_from_github(key_name)
        else:
            raise ValueError(f"Unsupported secrets source: {self.source}")

    def _get_from_vault(self, key_name):
        token_env = self.profile.get("vault_token_env", "VAULT_TOKEN")
        token = os.getenv(token_env)
        if not token:
            raise RuntimeError(f"Vault token missing in env var {token_env}")

        vault_addr = self.profile["vault_addr"]
        url = f"{vault_addr}/v1/secret/data/{key_name}"
        headers = {"X-Vault-Token": token}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data["data"]["data"].get("value")

    def _get_from_aws_sm(self, secret_name):
        region = self.profile.get("aws_region", "us-east-1")
        client = boto3.client("secretsmanager", region_name=region)
        try:
            resp = client.get_secret_value(SecretId=secret_name)
            val = resp.get("SecretString", "")
            return json.loads(val) if val.strip().startswith("{") else val
        except NoCredentialsError:
            raise RuntimeError("AWS credentials not set for AWS Secrets Manager")

    def _get_from_github(self, key_name):
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise RuntimeError("GITHUB_TOKEN env var missing")
        owner = self.profile["github_owner"]
        repo = self.profile["github_repo"]
        url = f"https://api.github.com/repos/{owner}/{repo}/actions/secrets/{key_name}"
        headers = {"Authorization": f"token {token}"}
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data.get("value")  # GitHub doesn't return secret value directly
