from fastapi import FastAPI, Request, Response, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import os
import time

# Deps:
#   pip install fastapi uvicorn authlib httpx "python-jose[cryptography]" pyyaml
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
try:
    # Make proxy header middleware optional (older Starlette may not have it)
    from starlette.middleware.proxy_headers import ProxyHeadersMiddleware  # type: ignore
    HAS_PROXY_MW = True
except Exception:
    ProxyHeadersMiddleware = None  # type: ignore
    HAS_PROXY_MW = False

from jose import jwt
import httpx
import yaml

# ------------------------------
# Optional internal deps
# ------------------------------
try:
    from config.config_loader import load_config
except Exception:
    def load_config(_): return {}

try:
    from utils.audit_log import write_audit_event
except Exception:
    def write_audit_event(*args, **kwargs):  # no-op if missing
        pass

# ------------------------------
# App
# ------------------------------
app = FastAPI(title="SnapCheck Web")
# Trust X-Forwarded-* when behind TLS terminator / proxy (if available)
if HAS_PROXY_MW:
    app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# ------------------------------
# Security / Profile (robust loader)
# ------------------------------
PROFILE_PATH = os.environ.get("SNAPCHECK_PROFILE", "profiles/demo.yaml")

CONFIG: Dict[str, Any] = {}
LOAD_ERR: Optional[str] = None

try:
    CONFIG = load_config(PROFILE_PATH) or {}
    # Coerce non-dicts (dataclass/namespace) into dict
    if not isinstance(CONFIG, dict):
        CONFIG = dict(CONFIG) if hasattr(CONFIG, "__iter__") else getattr(CONFIG, "__dict__", {})
except Exception as e:
    LOAD_ERR = f"load_config failed: {e}"
    try:
        CONFIG = yaml.safe_load(Path(PROFILE_PATH).read_text(encoding="utf-8")) or {}
    except Exception as e2:
        LOAD_ERR += f" | fallback yaml.safe_load failed: {e2}"
        CONFIG = {}

SEC_CONF: Dict[str, Any] = (CONFIG.get("security") or {})
SEC_ENABLED: bool = bool(SEC_CONF.get("enabled"))
OAUTH_PROVIDER: str = SEC_CONF.get("auth_provider", "github")

SECRET_KEY: str = os.getenv("SNAPCHECK_SECRET_KEY", "dev-secret-change-me")  # sessions + JWT share tokens
JWT_ALGO = "HS256"

# OAuth creds ONLY via env
OAUTH_CLIENT_ID = os.getenv("SNAPCHECK_OAUTH_CLIENT_ID")
OAUTH_CLIENT_SECRET = os.getenv("SNAPCHECK_OAUTH_CLIENT_SECRET")

# ------------------------------
# Session middleware (safe even if security disabled)
# ------------------------------
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie=(SEC_CONF.get("session", {}) or {}).get("cookie_name", "snapcheck_session"),
    max_age=int((SEC_CONF.get("session", {}) or {}).get("max_age_seconds", 86400)),
    same_site=(SEC_CONF.get("session", {}) or {}).get("same_site", "lax"),
    https_only=bool((SEC_CONF.get("session", {}) or {}).get("https_only", False)),
)

# ------------------------------
# OAuth (classic GitHub OAuth2)
# ------------------------------
oauth = OAuth()
if OAUTH_PROVIDER == "github":
    oauth.register(
        name="github",
        client_id=OAUTH_CLIENT_ID,
        client_secret=OAUTH_CLIENT_SECRET,
        access_token_url="https://github.com/login/oauth/access_token",
        authorize_url="https://github.com/login/oauth/authorize",
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "read:user user:email read:org"},
    )

# ------------------------------
# RBAC helpers
# ------------------------------
def _user_role(email: str) -> str:
    # SEC_CONF.rbac supports exact email, domain (e.g. "@acme.com"), or "*" default
    rbac = (SEC_CONF.get("rbac") or {})
    if email in rbac:
        return rbac[email]
    if "@" in email:
        domain = "@" + email.split("@", 1)[1]
        if domain in rbac:
            return rbac[domain]
    return rbac.get("*", "viewer")

