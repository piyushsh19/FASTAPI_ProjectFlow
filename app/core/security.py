
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.core.config import settings


password_hash = PasswordHash.recommended()


# --------------------------------------------------
# Password Security
# --------------------------------------------------

def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


# --------------------------------------------------
# JWT Token Creation
# --------------------------------------------------

def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": str(user_id),
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


# --------------------------------------------------
# JWT Token Validation
# --------------------------------------------------

def decode_access_token(token: str) -> int:
    """
    Validate an access token and return its user ID.

    Required claims:
    - sub: User ID as a string
    - exp: Token expiration timestamp

    Raises:
        jwt.InvalidTokenError: If the token is invalid.
    """

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
            options={
                "require": ["sub", "exp"],
            },
        )

        subject = payload.get("sub")

        if (
            not isinstance(subject, str)
            or not subject.isascii()
            or not subject.isdecimal()
        ):
            raise jwt.InvalidTokenError(
                "Invalid subject claim"
            )

        user_id = int(subject)

        if user_id <= 0:
            raise jwt.InvalidTokenError(
                "Invalid user ID"
            )

        return user_id

    except jwt.InvalidTokenError:
        raise

    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise jwt.InvalidTokenError(
            "Invalid access token"
        ) from exc
