from django.shortcuts import render
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
    return await sync_to_async(render)(request, "add_campaign_data.html", context)


async def delete_data(request):
    context = await get_user_geo_context(request)
    return await sync_to_async(render)(request, "delete_data.html", context)

async def edit_campaign_data(request):
    context = await get_user_geo_context(request)
    return await sync_to_async(render)(request, "edit_campaign_data.html", context)

async def read_campaign_data(request):
    context = await get_user_geo_context(request)
    return await sync_to_async(render)(request, "read_campaign_data.html", context)

async def report_new_pmc(request):
    context = await get_user_geo_context(request)
    return await sync_to_async(render)(request, "report_new_pmc.html", context)

async def reports_smc(request):
    context = await get_user_geo_context(request)
    return await sync_to_async(render)(request, "reports_smc.html", context)

async def smc_follow_up(request):
    context = await get_user_geo_context(request)
    return await sync_to_async(render)(request, "smc_follow_up.html", context)


