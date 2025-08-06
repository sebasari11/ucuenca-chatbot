from fastapi import APIRouter
from app.src.users.models import User


router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok"}



