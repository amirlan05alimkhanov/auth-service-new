from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt
from core.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_tokens(subject: int) -> dict:
    now = datetime.now(timezone.utc)

    # Access Token
    access_expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_payload = {"sub": str(subject), "type": "access", "exp": access_expire}
    access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    # Refresh Token
    refresh_expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_payload = {"sub": str(subject), "type": "refresh", "exp": refresh_expire}
    refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return {"access": access_token, "refresh": refresh_token}