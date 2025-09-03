from fastapi import APIRouter, Depends, Request, HTTPException
from starlette import status
from . import models, service
from fastapi.security import OAuth2PasswordRequestForm
from ..database.core import DbSession
import logging
from ..rate_limiter import limiter
import time
from sqlalchemy.exc import SQLAlchemyError
from .service import EOCClient,CampaignService,ReasonMapper
from .models import *
from typing import Dict, Any


router = APIRouter(
    prefix='/campaign',
    tags=['campaign']
)
logger = logging.getLogger("uvicorn")

@router.post("/synccampaign", response_model=SyncCampaignResponse)
async def sync_latest_campaign(payload: SyncCampaignRequest, db: DbSession):
    client = EOCClient()

    # Fetch campaigns from API
    campaigns = await client.get_campaign_list(limit=1)
    if not campaigns:
        return {"status": False, "message": "No campaigns found"}

    # Insert only the first campaign
    first_campaign = campaigns[0]
    result = await client.insert_campaign(db, [first_campaign], payload.idusers)
    return result


@router.get("/campaigns/summary")
async def campaign_summary_controller(db: DbSession):
    service = CampaignService(db)
    return await service.get_summary()


@router.post("/campaign/update-status")
async def update_campaign_controller(
    payload: UpdateCampaignPayload,
    db: DbSession):
    service = CampaignService(db)
    return await service.update_campaign_status(
        idcampaign=payload.idcampaign,
        type_field=payload.type_field,
        status=payload.status
    )



@router.get("/campaigns/list")
async def campaign_list(db: DbSession):
    """
    API endpoint to get campaigns (idcampaign, name).
    """
    service = CampaignService(db)
    result = await service.get_campaign_list()

    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))

    return result


@router.post("/campaign/locations")
async def get_locations(payload: CampaignDataRequest, db: DbSession):
    """
    API endpoint to fetch provinces, divisions, districts for campaign.
    """
    service = CampaignService(db)
    result = await service.get_province_division_district(idcampaign=payload.idcampaign,type_field_camp=payload.type_field)

    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))

    return result


@router.get("/campaign/{idcampaign}/provinces")
async def get_campaign_provinces(idcampaign: int, db: DbSession):
    """
    Endpoint to fetch provinces for a single campaign.
    """
    service = CampaignService(db)
    result = await service.get_provinces_for_campaign(idcampaign)
    return result

@router.post("/campaign/divisions")
async def fetch_divisions(payload: CampaignDDDataRequest,
    db: DbSession
):
    service = CampaignService(db)
    response = await service.get_divisions_for_campaign_and_provinces(
        province_ids=payload.ids,
        campaign_ids=payload.idcampaign,
    )
    return response


@router.post("/campaign/districts")
async def fetch_divisions(payload: CampaignDDDataRequest,
    db: DbSession
):
    service = CampaignService(db)
    response = await service.get_districts_for_campaign(
        division_ids=payload.ids,
        campaign_id=payload.idcampaign,
    )
    return response


@router.get("/campaign/{idcampaign}/details")
async def get_campaign_provinces(idcampaign: int, db: DbSession):
    """
    Endpoint to fetch provinces for a single campaign.
    """
    service = CampaignService(db)
    result = await service.get_campaign_active_info(idcampaign)
    return result



@router.post("/campaign/planning/updates")
async def update_planning_campaign(payload: CampaignUpdatePayload, db: DbSession):
    service = CampaignService(db)
    result = await service.save_plan(plans=payload.plans,campaignid=payload.campaignid,iduser=payload.updated_by)
    return result


@router.post("/campaign/aic/provinces")
async def geo_provinces_for_aic(payload: AICProvincePayload, db: DbSession):
    service = CampaignService(db)
    result = await service.get_provinces_info_for_campaign(idcampaign=payload.campaignid,idprovince=payload.geoid)
    return result


@router.post("/campaign/aic/division")
async def geo_division_for_aic(payload: AICDivisionPayload, db: DbSession):
    service = CampaignService(db)
    result = await service.get_divisions_info_for_campaign(idcampaign=payload.campaignid,idprovince=payload.geoprovid,iddivision=payload.geodivid)
    return result

@router.post("/campaign/aic/district")
async def geo_district_for_aic(payload: AICDistrictPayload, db: DbSession):
    service = CampaignService(db)
    result = await service.get_districts_info_for_campaign(idcampaign=payload.campaignid,iddivision=payload.geodivid,dcode=payload.geodisid)
    return result


@router.post("/campaign/aic/tehsil")
async def geo_tehsil_for_aic(payload: AICTehsilPayload, db: DbSession):
    service = CampaignService(db)
    result = await service.get_tehsils_info_for_campaign(idcampaign=payload.campaignid, dcode=payload.geodisid, lcode=payload.geotehid)
    return result


