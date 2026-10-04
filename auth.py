"""Sanad auth: bcrypt passwords, JWT sessions, role enforcement.
Passwords live hashed in the DB; the source code contains none."""
import os, time
from datetime import datetime, timedelta
from functools import wraps
import bcrypt
import jwt
import structlog
from db import tx, User, Tenant, new_id, audit

log = structlog.get_logger("sanad.auth")

JWT_SECRET = os.environ.get("SANAD_JWT_SECRET", "change-me-in-production")
JWT_ALG = "HS256"
TTL_HOURS = int(os.environ.get("SANAD_TOKEN_TTL_HOURS", "12"))

VALID_ROLES = {"rm", "credit_analyst", "scu", "verifier", "admin", "committee"}

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=12)).decode()

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False

def create_token(user_id: str, tenant_id: str, role: str, email: str) -> str:
    payload = {
        "sub": user_id, "tenant_id": tenant_id, "role": role, "email": email,
        "iat": int(time.time()), "exp": int(time.time()) + TTL_HOURS * 3600,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except jwt.ExpiredSignatureError:
        log.warning("token_expired")
        return None
    except jwt.InvalidTokenError:
        log.warning("token_invalid")
        return None

def require_role(*roles):
    """Decorator for FastAPI endpoints: enforces role + tenant scope."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            token = kwargs.pop("token", None) or _extract_token()
            if not token:
                from fastapi import HTTPException
                raise HTTPException(401, "Missing or invalid token")
            user = decode_token(token)
            if not user:
                from fastapi import HTTPException
                raise HTTPException(401, "Token expired or invalid")
            if user["role"] not in roles:
                from fastapi import HTTPException
                raise HTTPException(403, f"Role {user['role']} not authorized")
            kwargs["user"] = user
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def _extract_token():
    """Pulls JWT from Authorization header or query param (for simplicity)."""
    from fastapi import Request
    try:
        req: Request = _current_request()
        auth = req.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            return auth[7:]
        return req.query_params.get("token")
    except Exception:
        return None

_current_request = None

def set_request_getter(getter):
    global _current_request
    _current_request = getter

def login(email: str, password: str, tenant_id: str = None):
    """Authenticate. Returns (user_dict, token) or (None, None)."""
    with tx() as s:
        q = s.query(User).filter(User.email == email.lower())
        if tenant_id:
            q = q.filter(User.tenant_id == tenant_id)
        user = q.first()
        if not user or not verify_password(password, user.password_hash):
            log.info("login_failed", email=email)
            return None, None
        tenant = s.query(Tenant).filter(Tenant.id == user.tenant_id).first()
        token = create_token(user.id, user.tenant_id, user.role, user.email)
        audit(s, user.tenant_id, user.id, "login", target_type="user", target_id=user.id)
        log.info("login_ok", email=email, role=user.role)
        return dict(id=user.id, email=user.email, role=user.role,
                    tenant_id=user.tenant_id, tenant_name=tenant.name if tenant else None), token

def register(email: str, password: str, tenant_name: str = None, role: str = "rm"):
    """Register a new user and tenant dynamically. Returns (user_dict, token) or raises."""
    email_clean = email.strip().lower()
    with tx() as s:
        existing = s.query(User).filter(User.email == email_clean).first()
        if existing:
            return None, "User with this email already exists"
        
        t_name = tenant_name or f"Org_{email_clean.split('@')[0]}"
        tenant = Tenant(id=new_id(), name=t_name)
        s.add(tenant); s.flush()
        
        user_id = new_id()
        pw_hash = hash_password(password)
        user = User(id=user_id, tenant_id=tenant.id, email=email_clean, password_hash=pw_hash, role=role)
        s.add(user); s.flush()
        
        audit(s, tenant.id, user.id, "register", target_type="user", target_id=user.id)
        token = create_token(user.id, tenant.id, user.role, user.email)
        log.info("user_registered", email=email_clean, tenant=t_name, role=role)
        return dict(id=user.id, email=user.email, role=user.role, tenant_id=tenant.id, tenant_name=tenant.name), token