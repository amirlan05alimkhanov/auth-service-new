from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.connection import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    bin: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    requisites: Mapped[str | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    users: Mapped[list["User"]] = relationship(back_populates="company")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)

    first_name: Mapped[str | None] = mapped_column()
    last_name: Mapped[str | None] = mapped_column()

    role: Mapped[str] = mapped_column(default="contractor", nullable=False)

    is_active: Mapped[bool] = mapped_column(default=True)
    is_staff: Mapped[bool] = mapped_column(default=False)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    is_self_employed: Mapped[bool] = mapped_column(default=False)

    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    date_joined: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    company_id: Mapped[int | None] = mapped_column(ForeignKey("companies.id"))
    company: Mapped["Company"] = relationship(back_populates="users")