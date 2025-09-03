from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from typing import List
from typing import Optional
from datetime import date


class SyncCampaignRequest(BaseModel):
    jwt_token: str
    idusers: int = 1


class SyncCampaignResponse(BaseModel):
    status: bool
    code: int
    campaign_id: int
    message: Optional[str] = None
    campaign: Optional[dict] = None


class UpdateCampaignPayload(BaseModel):
    idcampaign: int
    type_field: str  # "plan", "insert", "update", or "delete"
    status: int      # 0 or 1

class CampaignDataRequest(BaseModel):
    idcampaign: int
    type_field:str

class CampaignDDDataRequest(BaseModel):
    idcampaign: int
    ids:List[int]

class CampaignUpdatePayload(BaseModel):
    campaignid: int
    plans:List
    updated_by:int

class AICProvincePayload(BaseModel):
    campaignid: int
    geoid: Optional[int] = None

class AICDivisionPayload(BaseModel):
    campaignid: int
    geoprovid: int
    geodivid: Optional[int] = None

class AICDistrictPayload(BaseModel):
    campaignid: int
    geodivid: int
    geodisid: Optional[int] = None


class AICTehsilPayload(BaseModel):
    campaignid: int
    geodisid: int
    geotehid: Optional[int] = None


class AICUCSPayload(BaseModel):
    campaignid: int
    geotehid: int
    geoucid: Optional[list[int]] = None


class CreateAICHeader(BaseModel):
    idcampaign: int
    iduc: int
    supervisor_name: str
    supervisor_full_name: Optional[str] = None
    enteredby: int

class CreateAICHeaderMobile(BaseModel):
    campaign_id: int
    ucmo_id: int
    aic_name: str
    user_id: int
    supervisor_full_name:Optional[str] = None
    def to_standard(self) -> CreateAICHeader:
        return CreateAICHeader(
            idcampaign=self.campaign_id,
            iduc=self.ucmo_id,
            supervisor_name=self.aic_name,
            enteredby=self.user_id,
            supervisor_full_name=self.supervisor_full_name
        )

class UpdateAICHeader(BaseModel):
    idcampaign: int
    iduc: int
    supervisor_name: str
    supervisor_full_name: str
    enteredby: int
    supervisor_id: int

class CreateTeamPayload(BaseModel):
    idheader: Optional[int] = None
    team_no: str
    team_member: Optional[str] = None
    enteredby: Optional[int] = None
    teamtype: int = 1


class CreateTeamPayloadMobile(BaseModel):
    aicid: Optional[int] = None
    team_name: str
    team_id: Optional[str] = None
    user_id: Optional[int] = None
    teamtype: int = 1

    def to_standard(self) -> CreateTeamPayload:
        return CreateTeamPayload(
            idheader=self.aicid,
            team_no=self.team_name,
            team_member=self.team_id,
            enteredby=self.user_id,
            teamtype=self.teamtype,
        )


class UpdateTeamPayload(BaseModel):
    idteam: int
    team_no: str
    team_member: str


class InsertChildDataPayload(BaseModel):
    idheader: Optional[int] = None
    idteam: Optional[int] = None
    day: int
    house: str
    name: str
    gender: str
    age: int
    father: str
    address: str
    nofmc: int
    reasontype: Optional[str] = None
    nodose: str
    reject: str
    location: Optional[str] = None
    hrmp: Optional[str] = None
    returndate: Optional[date] = None
    dateofvacc: Optional[date] = None
    idusers: int


class InsertChildDataPayloadMobile(BaseModel):
    idheader: Optional[int] = None
    idteam: Optional[int] = None
    day: int
    house: str
    name: str
    gender: str
    age: int
    father: str
    address: str
    nofmc: int
    reasontype: Optional[str] = None
    missedreason: str
    subreason: str
    location: Optional[str] = None
    mmp: Optional[str] = None
    return_date: Optional[date] = None
    date_of_vacc: Optional[date] = None
    user_id: int

    def to_standard(self) -> InsertChildDataPayload:
        return InsertChildDataPayload(
            idheader=self.idheader,
            idteam=self.idteam,
            day=self.day,
            house=self.house,
            name=self.name,
            gender=self.gender,
            age=self.age,
            father=self.father,
            address=self.address,
            nofmc=self.nofmc,
            reasontype=self.reasontype,
            nodose=self.missedreason,  # mapping subreason → nodose
            reject=self.subreason,  # mapping missedreason → reject
            location=self.location,
            hrmp=self.mmp,
            returndate=self.return_date,
            dateofvacc=self.date_of_vacc,
            idusers=self.user_id,
        )


class GetChildPayload(BaseModel):
    idheader: int
    idteam: int



class UpdateChildDataPayload(BaseModel):
    day: int
    house: str
    name: str
    gender: str
    age: int
    father: str
    address: str
    nofmc: int
    reasontype: Optional[str] = None
    nodose: str
    reject: str
    location: Optional[str] = None
    hrmp: Optional[str] = None
    returndate: Optional[date] = None
    dateofvacc: Optional[date] = None
    idusers: int


class CombinedPayloadMobile(BaseModel):
    team: CreateTeamPayloadMobile
    header: CreateAICHeaderMobile
    child: List[InsertChildDataPayloadMobile]


class GetUCMOData(BaseModel):
    iduc: List[int]
    campaignname: str
    enteredby: int


class UpdateVaccinationDate(BaseModel):
    updates: list[dict]
    idusers: int

class GetSMCSheetStats(BaseModel):
    idcampaign: int
    iduc: int


class GetAICSheetData(BaseModel):
    idcampaign: int
    idheader: int

class ChildData(BaseModel):
    idchildren: int
    age: int

class UpdatePMCStatus(BaseModel):
    child_data: list[ChildData]
    user_id: int
    campaign_id: int