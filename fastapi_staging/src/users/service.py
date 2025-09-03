from sqlalchemy import select, update
from typing import List, Dict, Any
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
import traceback
from .models import UserPayload
from .db_logic_model.location_models import LocationModel
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
import jwt
from sqlalchemy import text
from src.encryption_cryptography import hash
from fastapi import HTTPException, status
import re
from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


class LocationService:
    @staticmethod
    async def get_locations_for_user(db: AsyncSession, payload: UserPayload) -> Dict:
        usertype = payload.usertype
        result = {}

        if usertype in [1, 2]:  # Super or Province Admin
            result["Provinces"] = await LocationModel.get_provinces(db)

        if usertype in [3]:  # Super or Province Admin
            result["Divisions"] = await LocationModel.get_divisions(db, payload.province_code)

        if usertype in [11] and payload.division_code:
            result["Districts"] = await LocationModel.get_districts(db, payload.division_code)

        if usertype == [4, 12] and payload.district_code:
            result["Tehsils"] = await LocationModel.get_tehsils(db, payload.district_code)

        return result

    @staticmethod
    async def get_divisions_by_province(db: AsyncSession, province_code: int):
        if province_code is None:
            raise ValueError("Province code is required.")

        divisions = await LocationModel.get_divisions_by_province(db, province_code)
        return divisions

    @staticmethod
    async def get_districts_by_division(db: AsyncSession, division_code: int):
        if division_code is None:
            raise ValueError("division_code is required.")

        divisions = await LocationModel.get_districts_by_division(db, division_code)
        return divisions

    @staticmethod
    async def get_tehsil_by_district(db: AsyncSession, district_code: int):
        if district_code is None:
            raise ValueError("district_code is required.")

        divisions = await LocationModel.get_tehsil_by_district(db, district_code)
        return divisions

    @staticmethod
    async def get_ucs_by_tehsil(db: AsyncSession, tehsil_code: int):
        if tehsil_code is None:
            raise ValueError("tehsil_code is required.")

        divisions = await LocationModel.get_ucs_by_tehsil(db, tehsil_code)
        return divisions


class NameVerificationService:
    @staticmethod
    def extract_text_and_number(payload: str) -> Tuple[str, str]:
        """
        Extracts the alphabetic and numeric parts from the given input string.
        Numbers less than 3 digits are ignored.
        """
        text_part = ''.join(re.findall(r'[A-Za-z]+', payload))
        numbers = ''.join(re.findall(r'\d+', payload))
        number_part = numbers if len(numbers) >= 3 else ""
        return text_part, number_part

    @staticmethod
    async def is_name_verified(db: AsyncSession, payload: str) -> bool:
        """
        Checks if the given payload matches any record in the `name_verification` table.
        Matching is done using ILIKE for both text and numeric parts.
        """
        text_part, number_part = NameVerificationService.extract_text_and_number(payload)

        conditions = []
        parameters = {}

        if text_part:
            conditions.append("(code ILIKE :text OR location_name ILIKE :text)")
            parameters["text"] = f"%{text_part}%"

        if number_part:
            conditions.append("(code ILIKE :number OR location_name ILIKE :number)")
            parameters["number"] = f"%{number_part}%"

        if not conditions:
            return False

        where_clause = " OR ".join(conditions)
        query = text(f"""
            SELECT 1
            FROM name_verification
            WHERE {where_clause}
            LIMIT 1
        """)

        result = await db.execute(query, parameters)
        return result.first() is not None

    @staticmethod
    async def check_user_or_email(db: AsyncSession, value: str) -> bool:
        query = text("""
                     SELECT 1
                     FROM users
                     WHERE username = :value
                        OR email = :value LIMIT 1
                     """)
        result = await db.execute(query, {"value": value})
        return result.first() is not None


