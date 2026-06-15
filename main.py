from contextlib import asynccontextmanager
from fastapi import FastAPI
from database.connection import engine, Base
from api.routers.auth import router as auth_router

# Обязательно импортируем модели, чтобы Base.metadata о них узнал
import models.user

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Действия при запуске (Создание таблиц)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Действия при выключении
    await engine.dispose()

app = FastAPI(
    title="Auth Microservice",
    lifespan=lifespan
)

app.include_router(auth_router)