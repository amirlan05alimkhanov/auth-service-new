from pydantic import BaseModel, EmailStr, Field

class CompanyRegisterRequest(BaseModel):
    company_name: str
    bin: str
    bin: str = Field(..., min_length=12, max_length=12, pattern=r"^\d{12}$")
    requisites: str
    username: str
    email: EmailStr
    password: str

class ContractorRegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_self_employed: bool

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    refresh: str
    access: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    company: int | None = Field(default=None, validation_alias="company_id", serialization_alias="company")
    is_self_employed: bool
    model_config = {"from_attributes": True}


class EmailVerificationRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
    new_password: str = Field(..., min_length=6)