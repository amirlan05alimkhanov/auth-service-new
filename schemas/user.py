from pydantic import BaseModel, EmailStr, Field

class CompanyRegisterRequest(BaseModel):
    company_name: str
    bin: str
    username: str
    email: EmailStr
    password: str

class ContractorRegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_self_employed: bool

class UserLoginRequest(BaseModel):
    full_name: str
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
    # В БД поле называется company_id, а в JSON ответе должно быть company
    company: int | None = Field(default=None, validation_alias="company_id", serialization_alias="company")
    is_self_employed: bool

    model_config = {"from_attributes": True}