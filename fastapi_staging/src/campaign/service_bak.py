from typing import List, Dict, Any
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
import traceback
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
import jwt
from sqlalchemy import text
from src.encryption_cryptography import hash
from fastapi import HTTPException, status
import httpx
import re
import requests
import urllib3
from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text,bindparam
from dotenv import load_dotenv
import os

load_dotenv()  # loads variables from .env

EOC_API_KEY = os.getenv("EOC_API_KEY")
EOC_BASE_URL = os.getenv("EOC_BASE_URL")


class EOCClient:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.api_key = EOC_API_KEY
        self.base_url = EOC_BASE_URL

        if not self.api_key:
            raise ValueError("EOC_API_KEY not found in .env")

        # Disable SSL warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    async def get_campaign_list(self, limit=None):
        """Fetch campaign list from EOC API."""
        url = f"{self.base_url}campaignlist"
        async with httpx.AsyncClient(verify=False,timeout=httpx.Timeout(30.0)) as client:
            response = await client.get(
                url,
                params={"X-API-KEY": self.api_key}
            )

        if response.status_code != 200:
            raise RuntimeError(f"Error {response.status_code}: {response.text}")

        data = response.json()
        if data.get("status") == 1 and data.get("code") == 200:
            campaigns = data.get("data", [])
            return campaigns[:limit] if limit else campaigns

        return []

    async def insert_campaign(self, db: AsyncSession, campaign_data: list, idusers: int):
        """Insert campaign into DB after checking duplicates."""
        if not campaign_data or not campaign_data[0]:
            return {"error": "unable to add campaign data", "status": False, "code": 400}

        campaign = campaign_data[0]
        insert_data = {
            "campaign_code": campaign.get("campaign_code"),
            "name": campaign.get("campaign_name"),
            "date_from": campaign.get("start_date"),
            "date_to": campaign.get("end_date"),
            "status": int(campaign.get("status")),
            "activityid_idims": int(campaign.get("activityid_idims")),
            "api_id": int(campaign.get("api_id")),
            "createdby": idusers
        }

        # Validation
        if (
                insert_data["campaign_code"] == "--"
                or not insert_data["name"]
                or not insert_data["date_from"]
                or not insert_data["date_to"]
        ):
            return {"error": "unable to add campaign data", "status": False, "code": 400}

        async with db.begin():
            # Check duplicate
            date_from = datetime.strptime(insert_data["date_from"], "%Y-%m-%d").date()
            date_to = datetime.strptime(insert_data["date_to"], "%Y-%m-%d").date()
            insert_data["date_from"] = date_from
            insert_data["date_to"] = date_to

            query = text("""
                         SELECT COUNT(*) as cnt
                         FROM campaign
                         WHERE campaign_code = :campaign_code
                         """)
            result = await db.execute(query, {"campaign_code": insert_data["campaign_code"]})
            count = result.scalar()

            if count > 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"This Campaign {insert_data['name']} Already Exists."
                )

            # Insert campaign
            insert_query = text("""
                                INSERT INTO campaign (campaign_code, name, date_from, date_to,
                                                      status, activityid_idims, api_id, createdby)
                                VALUES (:campaign_code, :name, :date_from, :date_to,
                                        :status, :activityid_idims, :api_id, :createdby) RETURNING idcampaign
                                """)
            result = await db.execute(insert_query, insert_data)
            new_campaign_id = result.scalar()
            if new_campaign_id:
                async with httpx.AsyncClient(verify=False,timeout=httpx.Timeout(30.0)) as client:
                    response = await client.get(
                        f"{self.base_url}campaignlocations/{insert_data['campaign_code']}",
                        params={"X-API-KEY": self.api_key}
                    )
                if response.status_code != 200:
                    raise HTTPException(status_code=500, detail=f"API request failed: {response.status_code}")

                eocdata = response.json()
                if eocdata.get("status") != 1 or eocdata.get("code") != 200:
                    return {"status": False, "message": "No valid campaign location data"}

                campaignlocs = eocdata.get("data", [])
                if not isinstance(campaignlocs, list):
                    return {"status": False, "message": "Invalid campaign locations format"}

                cols = []
                for loc in campaignlocs:
                    ucode = int(loc.get("UCode", 0))  # default to 0 if missing
                    if ucode > 0:
                        # Check if UC exists
                        check_uc_query = text("SELECT COUNT(*) FROM uc WHERE code = :ucode")
                        result = await db.execute(check_uc_query, {"ucode": int(loc["UCode"])})
                        if result.scalar() > 0:
                            cols.append({
                                "idcampaign": new_campaign_id,
                                "iduc": int(loc["UCode"]),
                                "uc_status": 1,
                                "uc_type": 0,
                                "createdby": idusers
                            })
                        else:
                            raise HTTPException(
                                status_code=400,
                                detail=f"Campaign {insert_data['name']} UC ({loc['UCode']}) does not exist in the uc table."
                            )

                if cols:
                    await db.execute(
                        text("""
                             INSERT INTO campaign_ucs (idcampaign, iduc, uc_status, uc_type, createdby)
                             VALUES (:idcampaign, :iduc, :uc_status, :uc_type, :createdby)
                             """), cols
                    )
                    await db.execute(
                        text("""
                             INSERT INTO campaign_ucs_log (idcampaign, iduc, uc_status, uc_type, createdby)
                             VALUES (:idcampaign, :iduc, :uc_status, :uc_type, :createdby)
                             """), cols
                    )

            return {"status": True, "code": 200, "campaign_id": new_campaign_id}



# async def get_campaign_data(db, idusers: int):
#     client = EOCClient()
#     campaigns = await client.get_campaign_list()
#     if not campaigns:
#         return {"status": False, "message": "No campaigns found"}
#
#     # Insert only the first campaign
#     first_campaign = campaigns[0]
#     result = await client.insert_campaign(db, [first_campaign], idusers)
#     return result

