from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
from django.contrib.auth import authenticate, login,get_user_model
from django.contrib import messages
import httpx
import jwt
import time
from asgiref.sync import sync_to_async
from dotenv import load_dotenv
import os
load_dotenv()
FASTAPI_BASE_URL = os.getenv("FAST_API_URL")


async def sync_planning(request):
    jwt_token = await sync_to_async(lambda: request.session.get("jwt_token"))()
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{FASTAPI_BASE_URL}/campaign/campaigns/summary")
        data = resp.json() if resp.status_code == 200 else {}
    # pass API response into the template
    return await sync_to_async(render)(
        request,
        "campaign_templates/campaign_planning.html",
        {"summary": data,"jwt_token": jwt_token}
    )
async def campaign_planning(request):
    if request.method == "POST":
        try:
            payload = json.loads(request.body.decode("utf-8"))
            all_ids = set(payload['districts']).union(set(payload['districtsExcel']))
            print(all_ids)
            plans = []
            for iduc in all_ids:
                plans.append({
                    "iduc": iduc,
                    "uc_status": 1 if iduc in payload['districts'] else 0,
                    "uc_status_zd": 0,
                    "import_child_data": 1 if iduc in payload['districtsExcel'] else 0
                })

            print("this is the plan",plans)
            json_payload = {'campaignid': payload['campaign'],'updated_by':10, 'plans': plans}

            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{FASTAPI_BASE_URL}/campaign/campaign/planning/updates",
                    json=json_payload,
                    headers={"accept": "application/json", "Content-Type": "application/json"},
                    timeout=10.0
                )
            data = resp.json() if resp.status_code == 200 else {"error": resp.text}
            return JsonResponse(data, status=resp.status_code, safe=False)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)


    async with httpx.AsyncClient() as client:
        response = await client.get(f'{FASTAPI_BASE_URL}/campaign/campaigns/list')
        if response.status_code == 200:
            campaigns = response.json()['campaigns']
        else:
            campaigns = []

    return await sync_to_async(render)(
        request,
        'campaign_templates/planning.html',
        {'campaigns': campaigns}
    )