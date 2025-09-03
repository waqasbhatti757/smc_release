from fastapi import APIRouter, Depends, Request, HTTPException
from starlette import status
from . import models, service
from fastapi.security import OAuth2PasswordRequestForm
from ..database.core import DbSession
import logging
from ..rate_limiter import limiter
import time
from sqlalchemy.exc import SQLAlchemyError
from .service import EOCClient,CampaignService
from .models import *


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
