from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any


class LocationModel:
    @staticmethod
    async def get_provinces(db: AsyncSession) -> List[Dict[str, Any]]:
        query = text("SELECT code, name FROM location WHERE type = 2 AND status = 1 ORDER BY name ASC")
        result = await db.execute(query)
        return [dict(row._mapping) for row in result.fetchall()]

    @staticmethod
    async def get_divisions(db: AsyncSession, province_code: int) -> List[Dict[str, Any]]:
        query = text("""
                     SELECT DISTINCT
                     ON (d.divid)
                         d.divid AS division_id,
                         d.division AS division_name
                     FROM clean_divisions d
                         JOIN location l
                     ON l.code = d.provid AND l.status = 1
                     WHERE d.provid = :province
                     ORDER BY d.divid, d.division;
                     """)
        result = await db.execute(query, {"province": province_code})
        return [dict(row._mapping) for row in result.fetchall()]

    @staticmethod
    async def get_districts(db: AsyncSession, division_code: int) -> List[Dict[str, Any]]:
        query = text("""
                     SELECT l.code,
                            l.dname
                     FROM district d
                              JOIN location l ON l.code = d.code AND l.status = 1
                              JOIN divisions dv ON dv.divid = d.divid
                     WHERE d.divid = :division
                     GROUP BY l.code, l.dname
                     ORDER BY l.code;
                     """)
        result = await db.execute(query, {"division": division_code})
        return [dict(row._mapping) for row in result.fetchall()]

    @staticmethod
    async def get_tehsils(db: AsyncSession, district_code: int) -> List[Dict[str, Any]]:
        query = text("""
                     SELECT l.name AS tname, l.code
                     FROM location AS l
                              JOIN district AS d ON d.code = LEFT (CAST (l.code AS TEXT), 3):: INT
                         JOIN province AS p
                     ON d.province_idprovince = p.idprovince
                     WHERE d.code = :district
                       AND l.type = 4
                       AND l.status = 1
                     GROUP BY l.code, l.name
                     ORDER BY l.name ASC
                     """)
        result = await db.execute(query, {"district": district_code})
        return [dict(row._mapping) for row in result.fetchall()]

    @staticmethod
    async def get_divisions_by_province(db: AsyncSession, province_code: int):
        query = text("""
                     SELECT DISTINCT
                     ON (d.divid)
                         d.divid AS division_id,
                         d.division AS division_name
                     FROM clean_divisions d
                         JOIN location l
                     ON l.code = d.provid AND l.status = 1
                     WHERE d.provid = :province
                     ORDER BY d.divid, d.division;
                     """)
        result = await db.execute(query, {"province": province_code})
        return [dict(row._mapping) for row in result.fetchall()]

    @staticmethod
    async def get_districts_by_division(db: AsyncSession, division_code: int):
        query = text("""
                     SELECT l.code,
                            l.dname
                     FROM district d
                              JOIN location l ON l.code = d.code AND l.status = 1
                              JOIN divisions dv ON dv.divid = d.divid
                     WHERE d.divid = :division
                     GROUP BY l.code, l.dname
                     ORDER BY l.code;
                     """)
        result = await db.execute(query, {"division": division_code})
        return [dict(row._mapping) for row in result.fetchall()]

    @staticmethod
    async def get_tehsil_by_district(db: AsyncSession, district_code: int):
        query = text("""
                     SELECT l.name AS tname, l.code
                     FROM location AS l
                              JOIN district AS d ON d.code = LEFT (CAST (l.code AS TEXT), 3):: INT
                         JOIN province AS p
                     ON d.province_idprovince = p.idprovince
                     WHERE d.code = :district
                       AND l.type = 4
                       AND l.status = 1
                     GROUP BY l.code, l.name
                     ORDER BY l.name;
                     """)
        result = await db.execute(query, {"district": district_code})
        return [dict(row._mapping) for row in result.fetchall()]

    @staticmethod
    async def get_ucs_by_tehsil(db: AsyncSession, tehsil_code: int):
        query = text("""
                     SELECT l.code,
                            l.name || ' (' || l.tname || ')' AS uctname
                     FROM location l
                     WHERE LEFT ('' || l.code
                         , 5):: INT IN (:tehsil)
                       AND l.type = 5
                       AND l.status = 1
                     ORDER BY l.code, l.tname;
                     """)
        result = await db.execute(query, {"tehsil": tehsil_code})
        return [dict(row._mapping) for row in result.fetchall()]