class CampaignService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_summary(self):
        """
        Get a summary of all campaigns with counts of unique divisions, provinces,
        districts, tehsils, and UCs.
        """
        query = text("""
            SELECT 
                cd.idcampaign,
                c.name,
                c.campaign_code,
                c.date_from,
                c.date_to,
                c.plan,
                c.insert,
                c.update,
                c.delete,
                COUNT(DISTINCT d.divid) AS unique_divid_count,
                COUNT(DISTINCT p.idprovince) AS unique_province_count,
                COUNT(DISTINCT d.code) AS unique_district_count,
                COUNT(DISTINCT l.code) AS unique_tehsil_count,
                COUNT(DISTINCT cd.iduc) AS unique_uc_count
            FROM campaign_ucs AS cd
            JOIN campaign AS c
                ON cd.idcampaign = c.idcampaign
            JOIN district AS d 
                ON d.code = LEFT(CAST(cd.iduc AS TEXT), 3)::INT
            JOIN province AS p 
                ON d.province_idprovince = p.idprovince
            JOIN location AS l 
                ON l.code = LEFT(CAST(cd.iduc AS TEXT), 5)::INT
            GROUP BY cd.idcampaign, c.name, c.campaign_code, c.date_from, c.date_to, c.plan, c.insert, c.update, c.delete
            ORDER BY cd.idcampaign DESC
        """)

        try:
            result = await self.db.execute(query)
            # campaigns = [dict(row) for row in result.fetchall()]
            campaigns = result.mappings().all()
            return {"status": "success", "campaigns": campaigns}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def update_campaign_status(self, idcampaign: int, type_field: str, status: int):
        """
        Update the given field (plan/insert/update/delete) of a campaign
        based on type_field and status.
        """
        allowed_fields = ["plan", "insert", "update", "delete"]
        if type_field not in allowed_fields:
            raise HTTPException(status_code=400, detail=f"Invalid type_field: {type_field}")

        # Determine value based on status
        value_to_set = 1 if status == 1 else 0

        query = text(f"""
            UPDATE campaign
            SET {type_field} = :value
            WHERE idcampaign = :idcampaign
        """)

        name_query = text(f"""
                    SELECT name
                    FROM campaign
                    WHERE idcampaign = :idcampaign
                """)
        result = await self.db.execute(name_query, {"idcampaign": idcampaign})
        campaign_name = result.scalar()  # fetch single value

        try:
            await self.db.execute(query, {"value": value_to_set, "idcampaign": idcampaign})
            await self.db.commit()
            return {"status": "success", "message": f"{type_field} updated to {value_to_set} for campaign {campaign_name}"}
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))


    async def get_campaign_list(self):
        """
        Fetch list of campaigns (idcampaign, name) from DB
        and return as JSON-serializable list.
        Handles DB errors gracefully.
        """
        try:
            query = text("SELECT idcampaign, name FROM campaign where plan=1 and insert=1 and update=1 and delete=1")
            result = await self.db.execute(query)

            rows = result.fetchall()
            campaigns = [{"idcampaign": r.idcampaign, "name": r.name} for r in rows]

            return {"status": "success", "campaigns": campaigns}

        except SQLAlchemyError as e:
            return {"status": "error", "message": "Failed to fetch campaigns from database"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_province_division_district(self, idcampaign,type_field_camp):
        """
        Fetch provinces, divisions, and districts for a given campaign.
        :param idcampaign: int
        :return: dict with provinces, divisions, districts
        """
        if not idcampaign:
            return {"status": "error", "message": "idcampaign is required"}
        pq = """
              SELECT DISTINCT p.idprovince AS code,
                              p.name       AS name
              FROM campaign_ucs AS cd
                       JOIN province AS p
                            ON p.idprovince = LEFT ('' || cd.iduc, 1):: INT
              WHERE cd.idcampaign = :idcampaign AND cd.uc_status=1
              """
        if type_field_camp == 'EXCEL':
            pq=pq+""" AND cd.import_child_data=1"""

        pq=pq+""" ORDER BY p.name;"""

        try:
            # ------------------ Provinces ------------------
            province_query = text(pq)
            result = await self.db.execute(province_query, {"idcampaign": idcampaign})
            provinces = [dict(r) for r in result.mappings().all()]
            province_codes = [row["code"] for row in provinces]
            if not province_codes:
                return {"status": "success", "provinces": [], "divisions": [], "districts": []}

            # Convert list to tuple string for IN clause
            province_codes_str = "(" + ",".join(map(str, province_codes)) + ")"
            diq = f"""
                SELECT DISTINCT d.divid AS code,
                                d.division AS name
                FROM campaign_ucs AS cd
                JOIN clean_divisions AS d
                    ON d.dcode = LEFT('' || cd.iduc, 3)::INT
                JOIN province AS p
                    ON d.provid = p.idprovince
                WHERE cd.idcampaign = :idcampaign
                  AND d.provid IN {province_codes_str}
                  AND cd.uc_status=1
            """

            if type_field_camp == 'EXCEL':
                diq = diq + """ AND cd.import_child_data=1"""
            # ------------------ Divisions ------------------
            division_query = text(diq)
            result = await self.db.execute(division_query, {"idcampaign": idcampaign})
            divisions = [dict(r) for r in result.mappings().all()]
            division_codes = [row["code"] for row in divisions]

            if not division_codes:
                return {"status": "success", "provinces": provinces, "divisions": [], "districts": []}

            division_codes_str = "(" + ",".join(map(str, division_codes)) + ")"
            dq = f"""
                SELECT DISTINCT d.iddistrict AS code,
                                d.name AS name,
                                d.code AS dcode
                FROM campaign_ucs AS cd
                JOIN district AS d
                    ON d.code = LEFT('' || cd.iduc, 3)::INT
                JOIN province AS p
                    ON d.province_idprovince = p.idprovince
                WHERE cd.idcampaign = :idcampaign
                  AND d.divid IN {division_codes_str}
                  AND cd.uc_status=1
            """
            if type_field_camp == 'EXCEL':
                dq = dq + """ AND cd.import_child_data=1"""
            # ------------------ Districts ------------------
            district_query = text(dq)
            result = await self.db.execute(district_query, {"idcampaign": idcampaign})
            districts = [dict(r) for r in result.mappings().all()]

            return {
                "status": "success",
                "provinces": provinces,
                "divisions": divisions,
                "districts": districts
            }

        except SQLAlchemyError:
            return {"status": "error", "message": "Database error"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_provinces_for_campaign(self, idcampaign: int):
        if not idcampaign:
            return {"status": "error", "message": "idcampaign is required"}

        try:
            province_query = text("""
                                  SELECT DISTINCT p.idprovince AS code,
                                                  p.name       AS name
                                  FROM campaign_ucs AS cd
                                           JOIN province AS p
                                                ON p.idprovince = LEFT ('' || cd.iduc, 1):: INT
                                  WHERE cd.idcampaign = :idcampaign
                                  ORDER BY p.name;
                                  """)

            result = await self.db.execute(province_query, {"idcampaign": idcampaign})
            provinces = [dict(row) for row in result.mappings().all()]

            return {"status": "success", "provinces": provinces}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_divisions_for_campaign_and_provinces(self, campaign_ids: int,
                                                       province_ids: list[int]):
        """
        Fetch divisions for given campaign(s) and province(s)

        :param db: AsyncSession
        :param campaign_ids: List of campaign IDs
        :param province_ids: List of province IDs
        :return: dict with status and divisions or error message
        """
        if not campaign_ids:
            return {"status": "error", "message": "campaign_ids list is required"}
        if not province_ids:
            return {"status": "error", "message": "province_ids list is required"}

        try:
            # Convert lists to tuple string for SQL IN clause
            province_ids_str = "(" + ",".join(map(str, province_ids)) + ")"

            division_query = text(f"""
                SELECT DISTINCT 
                    d.divid AS code,
                    d.division AS dname
                FROM campaign_ucs AS cd
                JOIN clean_divisions AS d 
                    ON d.dcode = LEFT('' || cd.iduc, 3)::INT
                JOIN province AS p 
                    ON d.provid = p.idprovince
                WHERE cd.idcampaign = {campaign_ids} 
                  AND d.provid IN {province_ids_str};
            """)

            result = await self.db.execute(division_query)
            divisions = [dict(r) for r in result.mappings().all()]

            return {"status": "success", "divisions": divisions}

        except SQLAlchemyError as e:
            # Log the exception if you have a logger
            return {"status": "error", "message": f"Database error: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": f"Unexpected error: {str(e)}"}

    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.exc import SQLAlchemyError

    async def get_districts_for_campaign(self, campaign_id: int, division_ids: list):
        """
        Fetch districts for a given campaign and list of division IDs asynchronously.
        :param db: AsyncSession
        :param campaign_id: int
        :param division_ids: list of int
        :return: dict
        """
        try:
            if not division_ids:
                division_ids = [0]  # fallback to prevent SQL error
            division_ids_str = "(" + ",".join(map(str, division_ids)) + ")"

            query = text(f"""
                         SELECT DISTINCT d.iddistrict,
                                         d.name AS dname,
                                         d.code
                         FROM campaign_ucs AS cd
                                  JOIN district AS d
                                       ON d.code = LEFT ('' || cd.iduc, 3):: INT
                             JOIN province AS p
                         ON d.province_idprovince = p.idprovince
                         WHERE cd.idcampaign = {campaign_id} 
                           AND d.divid IN {division_ids_str};
                         """)

            result = await self.db.execute(query)
            districts = [dict(row) for row in result.mappings().all()]
            return {"status": "success", "districts": districts}

        except SQLAlchemyError as e:
            return {"status": "error", "message": f"Database error: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}



    async def get_campaign_active_info(self, campaign_id: int):
        """
        Fetch districts for a given campaign and list of division IDs asynchronously.
        :param db: AsyncSession
        :param campaign_id: int
        :param division_ids: list of int
        :return: dict
        """
        try:
            if not campaign_id:
                return {"status": "error", "message": f"Campaign ID Required"}
            else:
                firsthalf = """
                SELECT DISTINCT p.idprovince      AS province_code,
                    p.name            AS province_name,
                    d.divid           AS division_id,
                    d.division        AS division_name,
                    dist.iddistrict   AS district_id,
                    dist.name         AS district_name,
                    dist.code         AS district_code
                FROM campaign_ucs AS cd
                         JOIN province AS p
                              ON p.idprovince = LEFT('' || cd.iduc, 1)::INT
                    JOIN clean_divisions AS d
                ON d.dcode = LEFT('' || cd.iduc, 3)::INT
                    AND d.provid = p.idprovince
                    JOIN district AS dist
                    ON dist.code = LEFT('' || cd.iduc, 3)::INT
                    AND dist.province_idprovince = p.idprovince
                    AND dist.divid = d.divid
                WHERE cd.idcampaign = :campaignid"""

                secondhalf = """ and uc_status=1
                              AND d.provid = p.idprovince
                              AND dist.divid = d.divid
                            ORDER BY p.name, d.division, dist.name;
                             """
                thirdhalf = """ and import_child_data=1 and uc_status=1
                                              AND d.provid = p.idprovince
                                              AND dist.divid = d.divid
                                            ORDER BY p.name, d.division, dist.name;
                                             """

                query = text(firsthalf + secondhalf)
                squery = text(firsthalf + thirdhalf)

                result_aucs = await self.db.execute(query, {"campaignid":campaign_id,"icd": 0})
                result_eucs = await self.db.execute(squery, {"campaignid":campaign_id,"icd": 1})
                result_aucs = [dict(row) for row in result_aucs.mappings().all()]
                result_eucs = [dict(row) for row in result_eucs.mappings().all()]
                return {"status": "success", "Active UC's": result_aucs, "Excel Active UC's": result_eucs}

        except SQLAlchemyError as e:
            return {"status": "error", "message": f"Database error: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


    async def save_plan(self, plans: list,campaignid:int,iduser:int):
        """
        Save or update campaign plans.
        :param plans: list of dict containing plan info
        :param idusers: int (user id)
        :return: dict
        """
        try:
            for plan in plans:
                idcampaign = campaignid
                iduc = plan.get("iduc")

                if not idcampaign or not iduc:
                    continue

                # 1. Get previous log row
                prev_query = text("""
                    SELECT log_id FROM campaign_ucs_log
                    WHERE idcampaign = :idcampaign AND iduc = :iduc
                    ORDER BY log_id DESC LIMIT 1
                """)
                prev_log = await self.db.execute(prev_query, {"idcampaign": idcampaign, "iduc": int(iduc)})
                prev_log = prev_log.mappings().first()

                # 2. Update campaign_ucs
                update_query = text("""
                    UPDATE campaign_ucs
                    SET uc_status = :uc_status,
                        uc_status_zd = :uc_status_zd,
                        updatedby = :updatedby,
                        import_child_data = :import_child_data
                    WHERE idcampaign = :idcampaign
                      AND LEFT(CAST(iduc AS TEXT), 3) = :iduc
                """)
                result = await self.db.execute(update_query, {
                    "uc_status": plan.get("uc_status", 0),
                    "uc_status_zd": plan.get("uc_status_zd", 0),
                    "updatedby": iduser,
                    "import_child_data": plan.get("import_child_data", 0),
                    "idcampaign": idcampaign,
                    "iduc": str(iduc).strip()
                })
                print(result,"afeef")
                if result.rowcount == 0:
                    await self.db.rollback()
                    return {"status": False, "msg": "Error in Updating Plan"}

                # 3. Insert into campaign_ucs_log
                insert_query = text("""
                    INSERT INTO campaign_ucs_log (
                        prev_log_id, idcampaign, iduc, createdby,
                        uc_status, uc_status_zd, import_child_data
                    )
                    VALUES (:prev_log_id, :idcampaign, :iduc, :createdby,
                            :uc_status, :uc_status_zd, :import_child_data)
                """)
                await self.db.execute(insert_query, {
                    "prev_log_id": prev_log["log_id"] if prev_log else None,
                    "idcampaign": idcampaign,
                    "iduc": int(iduc),
                    "createdby": iduser,
                    "uc_status": plan.get("uc_status", 0),
                    "uc_status_zd": plan.get("uc_status_zd", 0),
                    "import_child_data": plan.get("import_child_data", 0)
                })



            plan_iducs = [plan.get("iduc") for plan in plans if plan.get("iduc")]
            reverse_update_query = text(f"""
                UPDATE campaign_ucs
                SET uc_status = 0,
                    uc_status_zd = 0,
                    updatedby = :updatedby,
                    import_child_data = 0
                WHERE idcampaign = :idcampaign
                  AND LEFT(CAST(iduc AS TEXT), 3) NOT IN :iducs
            """).bindparams(bindparam("iducs", expanding=True))

            await self.db.execute(reverse_update_query, {
                "updatedby": iduser,
                "idcampaign": idcampaign,
                "iducs": tuple(plan_iducs) if plan_iducs else tuple([-1])  # avoid empty IN ()
            })
            await self.db.commit()
            return {"status": True, "msg": "Plan Was Updated Successfully"}

        except SQLAlchemyError as e:
            await self.db.rollback()
            return {"status": "error", "msg": f"Database error: {str(e)}"}

        except Exception as e:
            await self.db.rollback()
            return {"status": "error", "msg": str(e)}

        nc def get_provinces_info_for_campaign(self, idcampaign: int, idprovince: int | None = None):
        """
        Get distinct provinces for a given campaign.
        If idprovince is provided, filter by it. Otherwise, return all provinces for that campaign.
        """
        base_query = """
            SELECT DISTINCT
                p.idprovince AS code,
                p.name       AS name
            FROM campaign_ucs AS cd
            JOIN province AS p
                ON p.idprovince = LEFT (CAST(cd.iduc AS TEXT), 1)::INT
            WHERE cd.idcampaign = :idcampaign
        """

        # Add optional province filter
        if idprovince is not None:
            base_query += " AND p.idprovince = :idprovince"

        base_query += " ORDER BY p.name"

        try:
            query = text(base_query)
            params = {"idcampaign": idcampaign}
            if idprovince is not None:
                params["idprovince"] = idprovince

            result = await self.db.execute(query, params)
            provinces = result.mappings().all()
            return {"status": "success", "provinces": provinces}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_divisions_info_for_campaign(
        self, idcampaign: int, idprovince: int, iddivision: int | None = None
    ):
        """
        Get distinct divisions for a given campaign and province.
        If iddivision is provided, filter by it. Otherwise, return all divisions for that province.
        """
        base_query = """
            SELECT DISTINCT
                d.divid   AS code,
                d.division AS dname
            FROM campaign_ucs AS cd
            JOIN clean_divisions AS d
                ON d.dcode = LEFT(CAST(cd.iduc AS TEXT), 3)::INT
            JOIN province AS p
                ON d.provid = p.idprovince
            WHERE cd.idcampaign = :idcampaign
              AND d.provid = :idprovince
        """

        # Add optional division filter
        if iddivision is not None:
            base_query += " AND d.divid = :iddivision"

        base_query += " ORDER BY d.division"

        try:
            query = text(base_query)
            params = {
                "idcampaign": idcampaign,
                "idprovince": idprovince,
            }
            if iddivision is not None:
                params["iddivision"] = iddivision

            result = await self.db.execute(query, params)
            divisions = result.mappings().all()
            return {"status": "success", "divisions": divisions}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_districts_info_for_campaign(
            self, idcampaign: int, iddivision: int, dcode: int | None = None
    ):
        """
        Get distinct districts for a given campaign and division.
        If dcode is provided, filter by it. Otherwise, return all districts.
        """
        base_query = """
                     SELECT DISTINCT d.iddistrict, \
                                     d.name AS dname, \
                                     d.code
                     FROM campaign_ucs AS cd
                              JOIN district AS d
                                   ON d.code = LEFT (CAST (cd.iduc AS TEXT), 3):: INT
                         JOIN province AS p
                     ON d.province_idprovince = p.idprovince
                     WHERE cd.idcampaign = :idcampaign
                       AND d.divid = :iddivision \
                     """

        if dcode is not None:
            base_query += " AND d.code = :dcode"

        base_query += " ORDER BY d.name"

        try:
            query = text(base_query)
            params = {"idcampaign": idcampaign, "iddivision": iddivision}
            if dcode is not None:
                params["dcode"] = dcode

            result = await self.db.execute(query, params)
            districts = result.mappings().all()
            return {"status": "success", "districts": districts}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    async def get_tehsils_info_for_campaign(
        self, idcampaign: int, dcode: int, lcode: int | None = None
    ):
        """
        Get tehsils for a given campaign and district.
        If lcode (tehsil code) is provided, filter by it. Otherwise, return all tehsils.
        """
        base_query = """
            SELECT
                l.code AS tehsil_code,
                l.name AS tehsil_name
            FROM campaign_ucs AS cd
            JOIN campaign AS c
                ON cd.idcampaign = c.idcampaign
            JOIN district AS d
                ON d.code = LEFT(CAST(cd.iduc AS TEXT), 3)::INT
            JOIN location AS l
                ON l.code = LEFT(CAST(cd.iduc AS TEXT), 5)::INT
            WHERE cd.idcampaign = :idcampaign
              AND d.code = :dcode
        """

        if lcode is not None:
            base_query += " AND l.code = :lcode"

        base_query += """
            GROUP BY cd.idcampaign, c.name, l.code, l.name
            ORDER BY cd.idcampaign DESC, l.name
        """

        try:
            query = text(base_query)
            params = {"idcampaign": idcampaign, "dcode": dcode}
            if lcode is not None:
                params["lcode"] = lcode

            result = await self.db.execute(query, params)
            tehsils = result.mappings().all()
            return {"status": "success", "tehsils": tehsils}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    async def get_ucs_info_for_campaign(
        self, idcampaign: int, tehcode: int, uc_codes: list[int] | None = None
    ):
        """
        Get UCs for a given campaign and tehsil.
        If uc_codes list is provided, filter by those UC codes. Otherwise, return all UCs for the tehsil.
        """
        base_query = """
            SELECT
                d.name || ' (' || d.tname || ')' AS uctname,
                d.code,
                ucs.uc_type
            FROM campaign_ucs AS ucs
            JOIN location AS d
                ON d.code = ucs.iduc
            WHERE ucs.idcampaign = :idcampaign
              AND ucs.uc_status = 1
              AND d.status = 1
              AND LEFT(CAST(d.code AS TEXT), 5)::INT = :tehcode
        """

        # If UC codes are passed, filter by them
        if uc_codes and len(uc_codes) > 0:
            placeholders = ", ".join([f":uc{i}" for i in range(len(uc_codes))])
            base_query += f" AND d.code IN ({placeholders})"

        base_query += """
            ORDER BY d.dname, d.name
        """

        try:
            query = text(base_query)

            params = {"idcampaign": idcampaign, "tehcode": tehcode}
            if uc_codes and len(uc_codes) > 0:
                for i, val in enumerate(uc_codes):
                    params[f"uc{i}"] = val

            result = await self.db.execute(query, params)
            ucs = result.mappings().all()
            return {"status": "success", "ucs": ucs}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def create_formheader(self, idcampaign: int, iduc: int, supervisor_name: str, enteredby: int):
        insert_sql = text("""
                          INSERT INTO formheader (idcampaign,
                                                  iduc,
                                                  supervisor_name,
                                                  enteredby,
                                                  tid,
                                                  day)
                          VALUES (:idcampaign,
                                  :iduc,
                                  :supervisor_name,
                                  :enteredby,
                                  'TEMP',
                                  EXTRACT(DAY FROM CURRENT_DATE)::SMALLINT) RETURNING idheader;
                          """)

        update_sql = text("""
                          UPDATE formheader
                          SET tid = CONCAT('SMC-', :idheader)
                          WHERE idheader = :idheader;
                          """)

        log_insert_sql = text("""
                              INSERT INTO logformheader (idheader, idcampaign, iduc, supervisor_name, enteredby, tid,
                                                         day)
                              SELECT idheader, idcampaign, iduc, supervisor_name, enteredby, tid, day
                              FROM formheader
                              WHERE idheader = :idheader;
                              """)

        try:
            async with self.db.begin():  # transaction scope
                # Insert row
                result = await self.db.execute(insert_sql, {
                    "idcampaign": idcampaign,
                    "iduc": iduc,
                    "supervisor_name": supervisor_name,
                    "enteredby": enteredby
                })

                row = result.fetchone()
                if not row:
                    raise HTTPException(status_code=500, detail="Failed to create form header")

                idheader = row[0]

                # Update tid
                await self.db.execute(update_sql, {"idheader": idheader})
                await self.db.execute(log_insert_sql, {"idheader": idheader})
            return {
                "status": "success",
                "message": "AIC header created successfully",
                "idheader": idheader
            }

        except Exception as e:
            # Log or raise a friendly error
            print(f"[ERROR] create_formheader failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error creating AIC header: {str(e)}"
            )



    async def update_formheader(self, idcampaign: int, iduc: int, supervisor_name: str, enteredby: int,idheader: int):
        update_sql = text("""
                          UPDATE formheader
                          SET supervisor_name = :supervisor_name
                          WHERE iduc = :iduc
                          AND idheader = :idheader
                          AND idcampaign = :idcampaign
                          RETURNING idheader;
                          """)

        log_insert_sql = text("""
                              INSERT INTO logformheader (idheader, idcampaign, iduc, supervisor_name, enteredby, tid,
                                                         day)
                              SELECT idheader, idcampaign, iduc, supervisor_name, enteredby, tid, day
                              FROM formheader
                              WHERE idheader = :idheader;
                              """)

        try:
            async with self.db.begin():  # transaction scope
                # Insert row
                result = await self.db.execute(update_sql, {
                    "supervisor_name": supervisor_name,
                    "iduc": iduc,
                    "idheader": idheader,
                    "idcampaign": idcampaign
                })

                row = result.fetchone()
                if not row:
                    raise HTTPException(status_code=500, detail="Failed to update form header")

                idheader = row[0]
                await self.db.execute(log_insert_sql, {"idheader": idheader})
            return {
                "status": "success",
                "message": "AIC header updated successfully",
                "idheader": idheader
            }

        except Exception as e:
            # Log or raise a friendly error
            print(f"[ERROR] update_formheader failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error creating AIC header: {str(e)}"
            )


    async def create_formteam(self, idheader, team_no, team_member, enteredby, teamtype):
        """
        Insert a new team member into formteam and return idteam
        """
        insert_sql = text("""
                          INSERT INTO formteam (idheader, team_no, team_member, teamtype, enteredby)
                          VALUES (:idheader, UPPER(TRIM(:team_no)), UPPER(TRIM(:team_member)), :teamtype,
                                  :enteredby) RETURNING idteam;
                          """)

        log_insert_sql = text("""
                              INSERT INTO logformteam (idteam, idheader, team_no, team_member, teamtype, enteredby)
                              SELECT idteam, idheader, team_no, team_member, teamtype, enteredby
                              FROM formteam
                              WHERE idteam = :idteam;
                              """)

        try:
            async with self.db.begin():  # transaction scope
                result = await self.db.execute(insert_sql, {
                    "idheader": idheader,
                    "team_no": team_no,
                    "team_member": team_member,
                    "teamtype": teamtype,
                    "enteredby": enteredby
                })

                # Correct fetch for async
                row = result.fetchone()
                if not row:
                    return {
                        "status": "error",
                        "message": "Failed to create team member",
                        "idteam": None
                    }

                idteam = row[0]
                await self.db.execute(log_insert_sql, {"idteam": idteam})
                return {
                    "status": "success",
                    "message": "Team member created successfully",
                    "idteam": idteam
                }

        except IntegrityError:
            # Duplicate team_no for the same header
            return {
                "status": "error",
                "message": f"Team number '{team_no}' already exists for this header.",
                "idteam": None
            }

        except Exception as e:
            print(f"[ERROR] create_formteam failed: {e}")
            return {
                "status": "error",
                "message": f"Error creating team member: {str(e)}",
                "idteam": None
            }

    async def update_formteam(self, idteam, team_no, team_member):
        """
        Update an existing team member in formteam by idteam.
        """
        update_sql = text("""
                          UPDATE formteam
                          SET team_no     = UPPER(TRIM(:team_no)),
                              team_member = UPPER(TRIM(:team_member))
                          WHERE idteam = :idteam RETURNING idteam;
                          """)

        log_insert_sql = text("""
                              INSERT INTO logformteam (idteam, idheader, team_no, team_member, teamtype, enteredby)
                              SELECT idteam, idheader, team_no, team_member, teamtype, enteredby
                              FROM formteam
                              WHERE idteam = :idteam;
                              """)
        try:
            async with self.db.begin():  # transaction scope
                result = await self.db.execute(update_sql, {
                    "idteam": idteam,
                    "team_no": team_no,
                    "team_member": team_member
                })

                row = result.fetchone()
                if not row:
                    return {
                        "status": "error",
                        "message": f"No team member found with idteam {idteam}",
                        "idteam": None
                    }

                await self.db.execute(log_insert_sql, {"idteam": idteam})
                return {
                    "status": "success",
                    "message": "Team member updated successfully",
                    "idteam": row[0]
                }

        except IntegrityError:
            # This handles duplicate team_no for the same header
            return {
                "status": "error",
                "message": f"Team number '{team_no}' already exists for this header.",
                "idteam": None
            }

        except Exception as e:
            print(f"[ERROR] update_formteam failed: {e}")
            return {
                "status": "error",
                "message": f"Error updating team member: {str(e)}",
                "idteam": None
            }

    async def get_formteam_by_header(self, idheader: int):
        """
        Fetch all team members for a given formheader.
        Returns a list of dictionaries with idteam, team_no, and team_member.
        """
        select_sql = text("""
                          SELECT idteam, team_no, team_member
                          FROM formteam
                          WHERE idheader = :idheader
                          ORDER BY team_no
                          """)

        try:
            result = await self.db.execute(select_sql, {"idheader": idheader})
            rows = result.fetchall()

            # Transform rows into list of dicts
            teams = [{"idteam": row.idteam, "team_no": row.team_no, "team_member": row.team_member}
                     for row in rows]

            return {
                "status": "success",
                "message": f"{len(teams)} team members found",
                "data": teams
            }

        except Exception as e:
            print(f"[ERROR] get_formteam_by_header failed: {e}")
            return {
                "status": "error",
                "message": f"Error fetching team members: {str(e)}",
                "data": []
            }

    async def get_team_options(self, idheader: int, teamtype: int = 1):
        """
        Fetch team options (value + label) for a given idheader & teamtype.
        Returns a list of dictionaries with 'value' and 'label'.
        Ensures uppercase formatting.
        """
        sql = text("""
                   SELECT t.idheader || ' , ' || t.idteam AS value,
                ' TEAM - ' ||
                UPPER(TRIM(t.team_no)) AS label
                   FROM formheader h
                       JOIN formteam t
                   ON h.idheader = t.idheader
                   WHERE h.idheader = :idheader
                     AND t.teamtype = :teamtype
                   ORDER BY t.idteam ASC;
                   """)

        try:
            async with self.db.begin():
                result = await self.db.execute(sql, {
                    "idheader": idheader,
                    "teamtype": teamtype
                })
                rows = result.fetchall()

                if not rows:
                    return {
                        "status": "error",
                        "message": f"No team members found for header {idheader} and teamtype {teamtype}",
                        "data": []
                    }

                options = [
                    {"value": row.value, "label": row.label}
                    for row in rows
                ]

                return {
                    "status": "success",
                    "message": f"Found {len(options)} team members for header {idheader}",
                    "data": options
                }

        except Exception as e:
            print(f"[ERROR] get_team_options failed: {e}")
            return {
                "status": "error",
                "message": f"Error fetching team options for header {idheader}: {str(e)}",
                "data": []
            }

    async def insert_formchildren(self, payload: dict):
        """
        Insert a new child record into formchildren.
        Expects `payload` to contain all required fields.
        """
        insert_sql = text("""
                          INSERT INTO formchildren (idheader,
                                                    idteam,
                                                    day,
                                                    house,
                                                    name,
                                                    gender,
                                                    age,
                                                    father,
                                                    address,
                                                    nofmc,
                                                    reasontype,
                                                    nodose,
                                                    reject,
                                                    location,
                                                    hrmp,
                                                    returndate,
                                                    dateofvacc,
                                                    enteredby,
                                                    entereddate)
                          VALUES (:idheader,
                                  :idteam,
                                  :day,
                                  :house,
                                  :name,
                                  :gender,
                                  :age,
                                  :father,
                                  :address,
                                  :nofmc,
                                  :reasontype,
                                  :nodose,
                                  :reject,
                                  :location,
                                  :hrmp,
                                  :returndate,
                                  :dateofvacc,
                                  :idusers,
                                  NOW()) RETURNING idchildren;
                          """)
        log_insert_sql = text("""
                              INSERT INTO logformchildren (idchildren, idheader, idteam, day, house, name, gender, age,
                                                           father, address,
                                                           nofmc, reasontype, nodose, reject, location, hrmp,
                                                           returndate, dateofvacc, enteredby, entereddate)
                              SELECT idchildren,
                                     idheader,
                                     idteam, day, house, name, gender, age, father, address, nofmc, reasontype, nodose, reject, location, hrmp, returndate, dateofvacc, enteredby, entereddate
                              FROM formchildren
                              WHERE idchildren = :idchildren;
                              """)
        try:
            async with self.db.begin():  # transaction
                result = await self.db.execute(insert_sql, payload)
                row = result.fetchone()

                if not row:
                    return {
                        "status": "error",
                        "message": "Insert failed, no idchildren returned.",
                        "idchildren": None
                    }

                idchildren = row[0]
                await self.db.execute(log_insert_sql, {"idchildren": idchildren})

                fetch_header_sql = text("""
                                        SELECT idcampaign, iduc
                                        FROM formheader
                                        WHERE idheader = :idheader LIMIT 1;
                                        """)
                header_result = await self.db.execute(fetch_header_sql, {"idheader": payload.get("idheader")})
                header_row = header_result.fetchone()

                if not header_row:
                    return {"status": "error", "message": "Header not found", "idchildren": idchildren}

                idcampaign, iduc = header_row

                # Insert into campaign_child_wise_history
                campaign_history_sql = text("""
                                            INSERT INTO campaign_child_wise_history (idcampaign, idchildren, is_pmc,
                                                                                     is_smc, is_covered,
                                                                                     updated_date, updated_by, idheader,
                                                                                     idteam, age_at_campaign, iduc)
                                            VALUES (:idcampaign, :idchildren, 0, 1, 0,
                                                    NOW(), :updated_by, :idheader, :idteam, :age, :iduc);
                                            """)
                await self.db.execute(campaign_history_sql, {
                    "idcampaign": idcampaign,
                    "idchildren": idchildren,
                    "updated_by": payload.get("idusers"),
                    "idheader": payload.get("idheader"),
                    "idteam": payload.get("idteam"),
                    "age": payload.get("age"),
                    "iduc": iduc
                })

                return {
                    "status": "success",
                    "message": "Child record inserted successfully",
                    "idchildren": idchildren
                }

        except IntegrityError as e:
            # E.g. invalid FK, unique constraint issues
            return {
                "status": False,
                "message": f"Integrity error inserting child record:",
                "idchildren": None
            }

        except Exception as e:
            print(f"[ERROR] insert_formchildren failed")
            return {
                "status": False,
                "message": f"Unexpected error inserting child record",
                "idchildren": None
            }

    async def get_children_by_header_and_team(self, idheader: int, idteam: int):
        """
        Fetch all children records for a given idheader and idteam.
        """
        query_sql = text("""
                         SELECT *
                         FROM formchildren
                         WHERE idheader = :idheader
                           AND idteam = :idteam
                         ORDER BY entereddate DESC;
                         """)

        try:
            async with self.db.begin():
                result = await self.db.execute(query_sql, {
                    "idheader": idheader,
                    "idteam": idteam
                })

                rows = result.mappings().all()  # returns list of dict-like rows

                if not rows:
                    return {
                        "status": "error",
                        "message": f"No child records found for idheader={idheader}, idteam={idteam}",
                        "data": []
                    }

                return {
                    "status": "success",
                    "message": "Child records retrieved successfully",
                    "data": [dict(row) for row in rows]  # ✅ clean JSON dict
                }

        except SQLAlchemyError as e:
            print(f"[DB ERROR] get_children_by_header_and_team failed: {e}")
            return {
                "status": "error",
                "message": f"Database error: {str(e)}",
                "data": []
            }
        except Exception as e:
            print(f"[ERROR] get_children_by_header_and_team failed: {e}")
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}",
                "data": []
            }

    async def get_children_by_header_and_team(self, idheader: int, idteam: int):
        """
        Fetch all children records for a given idheader and idteam.
        """
        query_sql = text("""
                         SELECT *
                         FROM formchildren
                         WHERE idheader = :idheader
                           AND idteam = :idteam
                         ORDER BY entereddate DESC;
                         """)

        try:
            async with self.db.begin():
                result = await self.db.execute(query_sql, {
                    "idheader": idheader,
                    "idteam": idteam
                })

                rows = result.mappings().all()  # returns list of dict-like rows

                if not rows:
                    return {
                        "status": "error",
                        "message": f"No child records found for idheader={idheader}, idteam={idteam}",
                        "data": []
                    }

                return {
                    "status": "success",
                    "message": "Child records retrieved successfully",
                    "data": [dict(row) for row in rows]  # ✅ clean JSON dict
                }

        except SQLAlchemyError as e:
            print(f"[DB ERROR] get_children_by_header_and_team failed: {e}")
            return {
                "status": "error",
                "message": f"Database error: {str(e)}",
                "data": []
            }
        except Exception as e:
            print(f"[ERROR] get_children_by_header_and_team failed: {e}")
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}",
                "data": []
            }

    async def get_formchild_by_id(self, idchildren: int = 1395363) -> Dict[str, Any]:
        """
        Fetch a single child record from formchildren by idchildren.
        Returns record as a JSON-like dictionary.
        """
        select_sql = text("""
                          SELECT *
                          FROM formchildren
                          WHERE idchildren = :idchildren LIMIT 1;
                          """)

        try:
            async with self.db.begin():  # transaction scope
                result = await self.db.execute(select_sql, {"idchildren": idchildren})
                row = result.fetchone()

                if not row:
                    return {
                        "status": "error",
                        "message": f"No child found with idchildren={idchildren}",
                        "data": None
                    }

                # Convert SQLAlchemy row to dict
                child_dict = dict(row._mapping)
                return {
                    "status": "success",
                    "message": "Child record retrieved successfully",
                    "data": child_dict
                }

        except Exception as e:
            print(f"[ERROR] get_formchild_by_id failed: {e}")
            return {
                "status": "error",
                "message": f"Unexpected error fetching child record: {str(e)}",
                "data": None
            }


    async def update_formchildren(self, idchildren: int, payload: dict) -> Dict[str, Any]:
        """
        Update an existing child record in formchildren by idchildren.
        Expects `payload` to contain all updatable fields.
        """
        update_sql = text("""
            UPDATE formchildren
            SET day = :day,
                house = :house,
                name = :name,
                gender = :gender,
                age = :age,
                father = :father,
                address = :address,
                nofmc = :nofmc,
                reasontype = :reasontype,
                nodose = :nodose,
                reject = :reject,
                location = :location,
                hrmp = :hrmp,
                returndate = :returndate,
                dateofvacc = :dateofvacc,
                updatedby = :idusers,
                updateddate = NOW()
            WHERE idchildren = :idchildren
            RETURNING idchildren;
        """)
        log_insert_sql = text("""
                              INSERT INTO logformchildren (idchildren, idheader, idteam, day, house, name, gender, age,
                                                           father, address,
                                                           nofmc, reasontype, nodose, reject, location, hrmp,
                                                           returndate, dateofvacc, enteredby, entereddate, updatedby,
                                                           updateddate)
                              SELECT idchildren,
                                     idheader,
                                     idteam, day, house, name, gender, age, father, address, nofmc, reasontype, nodose, reject, location, hrmp, returndate, dateofvacc, enteredby, entereddate, updatedby, updateddate
                              FROM formchildren
                              WHERE idchildren = :idchildren;
                              """)

        try:
            async with self.db.begin():  # transaction
                # include idchildren in the payload for the WHERE clause
                payload["idchildren"] = idchildren
                result = await self.db.execute(update_sql, payload)
                row = result.fetchone()

                if not row:
                    return {
                        "status": "error",
                        "message": f"Update failed, no record found with idchildren={idchildren}",
                        "idchildren": None
                    }

                await self.db.execute(log_insert_sql, {"idchildren": idchildren})
                return {
                    "status": "success",
                    "message": f"Child record with idchildren={idchildren} updated successfully",
                    "idchildren": row[0]
                }

        except IntegrityError as e:
            return {
                "status": "error",
                "message": f"Integrity error updating child record: {str(e.orig)}",
                "idchildren": None
            }

        except Exception as e:
            print(f"[ERROR] update_formchildren failed: {e}")
            return {
                "status": "error",
                "message": f"Unexpected error updating child record: {str(e)}",
                "idchildren": None
            }

    async def get_formheaders_by_campaign_uc(self, idcampaign: int, iduc: int) -> Dict[str, Any]:
        """
        Fetch header records from formheader filtered by idcampaign and iduc.
        Returns a list of dictionaries with idheader, tid, and supervisor_name.
        """
        select_sql = text("""
            SELECT idheader, tid, supervisor_name
            FROM formheader
            WHERE idcampaign = :idcampaign
              AND iduc = :iduc;
        """)

        try:
            async with self.db.begin():  # transaction
                result = await self.db.execute(select_sql, {"idcampaign": idcampaign, "iduc": iduc})
                rows = result.fetchall()

                if not rows:
                    return {
                        "status": "False",
                        "message": f"No headers found for idcampaign={idcampaign}, iduc={iduc}",
                        "data": []
                    }

                # Convert each row to dict
                data = [dict(row._mapping) for row in rows]
                return {
                    "status": "success",
                    "message": "Header records retrieved successfully",
                    "data": data
                }

        except Exception as e:
            print(f"[ERROR] get_formheaders_by_campaign_uc failed: {e}")
            return {
                "status": "False",
                "message": f"Unexpected error fetching header records: {str(e)}",
                "data": []
            }

    async def get_formheader_details_by_tid(self, tid: str) -> Dict[str, Any]:
        """
        Fetch detailed header record by tid.
        Returns province, division, district, tehsil, uc, campaign, and supervisor info.
        """
        select_sql = text("""
                          SELECT DISTINCT p.idprovince       AS pid,
                                          p.name             AS pname,
                                          d.divid            AS divid,
                                          d.division         AS divname,
                                          dist.iddistrict    AS districtid,
                                          dist.name          AS districtname,
                                          tehsil.code        AS tehsilid,
                                          tehsil.name        AS tehsilname,
                                          uc.code            AS uccode,
                                          uc.name            AS ucname,
                                          fh.idcampaign      AS idcampaign,
                                          c.name             AS campaign_name,
                                          fh.supervisor_name AS supervisor_name,
                                          fh.tid             AS aicid,
                                          fh.idheader        AS aicheader
                          FROM formheader fh
                                   JOIN campaign_ucs cu
                                        ON fh.iduc = cu.iduc
                                   JOIN campaign c
                                        ON fh.idcampaign = c.idcampaign
                                   JOIN province p
                                        ON p.idprovince = LEFT (fh.iduc::TEXT, 1):: INT
                              JOIN clean_divisions d
                          ON d.dcode = LEFT (fh.iduc::TEXT, 3):: INT
                              JOIN district dist
                              ON dist.code = LEFT (fh.iduc::TEXT, 3):: INT
                              JOIN location tehsil
                              ON tehsil.code = LEFT (fh.iduc::TEXT, 5):: INT
                              JOIN location uc
                              ON uc.code = fh.iduc
                          WHERE fh.tid = :tid;
                          """)

        try:
            async with self.db.begin():
                result = await self.db.execute(select_sql, {"tid": tid})
                rows = result.fetchall()

                if not rows:
                    return {
                        "status": "error",
                        "message": f"No details found for tid={tid}",
                        "data": []
                    }

                data = [dict(row._mapping) for row in rows]
                return {
                    "status": "success",
                    "message": f"Details retrieved successfully for tid={tid}",
                    "data": data
                }

        except Exception as e:
            print(f"[ERROR] get_formheader_details_by_tid failed: {e}")
            return {
                "status": "error",
                "message": f"Unexpected error fetching details for tid={tid}: {str(e)}",
                "data": []
            }

    async def insert_bulk_formchildren(self, payloads: list[dict]):
        """
        Bulk insert multiple child records into formchildren.
        Commits only if all inserts succeed (atomic).
        """
        insert_sql = text("""
                          INSERT INTO formchildren (idheader,
                                                    idteam,
                                                    day,
                                                    house,
                                                    name,
                                                    gender,
                                                    age,
                                                    father,
                                                    address,
                                                    nofmc,
                                                    reasontype,
                                                    nodose,
                                                    reject,
                                                    location,
                                                    hrmp,
                                                    returndate,
                                                    dateofvacc,
                                                    enteredby,
                                                    entereddate)
                          VALUES (:idheader,
                                  :idteam,
                                  :day,
                                  :house,
                                  :name,
                                  :gender,
                                  :age,
                                  :father,
                                  :address,
                                  :nofmc,
                                  :reasontype,
                                  :nodose,
                                  :reject,
                                  :location,
                                  :hrmp,
                                  :returndate,
                                  :dateofvacc,
                                  :idusers,
                                  NOW());
                          """)

        try:
            async with self.db.begin():  # single transaction
                await self.db.execute(insert_sql, payloads)
                return {
                    "status": "success",
                    "message": f"Bulk records inserted successfully",
                    "total_children": len(payloads)
                }

        except IntegrityError as e:
            return {
                "status": "error",
                "message": f"Integrity error during bulk insert",
                "idchildren": None
            }

        except Exception as e:
            print(f"[ERROR] bulk insert_formchildren failed:")
            return {
                "status": "error",
                "message": f"Unexpected error inserting child records",
                "idchildren": None
            }

    async def get_campaign_nested(self, iducs: List[int], idcampaign: int, enteredby: int):
        mapper = ReasonMapper()
        query = text("""
                     SELECT fh.iduc,
                            fh.idheader,
                            fh.tid,
                            fh.supervisor_name,
                            ft.idteam,
                            ft.team_no,
                            ft.team_member,
                            fc.day,
                            fc.house,
                            fc.name,
                            fc.gender,
                            fc.age,
                            fc.father,
                            fc.address,
                            fc.nofmc,
                            fc.reasontype,
                            fc.nodose,
                            fc.reject,
                            fc.location,
                            fc.hrmp,
                            fc.returndate,
                            fc.dateofvacc,
                            fc.enteredby,
                            fc.entereddate
                     FROM formheader fh
                              JOIN formteam ft
                                   ON fh.idheader = ft.idheader
                              JOIN formchildren fc
                                   ON ft.idteam = fc.idteam
                                       AND fc.idheader = fh.idheader
                     WHERE fh.iduc = ANY(:iducs)
                       AND fh.idcampaign = :idcampaign
                       AND fc.enteredby = :enteredby
                     """)

        try:
            result = await self.db.execute(query, {"iducs": tuple(iducs), "idcampaign": idcampaign, "enteredby": enteredby})
            rows = [dict(row._mapping) for row in result.fetchall()]

            if not rows:
                return {
                    "status_code": 404,
                    "content": {"success": False, "message": "No campaign data found", "data": []}
                }

            ucs = {}
            for row in rows:
                uc_id = row["iduc"]
                if uc_id not in ucs:
                    ucs[uc_id] = {"iduc": uc_id, "campaigns": {}}

                hid = row["idheader"]
                if hid not in ucs[uc_id]["campaigns"]:
                    ucs[uc_id]["campaigns"][hid] = {
                        "aic_identifier": row["idheader"],
                        "aic_id": row["tid"],
                        "aic_name": row["supervisor_name"],
                        "aicdata": {}
                    }

                team_id = row["idteam"]
                if team_id not in ucs[uc_id]["campaigns"][hid]["aicdata"]:
                    ucs[uc_id]["campaigns"][hid]["aicdata"][team_id] = {
                        "team_id": row["idteam"],
                        "team_no": row["team_no"],
                        "team_name": row["team_member"],
                        "children": []
                    }

                # child mapping
                child = {
                    "campaign_day": row["day"],
                    "house_no": row["house"],
                    "child_name": row["name"],
                    "gender": mapper.gender_to_string(int(row["gender"])) if row["gender"] is not None else None,
                    "age": int(row["age"]),
                    "father_name": row["father"],
                    "address": row["address"],
                    "miss_rounds": row["nofmc"],
                    "missedreason": None,
                    "subreason": None,
                    "location": row["location"],
                    "mmp": mapper.hrmp_to_string(int(row["hrmp"])) if row["hrmp"] is not None else None,
                    "expected_date_return": row["returndate"],
                    "vaccination_date": row["dateofvacc"],
                    "user_id": row["enteredby"],
                    "entered_date": row["entereddate"]
                }

                try:
                    child["missedreason"], child["subreason"] = mapper.to_strings(
                        int(row["nodose"]), int(row["reject"])
                    )
                except Exception:
                    child["missedreason"], child["subreason"] = None, None

                ucs[uc_id]["campaigns"][hid]["aicdata"][team_id]["children"].append(child)

            # restructure into list with campaigns + teams + children
            response_data = [
                {
                    "ucmo_id": uc_id,
                    "ucmo_name": uc_id,
                    "ucmodata": [
                        {
                            **campaign,
                            "aicdata": list(campaign["aicdata"].values())
                        }
                        for campaign in uc_data["campaigns"].values()
                    ]
                }
                for uc_id, uc_data in ucs.items()
            ]

            return {
                "success": True,
                "message": "Data Retrieve Successfully",
                "data":response_data
            }

        except SQLAlchemyError as e:
            return {
                "status_code": 500,
                "data": {"success": False, "message": "Database error", "details": str(e)}
            }

        except Exception as e:
            return {
                "status_code": 500,
                "data": {"success": False, "message": "Unexpected error", "details": str(e)}
            }

    async def get_campaign_id_by_name_mobile(self, name: str) -> dict:
        query = text("""
                     SELECT idcampaign
                     FROM campaign
                     WHERE name = :name LIMIT 1
                     """)

        try:
            result = await self.db.execute(query, {"name": name})
            row = result.fetchone()

            if not row:
                return {
                    "status_code": 404,
                    "content": {"success": False, "message": f"No campaign found with name '{name}'"}
                }

            return {
                "status_code": 200,
                "content": {"success": True, "message": "Campaign ID fetched", "idcampaign": row.idcampaign}
            }

        except SQLAlchemyError as e:
            return {
                "status_code": 500,
                "content": {"success": False, "message": "Database error", "details": str(e)}
            }

        except Exception as e:
            return {
                "status_code": 500,
                "content": {"success": False, "message": "Unexpected error", "details": str(e)}
            }

    async def get_formchildren_without_vacc(self, idheader: int):
        """
        Fetch all children records for a given header (idheader)
        where dateofvacc is null, joined with team info.
        """
        mapper = ReasonMapper()
        select_sql = text("""
                          SELECT a.idchildren,
                                 a.idheader,
                                 a.idteam,
                                 a.name,
                                 a.father,
                                 a.age,
                                 a.nodose,
                                 a.reject,
                                 a.house,
                                 a.hrmp,
                                 a.day,
                                 a.nofmc,
                                 a.returndate,
                                 a.gender,
                                 b.team_no
                          FROM formchildren a
                                   JOIN formteam b
                                        ON b.idteam = a.idteam
                                            AND a.idheader = b.idheader
                          WHERE a.idheader = :idheader
                            AND a.dateofvacc IS NULL
                          """)

        try:
            async with self.db.begin():
                result = await self.db.execute(select_sql, {"idheader": idheader})
                rows = result.fetchall()

                if not rows:
                    return {
                        "status": "error",
                        "message": f"No child records found for idheader={idheader} with null dateofvacc",
                        "data": []
                    }

                # convert rows to list of dicts
                columns = result.keys()
                data: List[Dict[str, Any]] = [dict(zip(columns, row)) for row in rows]
                for child in data:
                    # Apply mapping for gender
                    child["gender"] = mapper.gender_to_string(int(child["gender"])) if child["gender"] is not None else None

                    # Apply mapping for hrmp (renamed mmp in your code)
                    child["mmp"] = mapper.hrmp_to_string(int(child["hrmp"])) if child["hrmp"] is not None else None
                    child["age"] = int(child["age"])
                    # Apply mapping for nodose/reject → missedreason/subreason
                    if child["nodose"] is not None and child["reject"] is not None:
                        child["missedreason"], child["subreason"] = mapper.to_strings(
                            int(child["nodose"]), int(child["reject"])
                        )
                    else:
                        child["missedreason"], child["subreason"] = None, None

                key_map = {
                    "idchildren": "child_id",
                    "idheader": "aic_id",
                    "idteam": "team_id",
                    "name": "child_name",
                    "father": "father_name",
                    "age": "age_in_months",
                    "nodose": "nodose",
                    "reject": "reject",
                    "house": "house_number",
                    "hrmp": "hrmp",
                    "day": "day_number",
                    "nofmc": "no_of_missed_rounds",
                    "returndate": "expected_return_date",
                    "gender": "gender",
                    "team_no": "team_number",
                    "mmp": "mmp",
                    "missedreason": "missed_reason",
                    "subreason": "sub_reason",
                }
                data = [
                    {key_map.get(k, k): v for k, v in child.items()}
                    for child in data
                ]
                return {
                    "status": "success",
                    "message": f"Found {len(data)} child records for idheader={idheader}",
                    "data": data
                }

        except Exception as e:
            print(f"[ERROR] get_formchildren_without_vacc failed: {e}")
            return {
                "status": "error",
                "message": f"Unexpected error fetching child records: {str(e)}",
                "data": []
            }

    async def bulk_update_child_vaccination_dates(self, updates: list[dict], idusers: int):
        """
        Bulk update vaccination dates for multiple children.
        Each update item must be a dict: {"idchildren": int, "dateofvacc": "DD-MM-YYYY"}.
        Updates in a single transaction.
        """
        query_sql = text("""
                         UPDATE formchildren
                         SET dateofvacc  = :dateofvacc,
                             updateddate = NOW(),
                             updatedby   = :idusers
                         WHERE idchildren = :idchildren RETURNING idchildren;
                         """)

        updated_ids = []
        query_sql2 = text("""
                         SELECT fh.idheader, fh.iduc, fh.idcampaign, ft.idteam, ft.team_no, fc.idchildren,fc.age,fc.nofmc
                         FROM formheader fh
                                  JOIN formteam ft ON ft.idheader = fh.idheader
                                  JOIN formchildren fc ON fc.idheader = fh.idheader AND fc.idteam = ft.idteam
                         WHERE fc.idchildren = :idchildren;
                         """)

        campaign_insert_sql = text("""
                                   INSERT INTO campaign_child_wise_history (idcampaign, idchildren, is_pmc, is_smc,
                                                                            is_covered,
                                                                            updated_date, updated_by, idheader, idteam,
                                                                            age_at_campaign, iduc,no_miss_round)
                                   VALUES (:idcampaign, :idchildren, 0, 0, 1,
                                           NOW(), :updated_by, :idheader, :idteam, :age, :iduc,:no_miss_round) RETURNING id;
                                   """)
        # """select fh.idheader,fh.iduc,fh.idcampaign,ft.idteam,ft.team_no,fc.idchildren from formheader fh JOIN formteam ft ON ft.idheader=fh.idheader JOIN formchildren fc ON fc.idheader=fh.idheader and fc.idteam=ft.idteam where fc.idchildren=1391461"""

        try:
            async with self.db.begin():
                for item in updates:
                    result = await self.db.execute(query_sql, {
                        "idchildren": item["idchildren"],
                        "dateofvacc": datetime.strptime(item["dateofvacc"], "%d-%m-%Y").date(),
                        "idusers": idusers
                    })
                    row = result.fetchone()
                    if row:
                        result = await self.db.execute(query_sql2, {"idchildren": item["idchildren"]})
                        row = result.fetchone()
                        if not row:
                            continue

                        idheader, iduc, idcampaign, idteam, team_no, idchildren,age,nofmc = row

                        campaign_row = await self.db.execute(campaign_insert_sql, {
                            "idcampaign": idcampaign,
                            "idchildren": idchildren,
                            "updated_by": idusers,
                            "idheader": idheader,
                            "idteam": idteam,
                            "age": age,  # optional, can be None
                            "iduc": iduc,
                            "no_miss_round":nofmc
                        })

                        inserted_id = campaign_row.fetchone()[0]
                        updated_ids.append(row[0])

            if not updated_ids:
                return {
                    "status": "error",
                    "message": "No matching child records found to update.",
                    "updated_ids": []
                }

            return {
                "status": "success",
                "message": f"Updated vaccination dates for {len(updated_ids)} children",
                "updated_ids": updated_ids
            }

        except IntegrityError as e:
            return {
                "status": "error",
                "message": f"Integrity error during bulk update: {str(e.orig)}",
                "updated_ids": updated_ids
            }
        except SQLAlchemyError as e:
            print(f"[DB ERROR] bulk_update_child_vaccination_dates failed: {e}")
            return {
                "status": "error",
                "message": f"Database error: {str(e)}",
                "updated_ids": updated_ids
            }
        except Exception as e:
            print(f"[ERROR] bulk_update_child_vaccination_dates failed: {e}")
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}",
                "updated_ids": updated_ids
            }


    async def get_uc_campaign_summary(self, iduc: int, idcampaign: int):
        """
        Fetch UC-level campaign summary:
        - province/division/district/tehsil/uc hierarchy
        - campaign & supervisor info
        - distinct team count
        - distinct child count
        """

        query_sql = text("""
            SELECT
                p.idprovince       AS pid,
                p.name             AS pname,
                d.divid            AS divid,
                d.division         AS divname,
                dist.iddistrict    AS districtid,
                dist.name          AS districtname,
                tehsil.code        AS tehsilid,
                tehsil.name        AS tehsilname,
                uc.code            AS uccode,
                uc.name            AS ucname,
                fh.idcampaign      AS idcampaign,
                c.name             AS campaign_name,
                fh.supervisor_name AS supervisor_name,
                fh.tid             AS aicid,
                fh.idheader        AS aicheader,
                COUNT(DISTINCT ft.team_no)     AS totalteams,
                COUNT(DISTINCT fc.idchildren)  AS totalchildren,
                u.username AS username
            FROM formheader fh
            JOIN campaign_ucs cu
                ON fh.iduc = cu.iduc
            JOIN campaign c
                ON fh.idcampaign = c.idcampaign
            JOIN province p
                ON p.idprovince = LEFT(fh.iduc::TEXT, 1)::INT
            JOIN clean_divisions d
                ON d.dcode = LEFT(fh.iduc::TEXT, 3)::INT
            JOIN district dist
                ON dist.code = LEFT(fh.iduc::TEXT, 3)::INT
            JOIN location tehsil
                ON tehsil.code = LEFT(fh.iduc::TEXT, 5)::INT
            JOIN location uc
                ON uc.code = fh.iduc
            JOIN formteam ft
                ON fh.idheader = ft.idheader
            JOIN formchildren fc
                ON fh.idheader = fc.idheader
            JOIN users u
                ON u.idusers = fh.enteredby
            WHERE fh.iduc = :iduc
              AND fh.idcampaign = :idcampaign
            GROUP BY
                p.idprovince, p.name,
                d.divid, d.division,
                dist.iddistrict, dist.name,
                tehsil.code, tehsil.name,
                uc.code, uc.name,
                fh.idcampaign, c.name,
                fh.supervisor_name, fh.tid, fh.idheader,u.username
        """)

        try:
            async with self.db.begin():
                result = await self.db.execute(query_sql, {
                    "iduc": iduc,
                    "idcampaign": idcampaign
                })
                rows = result.fetchall()

            if not rows:
                return {
                    "status": "error",
                    "message": f"No campaign summary found for iduc={iduc}, idcampaign={idcampaign}",
                    "data": []
                }

            # Convert rows to list of dicts
            summary = [
                dict(row._mapping) for row in rows
            ]
            return {
                "status": "success",
                "message": f"Found {len(summary)} UC campaign summary records",
                "data": summary
            }

        except SQLAlchemyError as e:
            print(f"[DB ERROR] get_uc_campaign_summary failed: {e}")
            traceback.print_exc()
            return {
                "status": "error",
                "message": f"Database error: {str(e)}",
                "data": []
            }
        except Exception as e:
            print(f"[ERROR] get_uc_campaign_summary failed: {e}")
            traceback.print_exc()
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}",
                "data": []
            }

    async def get_uc_campaign_children(self, idheader: int, idcampaign: int):
        """
        Fetch child-level campaign data for a given header + campaign:
        - province/division/district/tehsil/uc hierarchy
        - campaign & supervisor info
        - child details (house, name, gender, father, etc.)
        """
        mapper=ReasonMapper()

        query_sql = text("""
                         SELECT p.idprovince       AS pid,
                                p.name             AS pname,
                                d.divid            AS divid,
                                d.division         AS divname,
                                dist.iddistrict    AS districtid,
                                dist.name          AS districtname,
                                tehsil.code        AS tehsilid,
                                tehsil.name        AS tehsilname,
                                uc.code            AS uccode,
                                uc.name            AS ucname,
                                fh.idcampaign      AS idcampaign,
                                c.name             AS campaign_name,
                                fh.supervisor_name AS supervisor_name,
                                fh.tid             AS aicid,
                                fh.idheader        AS aicheader,
                                fc.day AS day_number,
                                fc.idteam AS id_team,
                                fc.house AS house_number,
                                fc.name AS child_name,
                                fc.gender AS gender,
                                fc.age AS age,
                                fc.father AS father_name,
                                fc.address AS address,
                                fc.nofmc AS no_of_miss_round,
                                fc.reasontype AS reason_type,
                                fc.nodose AS nodose,
                                fc.reject AS reject,
                                fc.location AS location,
                                fc.hrmp AS hrmp,
                                fc.returndate AS return_data,
                                fc.dateofvacc AS data_vaccination,
                                fc.enteredby AS entered_by,
                                fc.entereddate AS entered_data,
                                u.username AS username
                         FROM formheader fh
                                  JOIN campaign_ucs cu
                                       ON fh.iduc = cu.iduc
                                  JOIN campaign c
                                       ON fh.idcampaign = c.idcampaign
                                  JOIN province p
                                       ON p.idprovince = LEFT (fh.iduc::TEXT, 1):: INT
                             JOIN clean_divisions d
                         ON d.dcode = LEFT (fh.iduc::TEXT, 3):: INT
                             JOIN district dist
                             ON dist.code = LEFT (fh.iduc::TEXT, 3):: INT
                             JOIN location tehsil
                             ON tehsil.code = LEFT (fh.iduc::TEXT, 5):: INT
                             JOIN location uc
                             ON uc.code = fh.iduc
                             JOIN formchildren fc
                             ON fh.idheader = fc.idheader
                             JOIN users u
                             ON u.idusers = fh.enteredby
                         WHERE fh.idheader = :idheader
                           AND fh.idcampaign = :idcampaign
                         GROUP BY
                             p.idprovince, p.name,
                             d.divid, d.division,
                             dist.iddistrict, dist.name,
                             tehsil.code, tehsil.name,
                             uc.code, uc.name,
                             fh.idcampaign, c.name,
                             fh.supervisor_name, fh.tid, fh.idheader, u.username,
                             fc.day,
                             fc.house,
                             fc.name,
                             fc.gender,
                             fc.age,
                             fc.father,
                             fc.address,
                             fc.nofmc,
                             fc.reasontype,
                             fc.nodose,
                             fc.reject,
                             fc.location,
                             fc.idteam,
                             fc.hrmp,
                             fc.returndate,
                             fc.dateofvacc,
                             fc.enteredby,
                             fc.entereddate
                         """)

        try:
            async with self.db.begin():
                result = await self.db.execute(query_sql, {
                    "idheader": idheader,
                    "idcampaign": idcampaign
                })
                rows = result.fetchall()

            if not rows:
                return {
                    "status": "error",
                    "message": f"No child-level data found for idheader={idheader}, idcampaign={idcampaign}",
                    "data": []
                }

            # Convert rows to list of dicts
            data = [dict(row._mapping) for row in rows]
            for child in data:
                # Apply mapping for gender
                child["gender"] = mapper.gender_to_string(int(child["gender"])) if child["gender"] is not None else None

                # Apply mapping for hrmp (renamed mmp in your code)
                child["mmp"] = mapper.hrmp_to_string(int(child["hrmp"])) if child["hrmp"] is not None else None

                # Apply mapping for nodose/reject → missedreason/subreason
                if child["nodose"] is not None and child["reject"] is not None:
                    child["missedreason"], child["subreason"] = mapper.to_strings(
                        int(child["nodose"]), int(child["reject"])
                    )
                else:
                    child["missedreason"], child["subreason"] = None, None


            return {
                "status": "success",
                "message": f"Found {len(data)} child records",
                "data": data
            }

        except SQLAlchemyError as e:
            print(f"[DB ERROR] get_uc_campaign_children failed: {e}")
            traceback.print_exc()
            return {
                "status": "error",
                "message": f"Database error: {str(e)}",
                "data": []
            }
        except Exception as e:
            print(f"[ERROR] get_uc_campaign_children failed: {e}")
            traceback.print_exc()
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}",
                "data": []
            }

    async def get_uc_campaign_smc_children_with_age(self, idcampaign: int, iduc: int):
        """
        Fetch child-level campaign data (excluding PMC children) with:
        - province/division/district/tehsil/uc hierarchy
        - campaign & supervisor info
        - child details (house, name, gender, father, etc.)
        - computed column: age in months + months since entereddate
        """

        mapper = ReasonMapper()
        get_campaign = text("""SELECT idcampaign, name
                                FROM campaign
                                WHERE idcampaign > :idcampaign
                                ORDER BY idcampaign ASC
                                LIMIT 1;""")
        try:
            async with self.db.begin():
                result = await self.db.execute(get_campaign, {
                    "idcampaign": idcampaign,
                })
                row = result.fetchone()
                if not row:
                    return {
                        "status": "error",
                        "message": "No next campaign found",
                        "idcampaign": idcampaign,
                        "iduc": iduc,
                    }
                idcampaign2, campaign_name = row

        except:
            return {
                "status": "error",
                "message": f"Database exception occured. Pls check",
                "idcampaign": idcampaign,
                "iduc": iduc,
            }


        first_half="""SELECT p.idprovince       AS province_id,
                                p.name             AS province_name,
                                d.divid            AS division_id,
                                d.division         AS division_name,
                                dist.iddistrict    AS district_id,
                                dist.name          AS district_name,
                                tehsil.code        AS tehsil_id,
                                tehsil.name        AS tehsil_name,
                                uc.code            AS uc_id,
                                uc.name            AS uc_name,
                                fh.idcampaign      AS id_campaign,
                                c.name             AS campaign_name,
                                fh.supervisor_name AS aic_name,
                                fh.idheader        AS aic_identifier,
                                fc.day             AS day_no,
                                fc.idchildren      AS id_child,
                                fc.idteam          AS id_team,
                                fc.house           AS house_no,
                                fc.name            AS child_name,
                                fc.gender          AS gender,
                                fc.age             AS age_in_months,
                                fc.father          AS father_name,
                                fc.address         AS address,
                                fc.nofmc           AS no_of_missing_round,
                                fc.reasontype      AS reason_type,
                                fc.nodose          AS missed_reason,
                                fc.reject          AS sub_reason,
                                fc.location        AS location,
                                fc.hrmp            AS mmp,
                                fc.returndate      AS return_date,
                                fc.dateofvacc      AS vaccination_date,
                                fc.enteredby       AS entered_by,
                                fc.entereddate     AS entered_date,
                                u.username         AS username,
                                :idcampaign AS  id_campaign_to_considered,

                                -- New column: age in months + months since entereddate
                                fc.age + (
                                    (EXTRACT(YEAR FROM AGE(CURRENT_DATE, fc.entereddate)) * 12)
                                        + EXTRACT(MONTH FROM AGE(CURRENT_DATE, fc.entereddate))
                                    )              AS age_plus_months_elapsed,"""
        second_half = """NULL AS previous_reported_pmc,False AS already_pmc,"""
        second_half2 = """(select name from campaign where idcampaign=:idcampaign) AS previous_reported_pmc,True AS already_pmc,"""
        third_half="""FROM formheader fh
                                  JOIN campaign_ucs cu
                                       ON fh.iduc = cu.iduc
                                  JOIN campaign c
                                       ON fh.idcampaign = c.idcampaign
                                  JOIN province p
                                       ON p.idprovince = LEFT (fh.iduc::TEXT, 1):: INT
                             JOIN clean_divisions d
                         ON d.dcode = LEFT (fh.iduc::TEXT, 3):: INT
                             JOIN district dist
                             ON dist.code = LEFT (fh.iduc::TEXT, 3):: INT
                             JOIN location tehsil
                             ON tehsil.code = LEFT (fh.iduc::TEXT, 5):: INT
                             JOIN location uc
                             ON uc.code = fh.iduc
                             JOIN formchildren fc
                             ON fh.idheader = fc.idheader
                             JOIN users u
                             ON u.idusers = fh.enteredby"""
        # fh.idheader =:idheader AND
        fourth_half="""WHERE fh.idcampaign = :idcampaign
                           AND fh.iduc = :iduc
                           AND fc.dateofvacc IS NULL
                           AND fc.idchildren NOT IN (
                             SELECT idchildren
                             FROM campaign_child_wise_history
                             WHERE is_pmc = 1 AND idcampaign=:idcampaign2
                             )"""
        fourth_half2 = """WHERE fh.iduc = :iduc
                                   AND fc.dateofvacc IS NULL
                                   AND fc.idchildren IN (
                                     SELECT idchildren
                                        FROM campaign_child_wise_history cch
                                        WHERE cch.is_pmc = 1
                                          AND cch.idcampaign = :idcampaign
                                          AND NOT EXISTS (
                                              SELECT 1
                                              FROM campaign_child_wise_history cch2
                                              WHERE cch2.idchildren = cch.idchildren
                                                AND cch2.is_pmc = 1
                                                AND cch2.idcampaign > :idcampaign
                                          )
                                     )"""
        fifth_half="""GROUP BY
                             p.idprovince, p.name,
                             d.divid, d.division,
                             dist.iddistrict, dist.name,
                             tehsil.code, tehsil.name,
                             uc.code, uc.name,
                             fh.idcampaign, c.name,
                             fh.supervisor_name, fh.tid, fh.idheader, u.username,
                             fc.day, fc.idchildren,
                             fc.house,
                             fc.name,
                             fc.gender,
                             fc.age,
                             fc.father,
                             fc.address,
                             fc.nofmc,
                             fc.reasontype,
                             fc.nodose,
                             fc.reject,
                             fc.location, fc.idteam,
                             fc.hrmp,
                             fc.returndate,
                             fc.dateofvacc,
                             fc.enteredby,
                             fc.entereddate"""
        query_sql = text(f"""
        (
            {first_half}
            {second_half}
            :campaign_name AS report_pmc_for
            {third_half}
            {fourth_half}
            {fifth_half}
        )
        UNION ALL
        (
            {first_half}
            {second_half2}
            :campaign_name AS report_pmc_for
            {third_half}
            {fourth_half2}
            {fifth_half}
        )
        """)

        try:
            async with self.db.begin():
                result = await self.db.execute(query_sql, {
                    "idcampaign":idcampaign,
                    "campaign_name":campaign_name,
                    "iduc": iduc,
                    "idcampaign2":idcampaign2
                })
                rows = result.fetchall()


            if not rows:
                return {
                    "status": "error",
                    "message": f"No eligible child-level data found for iduc={iduc}",
                    "data": []
                }

            data = [dict(row._mapping) for row in rows]
            geo_keys = [
                "province_id", "province_name",
                "division_id", "division_name",
                "district_id", "district_name",
                "tehsil_id", "tehsil_name",
                "uc_id", "uc_name"
            ]
            levels = ["province", "division", "district", "tehsil", "uc"]
            geo_info = {
                level: {
                    "id": data[0][f"{level}_id"],
                    "name": data[0][f"{level}_name"]
                }
                for level in levels
            }
            for child in data:
                for k in geo_keys:
                    child.pop(k, None)
                # Gender mapping
                child["gender"] = mapper.gender_to_string(int(child["gender"])) if child["gender"] is not None else None

                # HRMP → MMP mapping
                child["mmp"] = mapper.hrmp_to_string(int(child["mmp"])) if child["mmp"] is not None else None

                # Missed + subreason mapping
                if child["missed_reason"] is not None and child["sub_reason"] is not None:
                    child["missed_reason"], child["sub_reason"] = mapper.to_strings(
                        int(child["missed_reason"]), int(child["sub_reason"])
                    )
                else:
                    child["missed_reason"], child["sub_reason"] = None, None

            return {
                "status": "success",
                "message": f"Found {len(data)} child records (excluding PMC)",
                "data": {"geo_information":geo_info,"child_data":data}
            }

        except SQLAlchemyError as e:
            print(f"[DB ERROR] get_uc_campaign_children_with_age failed: {e}")
            traceback.print_exc()
            return {
                "status": "error",
                "message": f"Database error: {str(e)}",
                "data": []
            }
        except Exception as e:
            print(f"[ERROR] get_uc_campaign_children_with_age failed: {e}")
            traceback.print_exc()
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}",
                "data": []
            }

    async def bulk_update_child_pmc_status(self, updates: list[dict], idusers: int,idcampaign: int):
        get_campaign = text("""SELECT idcampaign
                                FROM campaign
                                WHERE idcampaign > :idcampaign
                                ORDER BY idcampaign ASC
                                LIMIT 1;""")
        try:
            async with self.db.begin():
                result = await self.db.execute(get_campaign, {
                    "idcampaign": idcampaign,
                })
                row = result.fetchone()
                if not row:
                    return {
                        "status": "error",
                        "message": "No next campaign found",
                    }
                next_campaign = row

        except:
            return {
                "status": "error",
                "message": f"Database exception occured. Pls check",
                "idcampaign": idcampaign,
            }
        updated_ids = []
        query_sql2 = text("""
                          SELECT fh.idheader, fh.iduc, ft.idteam, ft.team_no, fc.idchildren,fc.nofmc
                          FROM formheader fh
                                   JOIN formteam ft ON ft.idheader = fh.idheader
                                   JOIN formchildren fc ON fc.idheader = fh.idheader AND fc.idteam = ft.idteam
                          WHERE fc.idchildren = :idchildren;
                          """)

        campaign_insert_sql = text("""
                                   INSERT INTO campaign_child_wise_history (idcampaign, idchildren, is_pmc, is_smc,
                                                                            is_covered,
                                                                            updated_date, updated_by, idheader, idteam,
                                                                            age_at_campaign, iduc,no_miss_round)
                                   VALUES (:idcampaign, :idchildren, 1, 0, 0,
                                           NOW(), :updated_by, :idheader, :idteam, :age, :iduc,:no_miss_round) RETURNING id;
                                   """)
        # """select fh.idheader,fh.iduc,fh.idcampaign,ft.idteam,ft.team_no,fc.idchildren from formheader fh JOIN formteam ft ON ft.idheader=fh.idheader JOIN formchildren fc ON fc.idheader=fh.idheader and fc.idteam=ft.idteam where fc.idchildren=1391461"""

        try:
            async with self.db.begin():
                for item in updates:

                    result = await self.db.execute(query_sql2, {"idchildren": item["idchildren"]})
                    row = result.fetchone()
                    if not row:
                        continue

                    idheader, iduc, idteam, team_no, idchildren, nofmc = row
                    campaign_row = await self.db.execute(campaign_insert_sql, {
                        "idcampaign": next_campaign[0],
                        "idchildren": item["idchildren"],
                        "updated_by": idusers,
                        "idheader": idheader,
                        "idteam": idteam,
                        "age": item["age"],  # optional, can be None
                        "iduc": iduc,
                        "no_miss_round":int(nofmc)+1
                    })

                    inserted_id = campaign_row.fetchone()[0]
                    updated_ids.append(inserted_id)

            if not updated_ids:
                return {
                    "status": "error",
                    "message": "No matching child records found to update.",
                    "updated_ids": []
                }

            return {
                "status": "success",
                "message": f"Updated vaccination dates for {len(updated_ids)} children",
                "updated_ids": updated_ids
            }

        except IntegrityError as e:
            return {
                "status": "False",
                "message": f"Integrity error during bulk update",
                "updated_ids": updated_ids
            }
        except SQLAlchemyError as e:
            print(f"[DB ERROR] bulk_update_child_vaccination_dates failed")
            return {
                "status": "False",
                "message": f"Database error: {str(e)}",
                "updated_ids": updated_ids
            }
        except Exception as e:
            print(f"[ERROR] bulk_update_child_vaccination_dates failed")
            return {
                "status": "False",
                "message": f"Unexpected error",
                "updated_ids": updated_ids
            }


