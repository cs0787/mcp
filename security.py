"""
Security primitives for the multi-user control plane.
Updated for Vercel lazy evaluation.
"""

import os
import hashlib
import secrets

import bcrypt
from cryptography.fernet import Fernet, InvalidToken

_fernet = None


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        key = os.environ.get("ENCRYPTION_KEY")
        if not key:
            raise RuntimeError(
                "ENCRYPTION_KEY environment variable is not set in Vercel settings."
            )
        _fernet = Fernet(key.encode())
    return _fernet


# ---------------------------------------------------------------------------
# Passwords
# ---------------------------------------------------------------------------
def hash_password(raw_password: str) -> str:
    return bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(raw_password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(raw_password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# API keys
# ---------------------------------------------------------------------------
def generate_api_key() -> str:
    return "sbmcp_" + secrets.token_urlsafe(32)


def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Connection string encryption
# ---------------------------------------------------------------------------
def encrypt_text(plaintext: str) -> str:
    return _get_fernet().encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_text(ciphertext: str) -> str:
    try:
        return _get_fernet().decrypt(ciphertext.encode("utf-8")).decode("utf-8")
    except InvalidToken as e:
        raise ValueError(
            "Could not decrypt stored connection string -- ENCRYPTION_KEY may have changed."
        ) from e


def mask_connection_string(connection_string: str) -> str:
    import re
    return re.sub(r"//([^:/@]*):([^@]*)@", "//****:****@", connection_string)