@router.post("/campaign/aic/ucs")
async def geo_ucs_for_aic(payload: AICUCSPayload, db: DbSession):
    service = CampaignService(db)
    result = await service.get_ucs_info_for_campaign(idcampaign=payload.campaignid, tehcode=payload.geotehid, uc_codes = payload.geoucid)
    return result


@router.post("/campaign/createheader")
async def create_header_for_campaign(payload: CreateAICHeader, db: DbSession):
    service = CampaignService(db)
    result = await service.create_formheader(idcampaign=payload.idcampaign,iduc=payload.iduc,supervisor_name=payload.supervisor_name,enteredby=payload.enteredby)
    return result


@router.post("/campaign/updateheader")
async def create_header_for_campaign(payload: UpdateAICHeader, db: DbSession):
    service = CampaignService(db)
    result = await service.update_formheader(idcampaign=payload.idcampaign,iduc=payload.iduc,supervisor_name=payload.supervisor_name,enteredby=payload.enteredby,idheader = payload.supervisor_id)
    return result


@router.post("/campaign/createteam")
async def create_team_for_campaign(payload: CreateTeamPayload, db: DbSession):
    service = CampaignService(db)
    result = await service.create_formteam(idheader = payload.idheader,team_no=payload.team_no,
                                           team_member=payload.team_member,enteredby=payload.enteredby,
                                           teamtype = payload.teamtype)
    return result


@router.post("/campaign/updateteam")
async def update_team_for_campaign(payload: UpdateTeamPayload, db: DbSession):
    service = CampaignService(db)
    result = await service.update_formteam(idteam=payload.idteam, team_no=payload.team_no, team_member=payload.team_member)
    return result



@router.post("/campaign/get/teamdata")
async def get_team_data_for_table(idheader, db: DbSession):
    service = CampaignService(db)
    result = await service.get_formteam_by_header(int(idheader))
    return result


@router.post("/campaign/get/setentryheader")
async def set_child_data_entry_header(idheader, db: DbSession):
    service = CampaignService(db)
    result = await service.get_team_options(int(idheader))
    return result


@router.post("/campaign/add/childata")
async def add_child_data_for_campaign(payload: InsertChildDataPayload, db: DbSession):
    service = CampaignService(db)
    payload_dict = payload.model_dump()
    mapper = ReasonMapper()

    if payload_dict["nodose"] == "LockedHouse":
        payload_dict["reject"] = "Not Needed"

    payload_dict["nodose"], payload_dict["reject"] = mapper.to_ids(payload_dict["nodose"], payload_dict["reject"])

    payload_dict["gender"] = mapper.gender_to_id(payload_dict["gender"])
    payload_dict["hrmp"] = mapper.hrmp_to_id(payload_dict["hrmp"])

    result = await service.insert_formchildren(payload_dict)
    return result


@router.post("/campaign/get/childata")
async def get_child_data_for_campaign(payload:GetChildPayload, db: DbSession):
    service = CampaignService(db)
    # payload_dict = payload.model_dump()
    mapper = ReasonMapper()
    # payload_dict["nodose"], payload_dict["reject"] = mapper.to_ids(payload_dict["nodose"], payload_dict["reject"])
    # payload_dict["gender"] = mapper.gender_to_id(payload_dict["gender"])
    # payload_dict["hrmp"] = mapper.hrmp_to_id(payload_dict["hrmp"])

    result = await service.get_children_by_header_and_team(idheader=payload.idheader,idteam=payload.idteam)
    for rr in result['data']:
        rr["nodose"], rr["reject"] = mapper.to_strings(rr["nodose"],rr["reject"])
        rr["gender"] = mapper.gender_to_string(rr["gender"])
        rr["hrmp"] = mapper.hrmp_to_string(rr["hrmp"])

    return result

@router.get("/campaign/get/childata/{idchildren}")
async def get_child_by_id(idchildren: int, db: DbSession):
    service = CampaignService(db)
    mapper = ReasonMapper()
    result = await service.get_formchild_by_id(idchildren=idchildren)
    result["data"]["nodose"], result["data"]["reject"] = mapper.to_strings(result["data"]["nodose"], result["data"]["reject"])
    result["data"]["gender"] = mapper.gender_to_string(result["data"]["gender"])
    result["data"]["hrmp"] = mapper.hrmp_to_string(result["data"]["hrmp"])

    return result


@router.put("/update/{idchildren}")
async def update_child(idchildren: int, payload: UpdateChildDataPayload, db: DbSession):
    try:
        service = CampaignService(db)
        payload_dict = payload.model_dump()
        mapper = ReasonMapper()

        if payload_dict["nodose"] == "LockedHouse":
            payload_dict["reject"] = "Not Needed"

        payload_dict["nodose"], payload_dict["reject"] = mapper.to_ids(payload_dict["nodose"], payload_dict["reject"])

        payload_dict["gender"] = mapper.gender_to_id(payload_dict["gender"])
        payload_dict["hrmp"] = mapper.hrmp_to_id(payload_dict["hrmp"])
        print(payload_dict)
        result = await service.update_formchildren(idchildren=idchildren, payload=payload_dict)
        if result["status"] != "success":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")



