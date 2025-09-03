# auth/controller.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database.core import get_db
from . import service, models
import logging
import time

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)
logger = logging.getLogger("uvicorn")


@router.post("/login", response_model=models.TokenResponse)
async def login_user(
    request: models.LoginRequest,   # 👈 JSON body instead of form-data
    db: Session = Depends(get_db),
):
    """
    Login endpoint using JSON body.
    Accepts 'username' and 'password' in JSON.
    Returns access token and user details.
    """
    start_time = time.perf_counter()

    # Authenticate using JSON
    user = await service.authenticate_user(db, request.username, request.password)
    if not user:
        return models.TokenResponse(success=False, message="Invalid credentials", data=None)

    # Create JWT token
    token, expires_at, user = service.create_jwt(user, expires_in_minutes=100)

    # Handle UC codes for non-admin users
    if user['usertype'] not in [1, 2, 3, 4, 11, 12]:
        try:
            user['user_ucs'] = list(dict.fromkeys(user['user_ucs'].split(', ')))
        except (AttributeError, KeyError, TypeError):
            user['user_ucs'] = []

        try:
            value_uc = await service.get_user_uc_codes(user['idusers'], db)
            user['uc_codes'] = value_uc['uc_codes']
        except (AttributeError, KeyError, TypeError):
            user['uc_codes'] = []

    duration = time.perf_counter() - start_time
    logger.info(f"Login completed in {duration:.4f}s")

    # Sanitize before returning
    user = await service.sanitize_user_payload(user)
    data = {"access_token": token, "users": user, "expires_in": expires_at}

    return models.TokenResponse(success=True, message="Login successful", data=data)

