from fastapi import HTTPException, status
from datetime import datetime, timezone
from repositories.user_repo import UserRepository
from schemas.user import CompanyRegisterRequest, ContractorRegisterRequest, UserLoginRequest, TokenResponse
from models.user import User, Company
from core.security import hash_password, verify_password, create_tokens


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_company(self, data: CompanyRegisterRequest) -> None:
        if await self.user_repo.get_user_by_username(data.username):
            raise HTTPException(status_code=400, detail="Username already exists")
        if await self.user_repo.get_company_by_bin(data.bin):
            raise HTTPException(status_code=400, detail="Company with this BIN already exists")

        company = Company(name=data.company_name, bin=data.bin)
        admin = User(
            username=data.username,
            email=data.email.lower(),
            password_hash=hash_password(data.password),
            role="admin",
            is_staff=True
        )

        await self.user_repo.create_company_and_admin(company, admin)

    async def register_contractor(self, data: ContractorRegisterRequest) -> None:
        if await self.user_repo.get_user_by_username(data.username):
            raise HTTPException(status_code=400, detail="Username already exists")

        contractor = User(
            username=data.username,
            email=data.email.lower(),
            password_hash=hash_password(data.password),
            role="contractor",
            is_self_employed=data.is_self_employed
        )
        await self.user_repo.create_user(contractor)

    async def login(self, data: UserLoginRequest) -> TokenResponse:
        normalized_email = data.email.lower()
        user = await self.user_repo.get_user_by_email(normalized_email)

        # Проверяем: существует ли юзер, совпадает ли username и верен ли пароль
        if not user or user.username != data.username or not verify_password(data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email, username, or password")

        # Обновляем время последнего входа
        user.last_login = datetime.now(timezone.utc)
        await self.user_repo.update_user(user)

        tokens = create_tokens(user.id)
        return TokenResponse(**tokens)