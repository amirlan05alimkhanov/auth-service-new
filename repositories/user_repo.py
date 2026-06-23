from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.user import User, Company
from models.user import VerificationCode
from database.connection import get_db


class UserRepository:
    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.session = session

    async def get_user_by_username(self, username: str) -> User | None:
        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()


    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()


    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def get_company_by_bin(self, bin_val: str) -> Company | None:
        result = await self.session.execute(select(Company).where(Company.bin == bin_val))
        return result.scalar_one_or_none()

    async def create_company_and_admin(self, company: Company, admin: User) -> None:
        self.session.add(company)
        await self.session.flush()  # Получаем ID компании без коммита

        admin.company_id = company.id
        self.session.add(admin)
        await self.session.commit()

    async def create_user(self, user: User) -> None:
        self.session.add(user)
        await self.session.commit()

    async def update_user(self, user: User) -> None:
        await self.session.commit()

    async def save_verification_code(self, verification_code: VerificationCode) -> None:
        self.session.add(verification_code)
        await self.session.commit()

    async def get_verification_code(self, email: str, code: str) -> VerificationCode | None:
        result = await self.session.execute(
            select(VerificationCode).where(
                VerificationCode.email == email,
                VerificationCode.code == code
            )
        )
        return result.scalar_one_or_none()

    async def delete_verification_code(self, verification_code: VerificationCode) -> None:
        await self.session.delete(verification_code)
        await self.session.commit()