async def create_user(db: AsyncSession, user_data):
    # query = text("""
    #              SELECT 1
    #              FROM users
    #              WHERE username = :username
    #                 OR email = :email
    #                 OR cnic = :cnic LIMIT 1
    #              """)
    #
    # result = await db.execute(query, {
    #     "username": user_data.username,
    #     "email": user_data.email
    # })
    #
    # exists = result.scalar_one_or_none() is not None
    #
    # if exists:
    #     raise HTTPException(
    #         status_code=status.HTTP_409_CONFLICT,
    #         detail="User with the given username, email, or CNIC already exists."
    #     )
    # # Map accountstatus to is_active (1 for Active else 0)
    is_active = 1 if (user_data.accountstatus and user_data.accountstatus.lower() == 'active') else 0

    # Hash password

    password_hash = await hash.create_password_hash(user_data.password)
    password_style_de_passe = await hash.style_password(user_data.password)
    # Prepare SQL insert query (adjust column names)
    query = text("""
                 INSERT INTO users (is_first_time_login,
                                    createddate,
                                    is_admin,
                                    idoffice,
                                    first_name,
                                    affiliation,
                                    current_address,
                                    genderval,
                                    is_active,
                                    status,
                                    createdby,
                                    username,
                                    designation,
                                    district_code,
                                    usertype,
                                    entrypermission,
                                    tehsil_code,
                                    password_hash,
                                    password_style_de_passe,
                                    last_name,
                                    email,
                                    division_code,
                                    mobile,
                                    updatedby,
                                    updateddate)
                 VALUES (:is_first_time_login,
                         :createddate,
                         :is_admin,
                         :idoffice,
                         :first_name,
                         :affiliation,
                         :current_address,
                         :genderval,
                         :is_active,
                         :status,
                         :createdby,
                         :username,
                         :designation,
                         :district_code,
                         :usertype,
                         :entrypermission,
                         :tehsil_code,
                         :password_hash,
                         :password_style_de_passe,
                         :last_name,
                         :email,
                         :division_code,
                         :mobile,
                         :updatedby,
                         :updateddate) RETURNING idusers """)

    params = {
        "is_first_time_login": 1,
        "createddate": datetime.utcnow(),
        "is_admin": user_data.is_admin,
        "idoffice": user_data.provincename,
        "first_name": user_data.firstname,
        "affiliation": user_data.affiliation,
        "current_address": user_data.address,
        "genderval": user_data.gender,
        "is_active": is_active,
        "status": is_active,
        "createdby": user_data.created_by,
        "username": user_data.username,
        "designation": user_data.designation,
        "district_code": user_data.districtname,
        "usertype": user_data.userrole,
        "entrypermission": user_data.userentry,
        "tehsil_code": user_data.tehsilname,
        "password_hash": password_hash,
        "password_style_de_passe": password_style_de_passe,
        "last_name": user_data.lastname,
        "email": user_data.email,
        "division_code": user_data.divisionname,
        "mobile": user_data.contactnumber,
        "updatedby": user_data.created_by,
        "updateddate": datetime.utcnow(),
    }
    try:
        result = await db.execute(query, params)
        new_id = result.scalar_one()  # gets the single idusers value returned
        await db.commit()
        return {"message": "User created successfully", 'idusers': new_id}
    except IntegrityError as e:
        await db.rollback()
        # Detect duplicate user or constraint violation here
        raise Exception("User already exists or integrity error: " + str(e))

    except Exception as e:
        await db.rollback()
        raise


async def insert_user_locations(db: AsyncSession, user_id: int, user_data):
    # locations is a list of dicts, each dict has tehsil_code, uc_code, province_code, district_code
    delete_query = text("DELETE FROM user_locations WHERE idusers = :idusers")
    await db.execute(delete_query, {"idusers": user_id})

    insert_query = text("""
                        INSERT INTO user_locations (idusers, tehsil_code, uc_code, province_code, district_code)
                        VALUES (:idusers, :tehsil_code, :uc_code, :province_code, :district_code)
                        """)

    for loc in user_data.ucname:
        print(loc)
        params = {
            "idusers": user_id,
            "tehsil_code": int(user_data.tehsilname),
            "uc_code": int(loc),
            "province_code": int(user_data.provincename),
            "district_code": int(user_data.districtname),
        }
        await db.execute(insert_query, params)
    await db.commit()


