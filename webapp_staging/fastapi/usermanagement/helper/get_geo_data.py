import httpx
import json
from ..integrate_functions.requestsfunction import extract_geo_data,parsing_geo_api_data
from dotenv import load_dotenv
from asgiref.sync import sync_to_async

import os
load_dotenv()
FASTAPI_BASE_URL = os.getenv("FAST_API_URL")

async def get_user_geo_context(request):
    usertype, payload, province_name, division_name, district_name, tehsil_name = await extract_geo_data(request)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{FASTAPI_BASE_URL}/users/user/locations", json=payload)
            response.raise_for_status()
            api_data = response.json().get("data", {})
        except httpx.HTTPError as e:
            print("FastAPI call failed:", str(e))
            api_data = {}

    context = await parsing_geo_api_data(api_data, province_name, division_name, district_name, tehsil_name)
    print(context)
    context['usertype'] = usertype
    # context['userinfo'] = await sync_to_async(request.session.get)('user_info')
    context['context_data'] = json.dumps(context)
    return context
