from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.models.user import User


router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.get("/me")
async def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
    }
