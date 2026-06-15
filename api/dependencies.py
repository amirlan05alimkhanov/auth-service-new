from typing import AsyncGenerator
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from database.connection import AsyncSessionLocal
from repositories.user_repo import UserRepository
from services.auth_service import AuthService
from core.config import settings
from models.user import User

security = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session=db)


def get_auth_service(repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(user_repo=repo)


# Зависимость для эндпоинта /me/
async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        repo: UserRepository = Depends(get_user_repository)
) -> User:
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    user = await repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user