async def update_user(db: AsyncSession, user_data):
    login_val = 0

    # Start building your base update query and params dict
    base_query = """
                 UPDATE users
                 SET username            = :username,
                     first_name          = :first_name,
                     last_name           = :last_name,
                     genderval           = :genderval,
                     email               = :email,
                     mobile              = :mobile,
                     affiliation         = :affiliation,
                     designation         = :designation,
                     current_address     = :current_address,
                     updatedby           = :updatedby,
                     updateddate         = :updateddate,
                     is_first_time_login = :is_first_time_login \
                 """

    params = {
        "username": user_data.username,
        "first_name": user_data.firstname,
        "last_name": user_data.lastname,
        "genderval": user_data.gender,
        "email": user_data.email,
        "mobile": user_data.contactnumber,
        "affiliation": user_data.affiliation,
        "designation": user_data.designation,
        "current_address": user_data.address,
        "updatedby": user_data.created_by,
        "updateddate": datetime.utcnow(),
        "is_first_time_login": login_val,
        "idusers": user_data.created_by,
    }

    # Conditionally add password fields if password is provided
    if user_data.password is not None:
        password_hash = await hash.create_password_hash(user_data.password)
        password_style_de_passe = await hash.style_password(user_data.password)
        base_query += """,
            password_hash = :password_hash,
            password_style_de_passe = :password_style_de_passe
        """
        params["password_hash"] = password_hash
        params["password_style_de_passe"] = password_style_de_passe

    base_query += """
        WHERE idusers = :idusers
        RETURNING idusers
    """

    query = text(base_query)

    try:
        result = await db.execute(query, params)
        updated_id = result.scalar_one_or_none()
        await db.commit()

        if updated_id:
            return {"message": "User updated successfully", "idusers": updated_id}
        else:
            return {"message": "No user found with the given ID", "idusers": None}

    except IntegrityError as e:
        await db.rollback()
        raise Exception("User update failed due to integrity error: " + str(e))

    except Exception as e:
        await db.rollback()
        raise


async def get_user_profile_session_info(db: AsyncSession, payload):
    query = text("""
                 SELECT username,
                        first_name,
                        last_name,
                        genderval,
                        email,
                        password_hash,
                        password_style_de_passe,
                        cnic,
                        cnicexpiry,
                        mobile,
                        affiliation,
                        designation,
                        current_address,
                        updatedby,
                        updateddate,
                        is_first_time_login
                 FROM users
                 WHERE idusers = :idusers
                 """)

    result = await db.execute(query, {"idusers": payload.user_id})
    user_data = result.mappings().first()

    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "status": "success",
        "user": dict(user_data)
    }



def build_filter_conditions(payload) -> (str, Dict[str, Any]):
    conditions = [
        "(:current_id IN (1, 2) OR (:current_id = 3 AND u.usertype IN (3, 4, 5, 11, 12)) OR "
        "(:current_id = 11 AND u.usertype IN (11, 4, 5, 12)) OR (:current_id = 12 AND u.usertype IN (12, 5)) OR "
        "(:current_id = 4 AND u.usertype IN (5, 12)))"
    ]
    params = {"current_id": payload.user_id}

    if payload.userrole is not None:
        conditions.append("u.usertype = :userrole")
        params["userrole"] = payload.userrole
    if payload.provincename is not None:
        conditions.append("u.idoffice = :provincename")
        params["provincename"] = payload.provincename
    if payload.divisionname is not None:
        conditions.append("u.division_code = :divisionname")
        params["divisionname"] = payload.divisionname
    if payload.districtname is not None:
        conditions.append("u.district_code = :districtname")
        params["districtname"] = payload.districtname
    if payload.tehsilname is not None:
        conditions.append("u.tehsil_code = :tehsilname")
        params["tehsilname"] = payload.tehsilname
    if payload.statuses is not None:
        conditions.append("u.status = :statuses")
        params["statuses"] = payload.statuses
    if payload.gender is not None:
        conditions.append("u.genderval = :gender")
        params["gender"] = payload.gender
    if payload.affiliation is not None:
        conditions.append("u.affiliation = :affiliation")
        params["affiliation"] = payload.affiliation
    if payload.userentry is not None:
        conditions.append("u.entrypermission = :userentry")
        params["userentry"] = payload.userentry

    if payload.isadmin is not None:
        conditions.append("u.is_admin = :isadmin")
        params["isadmin"] = payload.isadmin

    where_clause = " AND ".join(conditions)
    return where_clause, params


