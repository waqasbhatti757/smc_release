from django.shortcuts import render, redirect
import requests
import json
from asgiref.sync import sync_to_async
from ...helper.get_geo_data import get_user_geo_context
from ...integrate_functions.requestsfunction import process_user_data, preparing_payload,deep_merge_user_session
from dotenv import load_dotenv
import os
from django.http import JsonResponse
import httpx
import time
import asyncio
load_dotenv()
FASTAPI_BASE_URL = os.getenv("FAST_API_URL")



async def add_campaign_data(request):
    context = await get_user_geo_context(request)
    user_info = await sync_to_async(request.session.get)('user_info')
    if user_info.get("is_first_time_login") == 1:
        return await sync_to_async(redirect)('dashboard:user_dashboard')

    return await sync_to_async(render)(request, "add_campaign_data.html", context)


async def delete_data(request):
    context = await get_user_geo_context(request)
    user_info = await sync_to_async(request.session.get)('user_info')
    if user_info.get("is_first_time_login") == 1:
        return await sync_to_async(redirect)('dashboard:user_dashboard')

    return await sync_to_async(render)(request, "delete_data.html", context)

async def edit_campaign_data(request):
    context = await get_user_geo_context(request)
    user_info = await sync_to_async(request.session.get)('user_info')
    if user_info.get("is_first_time_login") == 1:
        return await sync_to_async(redirect)('dashboard:user_dashboard')

    return await sync_to_async(render)(request, "edit_campaign_data.html", context)

async def read_campaign_data(request):
    context = await get_user_geo_context(request)
    user_info = await sync_to_async(request.session.get)('user_info')
    if user_info.get("is_first_time_login") == 1:
        return await sync_to_async(redirect)('dashboard:user_dashboard')

    return await sync_to_async(render)(request, "read_campaign_data.html", context)

async def report_new_pmc(request):
    context = await get_user_geo_context(request)
    user_info = await sync_to_async(request.session.get)('user_info')
    if user_info.get("is_first_time_login") == 1:
        return await sync_to_async(redirect)('dashboard:user_dashboard')

    return await sync_to_async(render)(request, "report_new_pmc.html", context)

async def reports_smc(request):
    context = await get_user_geo_context(request)
    user_info = await sync_to_async(request.session.get)('user_info')
    if user_info.get("is_first_time_login") == 1:
        return await sync_to_async(redirect)('dashboard:user_dashboard')

    return await sync_to_async(render)(request, "reports_smc.html", context)

async def smc_follow_up(request):
    context = await get_user_geo_context(request)
    user_info = await sync_to_async(request.session.get)('user_info')
    if user_info.get("is_first_time_login") == 1:
        return await sync_to_async(redirect)('dashboard:user_dashboard')

    return await sync_to_async(render)(request, "smc_follow_up.html", context)


async def manage_big_team_level_data(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method"})

    body = json.loads(request.body)
    idteam = body.get("idteam")
    deleted_by = body.get("deleted_by")

    if not idteam or not deleted_by:
        return JsonResponse({"status": "error", "message": "Missing parameters"})

    try:
        # Async call to FastAPI endpoint
        async with httpx.AsyncClient() as client:
            url = FASTAPI_BASE_URL + f"/campaign/delete/team-and-children?idteam={idteam}&deleted_by={deleted_by}"
            resp = await client.post(
                url,
                timeout=1000
            )
            # FastAPI returns a dict like {"status": "success", "message": "...", "data": {...}}
            result = resp.json()

        # Only return relevant info to JS
        return JsonResponse({
            "status": result.get("status"),
            "message": result.get("message")
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        })



async def manage_big_child_level_data(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method"})

    body = json.loads(request.body)
    idchildren = body.get("idchildren")
    deleted_by = body.get("deleted_by")

    if not idchildren or not deleted_by:
        return JsonResponse({"status": "error", "message": "Missing parameters"})

    try:
        # Async call to FastAPI endpoint
        async with httpx.AsyncClient() as client:
            url = FASTAPI_BASE_URL + f"/campaign/delete/single/children?idchildren={idchildren}&deleted_by={deleted_by}"
            resp = await client.post(
                url,
                timeout=1000
            )
            # FastAPI returns a dict like {"status": "success", "message": "...", "data": {...}}
            result = resp.json()

        # Only return relevant info to JS
        return JsonResponse({
            "status": result.get("status"),
            "message": result.get("message")
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        })
