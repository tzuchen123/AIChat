from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import get_db
from src.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from src.schemas.common import StandardResponse
from src.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=StandardResponse[UserResponse],
    status_code=201,
)
async def register(
    body: RegisterRequest, db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    user = await service.register(body.username, body.email, body.password)
    return StandardResponse.ok(user)


@router.post("/login", response_model=StandardResponse[TokenResponse])
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    token = await service.login(body.email, body.password)
    return StandardResponse.ok(token)