async def get_users(db: AsyncSession, payload) -> Dict[str, Any]:
    where_clause, params = build_filter_conditions(payload)
    data_query = text(f"""
                      WITH prov AS (SELECT code, name
                    FROM location
                    WHERE type = 2
                      AND status = 1),
                    divs AS (SELECT DISTINCT
                    ON (divid, provid) divid, provid, division
                    FROM clean_divisions
                    ), dist AS (
                    SELECT l.code, l.dname
                    FROM district d
                    JOIN location l
                    ON l.code = d.code AND l.status = 1
                    GROUP BY l.code, l.dname
                    ),
                    tehsil AS (
                    SELECT l.code, l.name AS tname
                    FROM location l
                    WHERE l.type = 4
                    AND l.status = 1
                    )
                    , roles AS (
                    SELECT idrole, name
                    FROM user_roles
                    ),
                    user_uc_names AS (
                    SELECT ul.idusers,string_agg(l.name, ', ') AS uc_names 
                    FROM user_locations ul JOIN location l ON l.code = ul.uc_code
                    GROUP BY ul.idusers)
                        
                    SELECT u.idusers,
                    p.name                                                         AS province_name,
                    CASE WHEN u.status = 1 THEN 'Active' ELSE 'Inactive' END       AS status_text,
                    u.username,
                    u.designation,
                    r.name                                                         AS user_role_name,
                    u.email,
                    d.division,
                    dist.dname                                                     AS district_name,
                    t.tname                                                        AS tehsil_name,
                    ucn.uc_names AS uc_names,
                    CASE WHEN u.usertype = 3 AND u.is_admin = 1 THEN 1 ELSE 0 END  AS is_province_admin,
                    CASE WHEN u.usertype = 11 AND u.is_admin = 1 THEN 1 ELSE 0 END AS is_divisional_admin,
                    CASE WHEN u.usertype = 4 AND u.is_admin = 1 THEN 1 ELSE 0 END  AS is_district_admin,
                    CASE WHEN u.usertype = 12 AND u.is_admin = 1 THEN 1 ELSE 0 END AS is_tehsil_admin
                    FROM users u
                    LEFT JOIN prov p ON p.code = u.idoffice
                    LEFT JOIN divs d ON d.divid = u.division_code AND d.provid = u.idoffice
                    LEFT JOIN dist ON dist.code = u.district_code
                    LEFT JOIN tehsil t ON t.code = u.tehsil_code
                    LEFT JOIN roles r ON r.idrole = u.usertype
                    LEFT JOIN user_uc_names ucn ON ucn.idusers = u.idusers
                      WHERE {where_clause}
                      ORDER BY u.idusers LIMIT :limit
                      OFFSET :offset;
                      """)

    total_query = text(f"""
                       SELECT COUNT(*) AS total
                        FROM users u
                        WHERE {where_clause}
                        ;

                       """)

    result_total = await db.execute(total_query, params)
    params["limit"] = payload.limit
    params["offset"] = payload.offset

    result_data = await db.execute(data_query,params)

    users = [dict(row._mapping) for row in result_data.fetchall()]
    total_count = result_total.scalar()
    return {"total": total_count, "users": users}


async def get_detail_user_info(db: AsyncSession, userinfo) -> (str, Dict[str, Any]):
    excluded_columns = {
        "password", "mot_de_passe", "final_password", "password_hash", "password_style_de_passe"
    }
    query = text("""
        WITH tehsil AS (
    SELECT l.code, l.name AS tname
    FROM location l
    WHERE l.type = 4
      AND l.status = 1
),
dist AS (
    SELECT l.code, l.dname
    FROM district d
    JOIN location l ON l.code = d.code
    WHERE l.status = 1
),
user_uc_names AS (
    SELECT ul.idusers,
           string_agg(loc.name, ', ') AS uc_names,
           string_agg(loc.code::text, ',') AS uc_codes   -- added aggregated codes
    FROM user_locations ul
    JOIN location loc ON loc.code = ul.uc_code
    WHERE loc.status = 1
    GROUP BY ul.idusers
),
creator AS (
    SELECT idusers, username AS createdby_username FROM users
),
updater AS (
    SELECT idusers, username AS updatedby_username FROM users
),
province AS (
    SELECT code, name AS province_name
    FROM location
    WHERE type = 2
      AND status = 1
)

SELECT 
    u.*,
    r.name AS role_name,
    cd.*,             -- columns from clean_divisions
    t.tname AS tehsil_name,
    dist.dname AS district_name,
    loc.code AS location_code,
    ucn.uc_names,     -- comma separated UC names
    ucn.uc_codes,     -- comma separated UC codes
    creator.createdby_username,
    updater.updatedby_username,
    p.province_name,  -- add province name here
    CASE WHEN u.usertype = 3 AND u.is_admin = 1 THEN 1 ELSE 0 END  AS is_province_admin,
    CASE WHEN u.usertype = 11 AND u.is_admin = 1 THEN 1 ELSE 0 END AS is_divisional_admin,
    CASE WHEN u.usertype = 4 AND u.is_admin = 1 THEN 1 ELSE 0 END  AS is_district_admin,
    CASE WHEN u.usertype = 12 AND u.is_admin = 1 THEN 1 ELSE 0 END AS is_tehsil_admin

FROM users u
LEFT JOIN user_roles r ON r.idrole = u.usertype
LEFT JOIN clean_divisions cd ON u.division_code = cd.divid
LEFT JOIN tehsil t ON u.tehsil_code = t.code
LEFT JOIN dist ON u.district_code = dist.code
LEFT JOIN location loc ON loc.code = u.idoffice AND loc.status = 1 AND loc.type = 2
LEFT JOIN user_uc_names ucn ON ucn.idusers = u.idusers
LEFT JOIN creator ON creator.idusers = u.createdby
LEFT JOIN updater ON updater.idusers = u.updatedby
LEFT JOIN province p ON p.code = u.idoffice
WHERE u.idusers = :user_id;
    """)
    params = {"user_id": userinfo.user_id}

    try:
        result = await db.execute(query, params)
        row = result.fetchone()  # fetch single row

        if row is None:
            return {"result": []}  # or handle "no record found" case

        row_dict = dict(row._mapping)
        for col in excluded_columns:
            row_dict.pop(col, None)


        return {"result":[row_dict]}

    except SQLAlchemyError as e:
        return {"total": "Database error fetching user info for id {user_id}: {e}"}

    except Exception as e:
        return {"total": "Unexpected error fetching user info for id {user_id}: {e}"}



