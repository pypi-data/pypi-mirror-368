from fastapi import Request, HTTPException, Depends
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from jose import jwt
import os, time

OAUTH_CLIENT_ID = os.getenv("SNAPCHECK_OAUTH_CLIENT_ID")
OAUTH_CLIENT_SECRET = os.getenv("SNAPCHECK_OAUTH_CLIENT_SECRET")
SECRET_KEY = os.getenv("SNAPCHECK_SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"

def add_session(app):
    app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

def make_oauth():
    oauth = OAuth()
    oauth.register(
        name="github",
        client_id=OAUTH_CLIENT_ID,
        client_secret=OAUTH_CLIENT_SECRET,
        server_metadata_url="https://github.com/.well-known/openid-configuration",
        client_kwargs={"scope": "read:user user:email"},
    )
    return oauth

def require_login(config):
    async def _inner(request: Request):
        if not (config.get("security") or {}).get("enabled"):
            return
        user = request.session.get("user")
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        allowed_emails = set((config["security"].get("allowed_emails") or []))
        allowed_orgs = set((config["security"].get("allowed_orgs") or []))
        if allowed_emails and user.get("email") not in allowed_emails:
            raise HTTPException(status_code=403, detail="Email not allowed")
        if allowed_orgs:
            if not any(org in allowed_orgs for org in (user.get("orgs") or [])):
                raise HTTPException(status_code=403, detail="Org not allowed")
        return user
    return _inner

def user_role(config, email: str) -> str:
    rbac = (config.get("security") or {}).get("rbac") or {}
    if email in rbac:
        return rbac[email]
    if "@" in email:
        domain = "@" + email.split("@", 1)[1]
        if domain in rbac:
            return rbac[domain]
    return rbac.get("*", "viewer")

def require_role(config, required: str):
    order = {"viewer": 0, "engineer": 1, "admin": 2}
    async def _inner(user = Depends(require_login(config))):
        role = user.get("role", "viewer")
        if order.get(role, 0) < order.get(required, 0):
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user
    return _inner

def create_share_token(subject: str, minutes: int = 60) -> str:
    now = int(time.time())
    payload = {"sub": subject, "exp": now + minutes * 60, "iat": now}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_share_token(token: str) -> str:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return payload.get("sub")
