from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserPayload(BaseModel):
    usertype: int
    device_type: int
    jwt_token: str
    province_code: Optional[int] = None
    division_code: Optional[int] = None
    district_code: Optional[int] = None
    tehsil_code: Optional[int] = None


class DivisionPayload(BaseModel):
    province_code: Optional[int] = None

class DistrictPayload(BaseModel):
    division_code: Optional[int] = None

class TehsilPayload(BaseModel):
    district_code: Optional[int] = None

class UCPayload(BaseModel):
    tehsil_code: Optional[int] = None

class VerificationRequest(BaseModel):
    text: str

class VerificationResponse(BaseModel):
    verified: bool

class UserCheckRequest(BaseModel):
    value: str

class UserCheckResponse(BaseModel):
    already_exists: bool


class UserCreate(BaseModel):
    is_admin: int
    provincename: Optional[int] = None
    firstname: str
    dob: Optional[str] = None  # you can use date if you want, adjust format accordingly
    affiliation: Optional[str] = None
    address: Optional[str] = None
    gender: Optional[str] = None
    accountstatus: Optional[str] = None
    username: str
    cnic: Optional[str] = None
    designation: Optional[str] = None
    districtname: Optional[int] = None
    userrole: Optional[int] = None
    userentry: Optional[str] = None
    tehsilname: Optional[int] = None
    password: Optional[str] = None
    lastname: str
    created_by: Optional[int] = None
    email: Optional[EmailStr] = None
    divisionname: Optional[int] = None
    contactnumber: Optional[str] = None
    ucname: Optional[list] = None  # If you want to include it, otherwise ignore


class TokenUserRequest(BaseModel):
    jwt_token: str
    user_id: int

class Payload(BaseModel):
    limit: int = Field(40, ge=1, le=5000, description="Number of records to return")
    offset: int = Field(0, ge=0, description="Number of records to skip")
    user_id: int
    userrole: Optional[int] = None
    provincename: Optional[int] = None
    divisionname: Optional[int] = None
    districtname: Optional[int] = None
    tehsilname: Optional[int] = None
    affiliation: Optional[str] = None
    isadmin: Optional[int] = None
    statuses: Optional[int] = None
    gender: Optional[str] = None
    userentry: Optional[str] = None




class FullUserUpdate(BaseModel):
    is_admin: int
    provincename: Optional[int] = None
    firstname: str
    dob: Optional[str] = None  # you can use date if you want, adjust format accordingly
    affiliation: Optional[str] = None
    address: Optional[str] = None
    gender: Optional[str] = None
    accountstatus: Optional[str] = None
    username: str
    cnic: str
    designation: Optional[str] = None
    districtname: Optional[int] = None
    userrole: Optional[int] = None
    userentry: Optional[str] = None
    tehsilname: Optional[int] = None
    password: Optional[str] = None
    lastname: str
    created_by: Optional[int] = None
    email: Optional[EmailStr] = None
    divisionname: Optional[int] = None
    contactnumber: Optional[str] = None
    ucname: Optional[list] = None  # If you want to include it, otherwise ignore
    idusers: Optional[int] = None