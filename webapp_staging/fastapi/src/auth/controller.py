from typing_extensions import Annotated
from fastapi import APIRouter, Depends, Request
from starlette import status
from src.auth import models
from src.auth import service
from fastapi.security import OAuth2PasswordRequestForm
from src.database.core import DbSession
import logging
from src.rate_limiter import limiter
import time
router = APIRouter(
    prefix='/auth',
    tags=['auth']
)
logger = logging.getLogger("uvicorn")


@router.post("/login", response_model=models.TokenResponse)
async def login_user(data: models.LoginRequest, db: DbSession):
    start_time = time.perf_counter()
    user = await service.authenticate_user(db, data.username, data.password)
    # token = service.create_jwt(user)
    token, expires_at,user = service.create_jwt(user, expires_in_minutes=100)
    if user['usertype'] not in [1,2,3,4,11,12]:
        try:
            # user['user_ucs'] = user['user_ucs'].split(', ')
            user['user_ucs'] = list(dict.fromkeys(user['user_ucs'].split(', ')))
        except (AttributeError, KeyError, TypeError):
            user['user_ucs'] = []

        try:
            value_uc = await service.get_user_uc_codes(user['idusers'], db)
            user['uc_codes'] = value_uc['uc_codes']
        except (AttributeError, KeyError, TypeError):
            user['uc_codes'] = []

    duration = time.perf_counter() - start_time
    logger.info(f"Completed in {duration:.4f}s")
    user = await service.sanitize_user_payload(user)
    data={"access_token": token, "users": user, "expires_in": expires_at}
    return models.TokenResponse(success=True, message = "Login successful",data=data)
    # return models.TokenResponse(access_token=token,users=dict(user._mapping), expires_in=expires_at)


# @router.post("/", status_code=status.HTTP_201_CREATED)
# @limiter.limit("5/hour")
# async def register_user(request: Request, db: DbSession,
#                       register_user_request: models.RegisterUserRequest):
#     service.register_user(db, register_user_request)
#
#
# @router.post("/token", response_model=models.Token)
# async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
#                                  db: DbSession):
#     return service.login_for_access_token(form_data, db)