def require_login():
    async def _inner(request: Request) -> Optional[Dict[str, Any]]:
        if not SEC_ENABLED:
            return None  # open mode
        user = request.session.get("user")
        if not user:
            # friendlier UX: redirect to login instead of 401
            # using HTTPException with Location to avoid dependency order issues
            raise HTTPException(status_code=303, detail="See Other", headers={"Location": "/login"})
        # allow-lists
        allowed_emails = set(SEC_CONF.get("allowed_emails") or [])
        allowed_orgs = set(SEC_CONF.get("allowed_orgs") or [])
        if allowed_emails and (user.get("email") or "").lower() not in {e.lower() for e in allowed_emails}:
            raise HTTPException(status_code=403, detail="Email not allowed")
        if allowed_orgs:
            orgs = [o.lower() for o in (user.get("orgs") or [])]
            if not any(o in orgs for o in {o.lower() for o in allowed_orgs}):
                raise HTTPException(status_code=403, detail="Org not allowed")
        return user
    return _inner

def require_role(required: str):
    order = {"viewer": 0, "engineer": 1, "admin": 2}
    async def _inner(user = Depends(require_login())):
        if not SEC_ENABLED:
            return {"role": "admin"}  # open mode, no gate
        role = (user or {}).get("role", "viewer")
        if order.get(role, 0) < order.get(required, 0):
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user
    return _inner

# ------------------------------
# Share tokens (signed, expiring)
# ------------------------------
def create_share_token(subject: str, minutes: int = 60) -> str:
    now = int(time.time())
    payload = {"sub": subject, "exp": now + minutes * 60, "iat": now}
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGO)

def verify_share_token(token: str) -> str:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGO])
    return payload.get("sub")

# ------------------------------
# Helpers
# ------------------------------
def _inject_client_js(html: str) -> str:
    # If you have /static/app.js, inject it before </body>
    snippet = '<script src="/static/app.js"></script></body>'
    return html.replace("</body>", snippet)

def _read(path: Path) -> Response:
    if not path.exists():
        return Response("<h1>Report Not Found</h1>", status_code=404, media_type="text/html")
    html = path.read_text(encoding="utf-8")
    wm = SEC_CONF.get("watermark")
    if wm:
        html = html.replace("<body", f'<body data-watermark="{wm}"', 1)
    return Response(_inject_client_js(html), media_type="text/html")

# ------------------------------
# Static mounts (protect when SEC_ENABLED)
# ------------------------------
STATIC_ROOTS: List[Tuple[str, Path]] = []
proj_static = Path("output/static")
tmpl_static = Path("output/templates/static")
if proj_static.exists():
    STATIC_ROOTS.append(("static", proj_static))
elif tmpl_static.exists():
    STATIC_ROOTS.append(("static", tmpl_static))

if SEC_ENABLED and STATIC_ROOTS:
    # Gate static via auth when security is enabled
    _static_dir = STATIC_ROOTS[0][1]

    def _safe_join(base: Path, rel: str) -> Path:
        target = (base / rel).resolve()
        if not str(target).startswith(str(base.resolve())):
            raise HTTPException(status_code=404, detail="Not found")
        return target

    @app.get("/static/{path:path}", dependencies=[Depends(require_login())])
    async def protected_static(path: str):
        target = _safe_join(_static_dir, path)
        if not target.exists():
            raise HTTPException(status_code=404, detail="Not found")
        return FileResponse(str(target))
else:
    for mount_name, static_dir in STATIC_ROOTS:
        app.mount(f"/{mount_name}", StaticFiles(directory=str(static_dir)), name=mount_name)

# ------------------------------
# Debug + Startup logs
# ------------------------------
@app.get("/_debug")
def _debug():
    return {
        "profile_path": PROFILE_PATH,
        "profile_abs": str(Path(PROFILE_PATH).resolve()),
        "profile_exists": Path(PROFILE_PATH).exists(),
        "load_error": LOAD_ERR,
        "config_keys": list(CONFIG.keys()),
        "security_block": SEC_CONF,
        "sec_enabled": SEC_ENABLED,
        "auth_provider": OAUTH_PROVIDER,
        "has_client_id": bool(OAUTH_CLIENT_ID),
        "has_client_secret": bool(OAUTH_CLIENT_SECRET),
        "session_cookie": (SEC_CONF.get("session", {}) or {}).get("cookie_name", "snapcheck_session"),
    }

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.on_event("startup")
async def _print_boot():
    print("[SnapCheck] profile:", PROFILE_PATH, "| abs:", Path(PROFILE_PATH).resolve(), "| exists:", Path(PROFILE_PATH).exists())
    print("[SnapCheck] load_error:", LOAD_ERR)
    print("[SnapCheck] config_keys:", list(CONFIG.keys()))
    print("[SnapCheck] security.enabled:", SEC_ENABLED)
    print("[SnapCheck] provider:", OAUTH_PROVIDER)
    print("[SnapCheck] client_id?", bool(OAUTH_CLIENT_ID))
    if not HAS_PROXY_MW:
        print("[SnapCheck] note: ProxyHeadersMiddleware not available; continuing without it")

