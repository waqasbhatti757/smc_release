from uuid import UUID
from pydantic import BaseModel, EmailStr
from typing import Optional



class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    success: bool
    message: str
    data: dict


# class TokenResponse(BaseModel):
#     access_token: str
#     token_type: str = "bearer"
#     users: dict  # raw user dict from SQLAlchemy `fetchone()._mapping`
#     expires_in: int


# class RegisterUserRequest(BaseModel):
#     email: EmailStr
#     first_name: str
#     last_name: str
#     password: str
#
# class Token(BaseModel):
#     access_token: str
#     token_type: str
#
# class TokenData(BaseModel):
#     user_id: str | None = None
#
#     def get_uuid(self) -> UUID | None:
#         if self.user_id:
#             return UUID(self.user_id)
#         return None