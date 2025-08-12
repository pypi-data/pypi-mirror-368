import os
import yaml

def generate_profile(profile_name: str = "default", output_path: str = "profiles/sample.yaml"):
    profile = {
        "name": profile_name,
        "aws_region": "us-east-1",
        "secrets_source": "env",
        "vault_addr": "https://vault.example.com",
        "vault_token_env": "VAULT_TOKEN",
        "env_secrets": [
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "GITHUB_TOKEN",
            "ARGOCD_TOKEN"
        ],
        "modules": [
            "terraform", "kubernetes", "helm",
            "ci_cd", "docker", "secrets", "cost", "gitops"
        ],
        "terraform_state": "./state.tfstate",
        "kubeconfig": "~/.kube/config",
        "helm_namespaces": ["default", "monitoring"],
        "ci_platform": "github",
        "github_repo": "username/repo",
        "github_token": "${GITHUB_TOKEN}",
        "docker_images": [
            {"name": "username/image", "tags": ["latest", "abc123"]}
        ],
        "gitops": {
            "method": "api",
            "test_mode": True,
            "argocd_server": "https://argo.example.com",
            "token": "${ARGOCD_TOKEN}",
            "app_whitelist": []
        },
        "demo_mode": True
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(profile, f, sort_keys=False)

    print(f"✅ Profile generated at: {output_path}")