# ------------------------------
# OAuth routes
# ------------------------------
async def _github_identity(token: dict) -> Dict[str, Any]:
    headers = {"Authorization": f"token {token['access_token']}"}
    async with httpx.AsyncClient() as client:
        me = await client.get("https://api.github.com/user", headers=headers)
        me.raise_for_status()
        emails = await client.get("https://api.github.com/user/emails", headers=headers)
        emails.raise_for_status()
        orgs = await client.get("https://api.github.com/user/orgs", headers=headers)
        orgs.raise_for_status()
    me = me.json()
    emails = emails.json()
    orgs = orgs.json()

    primary_email = next((e["email"] for e in emails if e.get("primary")), None)
    if not primary_email:
        primary_email = next((e["email"] for e in emails if e.get("verified")), None)

    return {
        "email": (primary_email or "").lower(),
        "name": me.get("name") or me.get("login"),
        "orgs": [o["login"] for o in orgs],
    }

@app.get("/login")
async def login(request: Request):
    if not SEC_ENABLED:
        return RedirectResponse(url="/")
    if not (OAUTH_CLIENT_ID and OAUTH_CLIENT_SECRET):
        raise HTTPException(status_code=500, detail="OAuth not configured")
    redirect_uri = request.url_for("auth")
    return await oauth.github.authorize_redirect(request, str(redirect_uri))

@app.get("/auth")
async def auth(request: Request):
    if not SEC_ENABLED:
        return RedirectResponse(url="/")
    try:
        token = await oauth.github.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(401, f"OAuth exchange failed: {e}")
    ident = await _github_identity(token)
    role = _user_role(ident["email"]) if ident["email"] else "viewer"
    request.session["user"] = {**ident, "role": role}
    write_audit_event("login", {"email": ident["email"], "role": role})
    return RedirectResponse(url="/")

@app.post("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/login")

# ------------------------------
# Protected views
# ------------------------------
@app.get("/", response_class=HTMLResponse)
async def latest(user = Depends(require_login())):
    """Serve latest report .snapcheck/report.html (auth-gated if enabled)."""
    p = Path(".snapcheck/report.html")
    if not p.exists():
        reports_dir = Path(".snapcheck/reports")
        if reports_dir.exists():
            files = sorted(reports_dir.glob("report-*.html"))
            if files:
                write_audit_event("report_view", {"path": str(files[-1])})
                return _read(files[-1])
    write_audit_event("report_view", {"path": str(p)})
    return _read(p)

@app.get("/report", response_class=HTMLResponse)
async def report_alias(user = Depends(require_login())):
    """Alias for latest report for backwards compatibility."""
    return await latest()  # type: ignore

@app.get("/reports/{name}", response_class=HTMLResponse)
async def get_report(name: str, user = Depends(require_login())):
    """Serve archived report from .snapcheck/reports/"""
    path = Path(".snapcheck/reports") / name
    write_audit_event("report_view", {"path": str(path)})
    return _read(path)

# ------------------------------
# Share links (token-gated, no login needed to view)
# ------------------------------
@app.get("/share")
async def share_create(minutes: Optional[int] = None, user = Depends(require_role("engineer"))):
    share_cfg = (SEC_CONF.get("share") or {})
    if not SEC_ENABLED:
        raise HTTPException(status_code=400, detail="Security disabled")
    if not share_cfg.get("enabled", False):
        raise HTTPException(status_code=403, detail="Sharing disabled")
    exp = minutes or int(share_cfg.get("default_expiry_minutes", 60))
    token = create_share_token("report", exp)
    write_audit_event("share_created", {"by": (user or {}).get("email"), "minutes": exp})
    return {"url": f"/shared?token={token}", "expires_in_minutes": exp}

@app.get("/shared", response_class=HTMLResponse)
async def shared(token: str):
    subject = verify_share_token(token)  # raises if invalid/expired
    if subject != "report":
        raise HTTPException(status_code=400, detail="Bad token")
    p = Path(".snapcheck/report.html")
    if not p.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    write_audit_event("report_shared_view", {})
    return _read(p)