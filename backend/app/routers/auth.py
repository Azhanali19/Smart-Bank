from fastapi import APIRouter, HTTPException
from ..schemas import UserCreate, Login, Token
from .. import crud
from ..utils import create_access_token
from datetime import timedelta
from ..config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=dict)
async def register(user: UserCreate):
    created = await crud.create_user(user.dict())
    if not created:
        raise HTTPException(status_code=400, detail="User with email exists")
    return {"msg": "user created", "user": created}

@router.post("/login", response_model=Token)
async def login(payload: Login):
    user = await crud.authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user["id"], "email": user["email"], "role": user["role"]}, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": token}