class ReasonMapper:
    def __init__(self):
        # master mapping: reason -> id + subreasons
        self.mapping = {
            "NotAvailable": {
                "id": 2,
                "subs": {
                    "In School": 8,
                    "Inside District": 9,
                    "Outside District": 10,
                    "Sleeping": 11,
                    "Inside UC":15
                }
            },
            "Refusal": {
                "id": 1,
                "subs": {
                    "Religious Matter": 1,
                    "Misconception": 12,
                    "Safety": 2,
                    "Demands": 3,
                    "Repeated Campaigns": 4,
                    "Direct Refusal": 5,
                    "Sickness": 6,
                    "Silent Refusal": 13
                }
            },
            "LockedHouse": {
                "id": 5,
                "subs": {"Not Needed":0}  # no sub reasons
            }
        }

        # gender + hrmp mappings added here
        self.gender_map = {
            "Not Mentioned": 0,
            "Male": 1,
            "Female": 2,
            "Preferred Not To Say": 3
        }
        self.gender_reverse = {v: k for k, v in self.gender_map.items()}

        self.hrmp_map = {
            "Yes": 1,
            "No": 2,
            "Null": 0,
        }
        self.hrmp_reverse = {v: k for k, v in self.hrmp_map.items()}

        # reverse lookup: id -> reason + sub
        self.reverse_mapping = {}
        for reason, data in self.mapping.items():
            rid = data["id"]
            self.reverse_mapping[rid] = {
                "name": reason,
                "subs": {sid: sname for sname, sid in data["subs"].items()}
            }

    def to_ids(self, reason: str, subreason: str = None):
        """Convert reason/subreason string to ids."""
        if reason not in self.mapping:
            raise ValueError(f"Unknown reason: {reason}")

        reason_id = self.mapping[reason]["id"]
        if subreason:
            subs = self.mapping[reason]["subs"]
            if subreason not in subs:
                raise ValueError(f"Unknown subreason '{subreason}' for reason '{reason}'")
            return reason_id, subs[subreason]

        return reason_id, None

    def to_strings(self, reason_id: int, subreason_id: int = None):
        """Convert reason/subreason ids back to strings."""
        if reason_id not in self.reverse_mapping:
            raise ValueError(f"Unknown reason_id: {reason_id}")

        reason_name = self.reverse_mapping[reason_id]["name"]
        if subreason_id:
            subs = self.reverse_mapping[reason_id]["subs"]
            if subreason_id not in subs:
                raise ValueError(f"Unknown subreason_id '{subreason_id}' for reason_id '{reason_id}'")
            return reason_name, subs[subreason_id]

        return reason_name, None

    # gender helpers
    def gender_to_id(self, gender: str) -> int:
        if gender not in self.gender_map:
            raise ValueError(f"Unknown gender: {gender}")
        return self.gender_map[gender]

    def gender_to_string(self, gid: int) -> str:
        if gid not in self.gender_reverse:
            raise ValueError(f"Unknown gender id: {gid}")
        return self.gender_reverse[gid]

    # hrmp helpers
    def hrmp_to_id(self, value: str) -> int:
        if value not in self.hrmp_map:
            raise ValueError(f"Unknown hrmp: {value}")
        return self.hrmp_map[value]

    def hrmp_to_string(self, vid: int) -> str:
        if vid not in self.hrmp_reverse:
            raise ValueError(f"Unknown hrmp id: {vid}")
        return self.hrmp_reverse[vid]


# Test Run for the Mapping Reasons for Web and Mobile
# mapper = ReasonMapper()

# String -> IDs
# print(mapper.to_ids("NotAvailable", "In School"))
# ➝ (2, 8)

# print(mapper.to_ids("Refusal", "Misconception"))
# ➝ (1, 12)

# IDs -> Strings
# print(mapper.to_strings(2, 8))
# ➝ ("NotAvailable", "In School")

# print(mapper.to_strings(1, 12))
# ➝ ("Refusal", "Misconception")

