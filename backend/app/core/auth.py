from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ── Business auth ────────────────────────────────────────────────────────────

async def get_current_business(token: str = Depends(oauth2_scheme)):
    """Validates JWT and returns the authenticated Business. Rejects staff tokens."""
    from app.models.business import Business

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik doğrulanamadı",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_type: str = payload.get("type", "business")
        if token_type != "business":
            raise credentials_exception
        business_id: str = payload.get("sub")
        if business_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    business = await Business.get(business_id)
    if business is None:
        raise credentials_exception
    return business


# Backward-compatible alias used by existing routers before rename
get_current_user = get_current_business


# ── Staff auth ───────────────────────────────────────────────────────────────

async def get_current_staff(token: str = Depends(oauth2_scheme)):
    """Validates JWT and returns the authenticated StaffMember. Rejects business tokens."""
    from app.models.staff_member import StaffMember

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik doğrulanamadı",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_type: str = payload.get("type")
        if token_type != "staff":
            raise credentials_exception
        staff_id: str = payload.get("sub")
        if staff_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    staff = await StaffMember.get(staff_id)
    if staff is None or not staff.is_active:
        raise credentials_exception
    return staff


# ── Actor context (accepts both business and staff tokens) ───────────────────

class ActorContext(BaseModel):
    actor_type: str          # "business" | "staff"
    business_id: str
    business: object         # Business document
    staff_id: Optional[str] = None
    staff_member: object = None  # StaffMember document or None

    model_config = {"arbitrary_types_allowed": True}


async def get_current_actor(token: str = Depends(oauth2_scheme)) -> ActorContext:
    """Accepts both business and staff tokens. Returns an ActorContext."""
    from app.models.business import Business
    from app.models.staff_member import StaffMember

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik doğrulanamadı",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise credentials_exception

    token_type: str = payload.get("type", "business")

    if token_type == "staff":
        staff_id: str = payload.get("sub")
        business_id: str = payload.get("business_id")
        if not staff_id or not business_id:
            raise credentials_exception

        staff = await StaffMember.get(staff_id)
        if staff is None or not staff.is_active:
            raise credentials_exception

        business = await Business.get(business_id)
        if business is None:
            raise credentials_exception

        return ActorContext(
            actor_type="staff",
            business_id=business_id,
            business=business,
            staff_id=staff_id,
            staff_member=staff,
        )
    else:
        business_id = payload.get("sub")
        if business_id is None:
            raise credentials_exception

        business = await Business.get(business_id)
        if business is None:
            raise credentials_exception

        return ActorContext(
            actor_type="business",
            business_id=str(business.id),
            business=business,
        )