@router.post("/campaign/get/aicdata")
async def get_aic_data_for_campaign(idcampaign: int, iduc: int, db: DbSession):
    service = CampaignService(db)
    result = await service.get_formheaders_by_campaign_uc(idcampaign=idcampaign, iduc=iduc)
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result


@router.post("/mobile/get/aicdata")
async def get_aic_data_for_campaign_mobile(idcampaign: int, iduc: int, db: DbSession):
    service = CampaignService(db)
    result = await service.get_formheaders_by_campaign_uc(idcampaign=idcampaign, iduc=iduc)
    for r in result['data']:
        r['aic_identifier'] = r.pop('idheader', None)
        r['aic_name'] = r.pop('supervisor_name', None)
        r.pop('tid', None)

    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result


@router.post("/campaign/get/aicheaderdata")
async def get_aic_header_data_for_campaign(tid: str, db: DbSession):
    service = CampaignService(db)
    result = await service.get_formheader_details_by_tid(tid)
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result



@router.post("/mobile/add/multi-child-data")
async def get_aic_header_data_for_campaign(payload: CombinedPayloadMobile, db: DbSession):
    service = CampaignService(db)
    mapper = ReasonMapper()
    header = payload.header.to_standard()
    team = payload.team.to_standard()
    child_list = [c.to_standard() for c in payload.child]

    payload = {
        "header": header.model_dump(),
        "team": team.model_dump(),
        "child": [c.model_dump() for c in child_list],
    }
    print(payload)
    result = await service.create_formheader(idcampaign= payload["header"]["idcampaign"], iduc= payload["header"]["iduc"], supervisor_name= payload["header"]["supervisor_name"], enteredby= payload["header"]["enteredby"])
    idheader = result['idheader']
    result = await service.create_formteam(idheader=idheader, team_no=payload["team"]["team_no"],
                                           team_member=payload["team"]["team_member"],
                                           enteredby=payload["header"]["enteredby"], teamtype=1)

    idteam = result['idteam']
    for rr in payload['child']:
        rr['idheader'] = idheader
        rr['idteam'] = idteam
        rr["nodose"], rr["reject"] = mapper.to_ids(rr["nodose"],rr["reject"])
        rr["gender"] = mapper.gender_to_id(rr["gender"])
        rr["hrmp"] = mapper.hrmp_to_id(rr["hrmp"])


    result = await service.insert_bulk_formchildren(payloads= payload['child'])
    result['idheader'] = idheader
    result['idteam'] = idteam
    return result




@router.post("/mobile/get/aic-data")
async def get_uc_data_for_campaign(payload: GetUCMOData, db: DbSession):
    service = CampaignService(db)
    result = await service.get_campaign_id_by_name_mobile(payload.campaignname)
    result = await service.get_campaign_nested(iducs= payload.iduc,idcampaign= int(result['content']['idcampaign']),enteredby=payload.enteredby)
    return result


@router.post("/get/unvaccinated-child-data")
async def get_uc_data_for_campaign(aic_identifier:int, db: DbSession):
    service = CampaignService(db)
    result = await service.get_formchildren_without_vacc(aic_identifier)
    return result


@router.post("/update/child-vaccination-date")
async def update_child_vaccination_date(payload:UpdateVaccinationDate, db: DbSession):
    service = CampaignService(db)
    result = await service.bulk_update_child_vaccination_dates(updates=payload.updates, idusers=payload.idusers)
    return result


@router.post("/read/smc-sheet-stats")
async def read_smc_filled_sheet_stats(payload:GetSMCSheetStats, db: DbSession):
    service = CampaignService(db)
    result = await service.get_uc_campaign_summary(iduc=payload.iduc, idcampaign=payload.idcampaign)
    return result



@router.post("/read/smc-aic-child-stats")
async def get_uc_campaign_children(payload:GetAICSheetData, db: DbSession):
    service = CampaignService(db)
    result = await service.get_uc_campaign_children(idheader=payload.idheader, idcampaign=payload.idcampaign)
    return result


@router.post("/read/smc_persistent_child")
async def get_persistently_missed_smc(campaign_id:int,uc_id:int, db: DbSession):
    service = CampaignService(db)
    result = await service.get_uc_campaign_smc_children_with_age(idcampaign=campaign_id,iduc=uc_id)
    return result



@router.post("/add/status/pmc/child")
async def set_pmc_status(payload:UpdatePMCStatus, db: DbSession):
    service = CampaignService(db)
    payload = payload.model_dump()

    result = await service.bulk_update_child_pmc_status(updates=payload['child_data'], idusers=payload['user_id'],idcampaign=payload['campaign_id'])
    return result


