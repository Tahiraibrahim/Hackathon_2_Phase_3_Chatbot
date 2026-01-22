"""
Authentication Skill
====================

Pure business logic for authentication operations, framework-agnostic, independently testable.

CONSTRAINTS (from Constitution & ADR-001):
- ❌ NO FastAPI imports
- ❌ NO HTTP request/response handling
- ❌ NO HTML/template rendering
- ✅ ONLY: passlib, jwt, Python standard library
- ✅ Functions accept primitives (str, int)
- ✅ Functions return primitives (str, bool, int, None)
- ✅ Must be testable WITHOUT FastAPI

This Skill contains authentication logic extracted from backend/auth.py:
- get_password_hash (line 37-38) → hash_password
- verify_password (line 40-41) → verify_password
- create_token (line 43-46) → create_jwt_token
- New helper → decode_jwt_token

Business Rules:
- Passwords: bcrypt hashing (secure, salted)
- JWT Tokens: HS256 algorithm, user_id in "sub" claim
- Token Expiry: Configurable (default: 60 minutes)
- Secret Key: Provided by caller (dependency injection)
"""

from typing import Optional
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone


# Bcrypt context for password hashing
# Note: Created here (module-level) for performance
# Creating CryptContext is expensive, reuse across function calls
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Bcrypt automatically handles salting, so the same password
    will generate different hashes each time (secure).

    Args:
        password: Plaintext password to hash

    Returns:
        Bcrypt hashed password string (starts with $2b$ or $2a$)

    Examples:
        >>> hashed = hash_password("mysecretpassword")
        >>> hashed.startswith("$2")
        True
        >>> len(hashed) > 50
        True

        >>> # Same password generates different hashes (salt)
        >>> hash1 = hash_password("password")
        >>> hash2 = hash_password("password")
        >>> hash1 != hash2
        True

    Extracted from: backend/auth.py:37-38 (get_password_hash)
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.

    Args:
        plain_password: Plaintext password to verify
        hashed_password: Bcrypt hashed password to check against

    Returns:
        True if password matches, False otherwise

    Examples:
        >>> hashed = hash_password("mysecret")
        >>> verify_password("mysecret", hashed)
        True

        >>> verify_password("wrongpassword", hashed)
        False

        >>> # Case-sensitive
        >>> verify_password("MySecret", hashed)
        False

    Extracted from: backend/auth.py:40-41 (verify_password)
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Invalid hash format or verification error
        return False


def create_jwt_token(
    user_id: int,
    secret_key: str,
    expiry_minutes: int = 60
) -> str:
    """
    Create a JWT token for a user.

    JWT Structure:
    - Header: Algorithm (HS256)
    - Payload: {"sub": user_id_as_string, "exp": expiry_timestamp}
    - Signature: HMAC with secret_key

    Args:
        user_id: ID of the user to create token for
        secret_key: Secret key for signing the JWT (provided by caller)
        expiry_minutes: Token expiry in minutes (default: 60)

    Returns:
        JWT token string (format: header.payload.signature)

    Examples:
        >>> token = create_jwt_token(user_id=42, secret_key="my_secret")
        >>> len(token) > 50
        True
        >>> token.count(".") == 2  # Three parts
        True

        >>> # Different users get different tokens
        >>> token1 = create_jwt_token(1, "secret")
        >>> token2 = create_jwt_token(2, "secret")
        >>> token1 != token2
        True

    Extracted from: backend/auth.py:43-46 (create_token)
    Modified: Accepts secret_key and expiry_minutes as parameters
              (dependency injection, not reading from environment)
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)
    payload = {
        "sub": str(user_id),  # Subject: user ID as string
        "exp": expire          # Expiry: UTC timestamp
    }
    return jwt.encode(payload, secret_key, algorithm="HS256")


def decode_jwt_token(token: str, secret_key: str) -> Optional[int]:
    """
    Decode a JWT token and extract the user ID.

    Args:
        token: JWT token string to decode
        secret_key: Secret key for verifying the JWT signature

    Returns:
        User ID (int) if token is valid, None otherwise

    Returns None if:
    - Token is expired
    - Token signature is invalid (wrong secret key)
    - Token format is malformed
    - Token is missing required claims ("sub")

    Examples:
        >>> token = create_jwt_token(user_id=42, secret_key="secret")
        >>> decode_jwt_token(token, secret_key="secret")
        42

        >>> # Wrong secret returns None
        >>> decode_jwt_token(token, secret_key="wrong_secret")
        None

        >>> # Invalid token returns None
        >>> decode_jwt_token("invalid.token", secret_key="secret")
        None

    Extracted from: New helper function (not in original auth.py)
    Purpose: Needed by Orchestrators to decode tokens
    """
    try:
        # Decode JWT and verify signature
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])

        # Extract user_id from "sub" claim
        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None

        # Convert to integer
        return int(user_id_str)

    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Invalid signature, malformed token, etc.
        return None
    except (ValueError, TypeError):
        # Failed to convert user_id to int
        return None
