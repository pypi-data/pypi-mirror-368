# config/profile_schema.py
from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field


# ---------- Existing models ----------
class DockerImage(BaseModel):
    name: str
    tags: List[str]


class GitOpsConfig(BaseModel):
    method: str
    test_mode: Optional[bool] = False
    argocd_server: Optional[str] = ""
    token: Optional[str] = None
    app_whitelist: List[str] = Field(default_factory=list)


# ---------- New: Security models ----------
class SessionConfig(BaseModel):
    cookie_name: str = "snapcheck_session"
    max_age_seconds: int = 86400
    same_site: Literal["lax", "strict", "none"] = "lax"
    https_only: bool = False


class ShareConfig(BaseModel):
    enabled: bool = False
    default_expiry_minutes: int = 60


class SecurityConfig(BaseModel):
    enabled: bool = False
    auth_provider: Literal["github", "google", "okta"] = "github"
    allowed_emails: List[str] = Field(default_factory=list)
    allowed_orgs: List[str] = Field(default_factory=list)
    # RBAC map: exact email, "@domain", or "*" -> role ("viewer"|"engineer"|"admin")
    rbac: Dict[str, Literal["viewer", "engineer", "admin"]] = Field(default_factory=lambda: {"*": "viewer"})
    watermark: Optional[str] = None
    session: SessionConfig = SessionConfig()
    share: ShareConfig = ShareConfig()


# ---------- Root profile ----------
class ProfileConfig(BaseModel):
    name: str
    aws_region: str

    secrets_source: str
    vault_addr: Optional[str] = None
    vault_token_env: Optional[str] = "VAULT_TOKEN"
    env_secrets: List[str]

    modules: List[str]

    terraform_state: Optional[str] = None
    kubeconfig: Optional[str] = None
    helm_namespaces: Optional[List[str]] = None

    ci_platform: Optional[str] = None
    github_repo: Optional[str] = None
    github_token: Optional[str] = None

    docker_images: Optional[List[DockerImage]] = None
    gitops: Optional[GitOpsConfig] = None

    demo_mode: Optional[bool] = False

    # NEW: keep the whole security block
    security: Optional[SecurityConfig] = None

    class Config:
        # preserve unknown keys so future fields (or per-user extras) don’t get dropped
        extra = "allow"
        validate_assignment = True