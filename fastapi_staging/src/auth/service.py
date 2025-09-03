# from datetime import timedelta, datetime, timezone
# from typing import Annotated
# from uuid import UUID, uuid4
# from fastapi import Depends
# from passlib.context import CryptContext
# import jwt
# from jwt import PyJWTError
# from sqlalchemy.orm import Session
# from src.entities.user import User
# from . import models
# from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
# from ..exceptions import AuthenticationError
# import logging
#
# # You would want to store this in an environment variable or a secret manager
# SECRET_KEY = '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3'
# ALGORITHM = 'HS256'
# ACCESS_TOKEN_EXPIRE_MINUTES = 30
#
# oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
# bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
#
# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return bcrypt_context.verify(plain_password, hashed_password)
#
#
# def get_password_hash(password: str) -> str:
#     return bcrypt_context.hash(password)
#
#
# def authenticate_user(email: str, password: str, db: Session) -> User | bool:
#     user = db.query(User).filter(User.email == email).first()
#     if not user or not verify_password(password, user.password_hash):
#         logging.warning(f"Failed authentication attempt for email: {email}")
#         return False
#     return user
#
#
# def create_access_token(email: str, user_id: UUID, expires_delta: timedelta) -> str:
#     encode = {
#         'sub': email,
#         'id': str(user_id),
#         'exp': datetime.now(timezone.utc) + expires_delta
#     }
#     return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
#
#
# def verify_token(token: str) -> models.TokenData:
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id: str = payload.get('id')
#         return models.TokenData(user_id=user_id)
#     except PyJWTError as e:
#         logging.warning(f"Token verification failed: {str(e)}")
#         raise AuthenticationError()
#
#
# def register_user(db: Session, register_user_request: models.RegisterUserRequest) -> None:
#     try:
#         create_user_model = User(
#             id=uuid4(),
#             email=register_user_request.email,
#             first_name=register_user_request.first_name,
#             last_name=register_user_request.last_name,
#             password_hash=get_password_hash(register_user_request.password)
#         )
#         db.add(create_user_model)
#         db.commit()
#     except Exception as e:
#         logging.error(f"Failed to register user: {register_user_request.email}. Error: {str(e)}")
#         raise
#
#
# def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]) -> models.TokenData:
#     return verify_token(token)
#
# CurrentUser = Annotated[models.TokenData, Depends(get_current_user)]
#
#
# def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
#                                  db: Session) -> models.Token:
#     user = authenticate_user(form_data.username, form_data.password, db)
#     if not user:
#         raise AuthenticationError()
#     token = create_access_token(user.email, user.id, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     return models.Token(access_token=token, token_type='bearer')


# auth/service.py
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
import jwt
from src.encryption_cryptography import hash
bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30


async def sanitize_user_payload(payload: dict) -> dict:
    """
    Asynchronously remove sensitive password-related fields from the 'users' object in the payload.
    """
    sensitive_keys = {
        "password",
        "mot_de_passe",
        "final_password",
        "password_hash",
        "password_style_de_passe"
    }

    for key in sensitive_keys:
        payload.pop(key, None)

    return payload


async def authenticate_user(db: AsyncSession, username: str, password: str):
    query = text("""SELECT u.*,
                           t.name AS role,
                           t.code AS role_code,
                           s.name AS office,

                           -- Province name from location table where type = 2
                           prov.name                                             AS province_name,

                           -- Division name from clean_divisions table
                           divs.division                                         AS division_name,

                           -- District full name from district table
                           d.full_name                                           AS district_name,

                           -- Tehsil name from location table (type = 4 and status = 1)
                           tehsil.name                                           AS tehsil_name,

                           -- Aggregated UC names and codes
                           STRING_AGG(loc.name || ' (' || loc.code || ')', ', ') AS user_ucs

                    FROM users u

-- User role
                             LEFT JOIN user_roles t ON u.usertype = t.idrole

-- Support office
                             LEFT JOIN support_office s ON u.idoffice = s.idoffice

-- Province (from idoffice match with location.type = 2)
                             LEFT JOIN location prov ON prov.code = u.idoffice AND prov.type = 2 AND prov.status = 1

-- Division (from division_code match with clean_divisions.divid)
                             LEFT JOIN clean_divisions divs ON divs.divid = u.division_code

-- District (from district_code match with district.code)
                             LEFT JOIN district d ON d.code = u.district_code

-- Tehsil (from tehsil_code match with location.code, type = 4 and status = 1)
                             LEFT JOIN location tehsil
                                       ON tehsil.code = u.tehsil_code AND tehsil.type = 4 AND tehsil.status = 1

-- UC info from user_locations and location
                             LEFT JOIN user_locations ul ON ul.idusers = u.idusers
                             LEFT JOIN location loc ON loc.code = ul.uc_code

                    WHERE u.username = :username
                      AND u.ishide = 0
                      AND u.status = 1

                    GROUP BY u.idusers,
                             t.name,
                             t.code,
                             s.name,
                             prov.name,
                             divs.division,
                             d.full_name,
                             tehsil.name LIMIT 1;""")
    result = await db.execute(query, {"username": username})
    user = result.fetchone()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid UserName. Try Again !!!")

    # if not bcrypt.verify(password, user.password_hash):
    #     raise HTTPException(status_code=401, detail="Invalid password")
    latest_hash = await hash.create_password_hash(password)
    print(latest_hash)
    if user.password_hash != latest_hash:
        raise HTTPException(status_code=401, detail="Invalid Password. Try Again !!!")


    return user


async def get_user_uc_codes(user_id: int, db: AsyncSession):
    query = text("""
                 SELECT STRING_AGG(ul.uc_code::TEXT, ',') AS uc_codes
                 FROM user_locations ul
                          JOIN users u ON u.idusers = ul.idusers
                 WHERE u.status = 1
                   AND u.idusers = :user_id
                 """)

    result = await db.execute(query, {"user_id": user_id})
    row = result.fetchone()

    if not row or not row.uc_codes:
        raise HTTPException(status_code=404, detail="UC codes not found for this user.")

    return {"user_id": user_id, "uc_codes": row.uc_codes.split(',')}


def create_jwt(user, expires_in_minutes=2):
    exp_datetime = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
    exp_timestamp = int(exp_datetime.timestamp())  # <-- UNIX timestamp
    payload = {
        "sub": user.username,
        "user_id": str(user.idusers),
        "uid": user.usertype,
        "role": user.role,
        "is_admin": user.usertype == 1,
        "is_province_admin": int(user.usertype == 3 and user.is_admin == 1),
        "is_district_admin": int(user.usertype == 4 and user.is_admin == 1),
        "is_division_admin": int(user.usertype == 11 and user.is_admin == 1),
        "is_tehsil_admin": int(user.usertype == 12 and user.is_admin == 1),
        "is_oc": int(user.usertype == 4),
        "is_pmc": user.pmc,
        "district_code": user.district_code,
        "tehsil_code": user.tehsil_code,
        "division_code": user.division_code,
        "uc_code": user.uc_code,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    users = dict(user._mapping)
    users.update({k: v for k, v in payload.items() if
                  k in ["is_admin", "is_province_admin", "is_district_admin", "is_tehsil_admin", "is_division_admin",
                        "is_oc", "is_pmc", "district_code",
                        "division_code", "tehsil_code", "uc_code"]},
                 uc_codes=[users["uc_code"]] if users["uc_code"] else [])

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM), exp_timestamp, users
