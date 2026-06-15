from fastapi import APIRouter, Depends, status, Response
from schemas.user import (
    CompanyRegisterRequest, ContractorRegisterRequest,
    UserLoginRequest, TokenResponse, UserResponse
)
from services.auth_service import AuthService
from api.dependencies import get_auth_service, get_current_user
from models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register_company(
    request: CompanyRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    await auth_service.register_company(request)
    return Response(status_code=status.HTTP_201_CREATED) # Ничего не возвращает, как просили

@router.post("/register-contractor/", status_code=status.HTTP_201_CREATED)
async def register_contractor(
    request: ContractorRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    await auth_service.register_contractor(request)
    return Response(status_code=status.HTTP_201_CREATED)

@router.post("/login/", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login_user(
    request: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.login(request)

@router.get("/me/", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user