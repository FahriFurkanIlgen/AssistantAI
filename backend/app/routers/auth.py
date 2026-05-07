"""
Auth Router - Business registration and login.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from datetime import datetime

from app.models.business import Business
from app.core.security import hash_password, verify_password
from app.core.auth import create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    name: str
    slug: str
    email: EmailStr
    password: str
    sector: str = "tattoo"
    phone: str | None = None
    city: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    business_id: str
    business_name: str
    slug: str


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest):
    # Check unique email
    if await Business.find_one(Business.email == req.email):
        raise HTTPException(status_code=400, detail="Bu e-posta adresi zaten kayıtlı")
    # Check unique slug
    if await Business.find_one(Business.slug == req.slug):
        raise HTTPException(status_code=400, detail="Bu URL adı zaten kullanılıyor")

    business = Business(
        name=req.name,
        slug=req.slug.lower().strip(),
        email=req.email,
        hashed_password=hash_password(req.password),
        sector=req.sector,
        phone=req.phone,
        city=req.city,
    )
    await business.insert()

    token = create_access_token({"sub": str(business.id)})
    return TokenResponse(
        access_token=token,
        business_id=str(business.id),
        business_name=business.name,
        slug=business.slug,
    )


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    business = await Business.find_one(Business.email == form_data.username)
    if not business or not verify_password(form_data.password, business.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-posta veya şifre hatalı",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": str(business.id)})
    return TokenResponse(
        access_token=token,
        business_id=str(business.id),
        business_name=business.name,
        slug=business.slug,
    )


@router.get("/me")
async def me(current_business: Business = Depends(get_current_user)):
    return {
        "id": str(current_business.id),
        "name": current_business.name,
        "slug": current_business.slug,
        "email": current_business.email,
        "sector": current_business.sector,
        "google_connected": current_business.google_refresh_token is not None,
    }
