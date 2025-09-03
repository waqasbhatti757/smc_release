from fastapi import APIRouter, Depends, Request, HTTPException
from starlette import status
from src.auth import models, service
from fastapi.security import OAuth2PasswordRequestForm
from src.database.core import DbSession
from src.models import UserPayload,VerificationRequest, VerificationResponse,UserCheckResponse,UserCheckRequest,Payload
import logging
from src.rate_limiter import limiter
import time
from src.service import LocationService
from sqlalchemy.exc import SQLAlchemyError
from src.service import NameVerificationService
from src.models import UserCreate,TokenUserRequest
from src.service import create_user,insert_user_locations,update_user,get_user_profile_session_info,get_users,get_detail_user_info
from src.models import FullUserUpdate
from src.service import full_update_user
router = APIRouter(
    prefix='/users',
    tags=['users']
)
logger = logging.getLogger("uvicorn")


@router.post("/user/locations")
async def get_user_locations(db:DbSession, payload: UserPayload):
    try:
        data = await LocationService.get_locations_for_user(db,payload)
        return {"status": "Success", "data": data}

    except SQLAlchemyError as db_error:
        logger.error(f"Database error in /user/locations: {db_error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred. Please try again later."
        )

    except ValueError as ve:
        logger.warning(f"Value error in /user/locations: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )

    except Exception as ex:
        logger.exception(f"Unhandled error in /user/locations: {ex}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please contact support."
        )


@router.get("/province/{province_code}/divisions")
async def get_divisions_by_province(province_code:int, db: DbSession):
    try:
        divisions = await LocationService.get_divisions_by_province(db, province_code)
        return {"status": "Success", "data": divisions}

    except SQLAlchemyError as db_error:
        logger.error(f"Database error in /province/{province_code}/divisions: {db_error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred. Please try again later."
        )

    except ValueError as ve:
        logger.warning(f"Value error in /province/{province_code}/divisions: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )

    except Exception as ex:
        logger.exception(f"Unhandled error in /province/{province_code}/divisions: {ex}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please contact support."
        )


@router.get("/division/{division_code}/district")
async def get_districts_by_division(division_code:int, db: DbSession):
    try:
        districts = await LocationService.get_districts_by_division(db, division_code)
        return {"status": "Success", "data": districts}

    except SQLAlchemyError as db_error:
        logger.error(f"Database error in /division/{division_code}/districts: {db_error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred. Please try again later."
        )

    except ValueError as ve:
        logger.warning(f"Value error in /division/{division_code}/districts: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )

    except Exception as ex:
        logger.exception(f"Unhandled error in /division/{division_code}/districts: {ex}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please contact support."
        )


@router.get("/district/{district_code}/tehsil")
async def get_tehsil_by_districts(district_code:int, db: DbSession):
    try:
        districts = await LocationService.get_tehsil_by_district(db, district_code)
        return {"status": "Success", "data": districts}

    except SQLAlchemyError as db_error:
        logger.error(f"Database error in /district/{district_code}/tehsils: {db_error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred. Please try again later."
        )

    except ValueError as ve:
        logger.warning(f"Value error in /district/{district_code}/tehsils: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )

    except Exception as ex:
        logger.exception(f"Unhandled error in /district/{district_code}/tehsils: {ex}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please contact support."
        )


@router.get("/tehsil/{tehsil_code}/ucs")
async def get_ucs_by_tehsil(tehsil_code:int, db: DbSession):
    try:
        districts = await LocationService.get_ucs_by_tehsil(db, tehsil_code)
        return {"status": "Success", "data": districts}

    except SQLAlchemyError as db_error:
        logger.error(f"Database error in /tehsil/{tehsil_code}/ucs: {db_error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred. Please try again later."
        )

    except ValueError as ve:
        logger.warning(f"Value error in /tehsil/{tehsil_code}/ucs: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )

    except Exception as ex:
        logger.exception(f"Unhandled error in /tehsil/{tehsil_code}/ucs: {ex}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please contact support."
        )



@router.post("/find_anomaly_name", response_model=VerificationResponse)
async def verify_name(request: VerificationRequest,db: DbSession ) -> VerificationResponse:
    is_valid = await NameVerificationService.is_name_verified(db, request.text)
    return VerificationResponse(verified=is_valid)


@router.post("/check-username-or-email", response_model=UserCheckResponse)
async def check_user_or_email(request: UserCheckRequest, db: DbSession) -> UserCheckResponse:
    is_found = await NameVerificationService.check_user_or_email(db, request.value)
    return UserCheckResponse(already_exists=is_found)


@router.post("/createusers")
async def add_user(user: UserCreate, db: DbSession):
    try:

        result = await create_user(db, user)
        print(user)
        if user.userrole == 5:
            await insert_user_locations(db, result["idusers"], user)

        return result
    except Exception as e:
        print(e)
        # Log the exception with some context
        # You can customize the error message or just return the exception string
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user"
        )


@router.post("/updateuser")
async def update_user_endpoint(user: UserCreate, db: DbSession):
    try:
        print(user)
        result = await update_user(db, user)
        print(result)
        result['success'] = True
        return result

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user"
        )


@router.post("/resetsessionuserinfo")
async def update_user_endpoint(user: TokenUserRequest, db: DbSession):
    try:
        result = await get_user_profile_session_info(db, user)
        return result

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get user information"
        )

@router.post("/getuserbasicinfo")
async def read_users(payload: Payload, db: DbSession):
    users = await get_users(db, payload)
    return {"users": users}



@router.post("/profile_detail")
async def read_users(userinfo: TokenUserRequest, db: DbSession):
    users = await get_detail_user_info(db, userinfo)
    return {"users": users}


@router.post("/reupdate_user_info")
async def reupdate_user_info(userinfo: FullUserUpdate, db: DbSession):
    try:
        result = await full_update_user(db, userinfo)
        if userinfo.userrole == 5:
            await insert_user_locations(db, userinfo.idusers, userinfo)
        return result
    except Exception as e:
        print(e)
        # Log the exception with some context
        # You can customize the error message or just return the exception string
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user"
        )

