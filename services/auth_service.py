import random
from fastapi import HTTPException, status, Depends
from datetime import datetime, timezone, timedelta
from repositories.user_repo import UserRepository
from schemas.user import CompanyRegisterRequest, ContractorRegisterRequest, UserLoginRequest, TokenResponse
from models.user import User, Company
from core.security import hash_password, verify_password, create_tokens
from models.user import VerificationCode
from schemas.user import EmailVerificationRequest


class AuthService:
    def __init__(self, user_repo: UserRepository = Depends()):
        self.user_repo = user_repo

    async def register_company(self, data: CompanyRegisterRequest) -> None:
        if await self.user_repo.get_user_by_username(data.username):
            raise HTTPException(status_code=400, detail="Username already exists")
        if await self.user_repo.get_company_by_bin(data.bin):
            raise HTTPException(status_code=400, detail="Company with this BIN already exists")

        normalized_email = data.email.lower()

        company = Company(name=data.company_name, bin=data.bin)
        admin = User(
            username=data.username,
            email=normalized_email,
            password_hash=hash_password(data.password),
            is_active=False,
            role="admin",
            is_staff = True
        )

        # Сохраняем компанию и админа как обычно
        await self.user_repo.create_company_and_admin(company, admin)

        # --- НОВАЯ ЛОГИКА ВЕРИФИКАЦИИ ---
        code = generate_random_code()
        # Код будет жить 5 минут
        expires_at = datetime.now() + timedelta(minutes=5)

        v_code = VerificationCode(email=normalized_email, code=code, expires_at=expires_at)
        await self.user_repo.save_verification_code(v_code)

        # "Отправляем" письмо (код отобразится в консоли PyCharm)
        await send_verification_email(normalized_email, code)

    async def register_contractor(self, data: ContractorRegisterRequest):  # Твое название схемы запроса
        # 1. Приводим почту к нижнему регистру
        normalized_email = data.email.lower()

        # 2. Проверяем, свободен ли email
        existing_user = await self.user_repo.get_user_by_email(normalized_email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

        # 3. Создаем объект контрактора (пользователя)
        contractor = User(
            username=data.username,
            email=normalized_email,
            password_hash=hash_password(data.password),
            is_active=False,  # !!! КРИТИЧЕСКИ ВАЖНО: блокируем до ввода кода
            role="contractor",  # Назначаем роль контрактора
            # ... переносим остальные поля контрактора, которые приходят с фронта ...
        )

        # Сохраняем контрактора в базу данных через твой репозиторий
        await self.user_repo.create_user(contractor)  # Или твой метод сохранения обычного юзера

        # 4. --- ГЕНЕРИРУЕМ И ОТПРАВЛЯЕМ КОД ВЕРИФИКАЦИИ ---
        code = generate_random_code()
        expires_at = datetime.now() + timedelta(minutes=5)  # Код живет 5 минут

        v_code = VerificationCode(email=normalized_email, code=code, expires_at=expires_at)
        await self.user_repo.save_verification_code(v_code)

        # Имитируем отправку (код выведется в консоль PyCharm)
        await send_verification_email(normalized_email, code)

        return {"status": "success", "message": "Регистрация успешна. Код подтверждения отправлен на почту"}


    async def login(self, data: UserLoginRequest) -> TokenResponse:
        normalized_email = data.email.lower()
        user = await self.user_repo.get_user_by_email(normalized_email)

        # 1. Проверяем, существует ли пользователь и верен ли пароль
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # 2. --- ДОБАВЛЯЕМ ПРОВЕРКУ ВЕРИФИКАЦИИ ---
        if not user.is_active:
            raise HTTPException(
                status_code=403,
                detail="Пожалуйста, подтвердите ваш email перед входом в систему"
            )

        # 3. Если всё ок, обновляем время входа и генерируем токены
        user.last_login = datetime.now(timezone.utc)
        await self.user_repo.update_user(user)

        tokens = create_tokens(user.id)
        return TokenResponse(**tokens)


    async def verify_email(self, data: EmailVerificationRequest) -> dict:
        v_code = await self.user_repo.get_verification_code(data.email, data.code)

        if not v_code:
            raise HTTPException(status_code=400, detail="Неверный код верификации")

        if datetime.now() > v_code.expires_at:
            await self.user_repo.delete_verification_code(v_code)
            raise HTTPException(status_code=400, detail="Срок действия кода истек")

        user = await self.user_repo.get_user_by_email(data.email)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        user.is_active = True
        await self.user_repo.update_user(user)

        await self.user_repo.delete_verification_code(v_code)

        return {"status": "success", "message": "Email успешно подтвержден"}


def generate_random_code() -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(6))

async def send_verification_email(email: str, code: str):
    # ЗАГЛУШКА: в реальном проекте тут будет код отправки через SMTP.
    # Сейчас мы просто смотрим код в консоли.
    print("\n" + "="*50)
    print(f"ПИСЬМО ОТПРАВЛЕНО НА {email}")
    print(f"ВАШ КОД ДЛЯ ПОДТВЕРЖДЕНИЯ: {code}")
    print("="*50 + "\n")




