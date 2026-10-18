from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from schemas.auth import LoginRequest
from services.auth_service import login_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
async def login(data: LoginRequest, db=Depends(get_db)):
    return await login_service(data, db)
