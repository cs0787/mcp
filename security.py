"""
Security primitives for the multi-user control plane.

- Passwords: bcrypt (salted, one-way).
- API keys: a random token is shown to the user ONCE; only its SHA-256 hash
  is ever stored, so a DB leak doesn't hand out usable keys.
- Neon connection strings: these contain real DB credentials, so they're
  encrypted at rest with Fernet (symmetric, authenticated encryption) using
  a key that lives only in the server's environment (ENCRYPTION_KEY).
"""

import os
import hashlib
import secrets

import bcrypt
from cryptography.fernet import Fernet, InvalidToken

_ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY")
if not _ENCRYPTION_KEY:
    raise RuntimeError(
        "ENCRYPTION_KEY environment variable is not set. Generate one with:\n"
        '  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
    )

_fernet = Fernet(_ENCRYPTION_KEY.encode())


# ---------------------------------------------------------------------------
# Passwords
# ---------------------------------------------------------------------------
def hash_password(raw_password: str) -> str:
    return bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(raw_password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(raw_password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        # Malformed hash in DB -- fail closed rather than raising 500s.
        return False


# ---------------------------------------------------------------------------
# API keys
# ---------------------------------------------------------------------------
def generate_api_key() -> str:
    # Prefixed so a stray key is recognizable in logs/screenshots -- makes it
    # easier for a user to tell "this is a secret" if they ever paste it
    # somewhere by accident.
    return "sbmcp_" + secrets.token_urlsafe(32)


def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Connection string encryption
# ---------------------------------------------------------------------------
def encrypt_text(plaintext: str) -> str:
    return _fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_text(ciphertext: str) -> str:
    try:
        return _fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
    except InvalidToken as e:
        raise ValueError(
            "Could not decrypt stored connection string -- ENCRYPTION_KEY may have "
            "changed since it was saved."
        ) from e


def mask_connection_string(connection_string: str) -> str:
    """postgresql://user:password@host/db -> postgresql://****:****@host/db"""
    import re

    return re.sub(r"//([^:/@]*):([^@]*)@", "//****:****@", connection_string)
