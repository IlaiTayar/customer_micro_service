import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Optional

from fastapi import Header, HTTPException

from database import config

ROLE_CUSTOMER = "customer"
ROLE_ADMIN = "admin"
ADMIN_ID = 100
ADMIN_EMAIL = "admin@admin"


def is_admin(principal_id: Optional[int], email: Optional[str]) -> bool:
    if principal_id is None:
        return False
    return int(principal_id) == ADMIN_ID and (email or "").strip().lower() == ADMIN_EMAIL


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64url_decode(segment: str) -> bytes:
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def _sign(signing_input: bytes) -> str:
    signature = hmac.new(config.AUTH_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return _b64url_encode(signature)


def create_access_token(principal_id: int, role: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    issued_at = int(time.time())
    payload = {
        "sub": principal_id,
        "role": role,
        "iat": issued_at,
        "exp": issued_at + config.AUTH_TOKEN_TTL_MINUTES * 60,
    }

    header_segment = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_segment = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")

    return f"{header_segment}.{payload_segment}.{_sign(signing_input)}"


@dataclass
class Principal:
    principal_id: int
    role: str


def _decode_token(token: str) -> Principal:
    try:
        header_segment, payload_segment, signature = token.split(".")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    expected_signature = _sign(signing_input)
    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    try:
        payload = json.loads(_b64url_decode(payload_segment))
    except (ValueError, json.JSONDecodeError):
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    if int(payload.get("exp", 0)) < int(time.time()):
        raise HTTPException(status_code=401, detail="Authentication token expired")

    return Principal(principal_id=int(payload["sub"]), role=str(payload.get("role", "")))


async def get_current_principal(authorization: Optional[str] = Header(default=None)) -> Principal:
    if authorization is None or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = authorization.split(" ", 1)[1].strip()
    return _decode_token(token)


def require_ownership(principal: Principal, owner_id: Optional[int]) -> None:
    if principal.role == ROLE_ADMIN:
        return
    if owner_id is None or principal.principal_id != int(owner_id):
        raise HTTPException(status_code=403, detail="Forbidden: you can only modify your own resources")