async def full_update_user(db: AsyncSession, user_data):
    """
    Async function to update a user record.
    Only hashes password if provided, otherwise leaves it unchanged.
    """
    # Map accountstatus to is_active (1 for Active else 0)
    is_active = 1 if (user_data.accountstatus and user_data.accountstatus.lower() == 'active') else 0

    # Start building SQL update query
    query = """
        UPDATE users
        SET is_first_time_login = :is_first_time_login,
            updateddate = :updateddate,
            is_admin = :is_admin,
            username = :username,
            idoffice = :idoffice,
            first_name = :first_name,
            affiliation = :affiliation,
            current_address = :current_address,
            genderval = :genderval,
            is_active = :is_active,
            status = :status,
            updatedby = :updatedby,
            last_name = :last_name,
            email = :email,
            division_code = :division_code,
            mobile = :mobile,
            designation = :designation,
            district_code = :district_code,
            usertype = :usertype,
            entrypermission = :entrypermission,
            tehsil_code = :tehsil_code
    """

    # Prepare params
    params = {
        "is_first_time_login": 1,
        "updateddate": datetime.utcnow(),
        "is_admin": user_data.is_admin,
        "username": user_data.username,
        "idoffice": user_data.provincename,
        "first_name": user_data.firstname,
        "affiliation": user_data.affiliation,
        "current_address": user_data.address,
        "genderval": user_data.gender,
        "is_active": is_active,
        "status": is_active,
        "updatedby": 10,
        "last_name": user_data.lastname,
        "email": user_data.email,
        "division_code": user_data.divisionname,
        "mobile": user_data.contactnumber,
        "designation": user_data.designation,
        "district_code": user_data.districtname,
        "usertype": user_data.userrole,
        "entrypermission": user_data.userentry,
        "tehsil_code": user_data.tehsilname,
        "idusers": user_data.idusers
    }

    # Conditionally add password if provided
    if getattr(user_data, "password", None):
        password_hash = await hash.create_password_hash(user_data.password)
        password_style_de_passe = await hash.style_password(user_data.password)
        query += ", password_hash = :password_hash, password_style_de_passe = :password_style_de_passe"
        params["password_hash"] = password_hash
        params["password_style_de_passe"] = password_style_de_passe

    # Add WHERE clause
    query += " WHERE idusers = :idusers"

    try:
        result = await db.execute(text(query), params)
        await db.commit()
        return {"message": "User updated successfully", "idusers": user_data.idusers}
    except IntegrityError as e:
        await db.rollback()
        raise Exception("Integrity error or duplicate user: " + str(e))
    except Exception as e:
        await db.rollback()
        raise


from src.encryption_cryptography import hash  # your existing hash module
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import asyncio

async def update_user_passwords(db: AsyncSession):
    # Fetch all users with temp_password
    query = text("SELECT idusers, temp_password FROM users WHERE temp_password IS NOT NULL")
    result = await db.execute(query)
    users = result.fetchall()

    if not users:
        return "No users found with temp_password."

    for user_id, temp_password in users:
        # Skip empty passwords
        if not temp_password:
            continue

        password_hash = await hash.create_password_hash(temp_password)
        password_style_de_passe = await hash.style_password(temp_password)

        # Update user row
        update_query = text("""
            UPDATE users
            SET password_hash = :password_hash,
                password_style_de_passe = :password_style_de_passe
            WHERE idusers = :user_id
        """)
        await db.execute(update_query, {
            "password_hash": password_hash,
            "password_style_de_passe": password_style_de_passe,
            "user_id": user_id
        })

    await db.commit()
    return f"Updated {len(users)} users successfully."
