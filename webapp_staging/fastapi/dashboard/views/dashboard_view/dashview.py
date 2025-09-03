from django.shortcuts import render, redirect
from asgiref.sync import sync_to_async
from ...helper.get_geo_data import get_user_geo_context
# from ...integrate_functions.requestsfunction import deep_merge_user_session
import json
import httpx
import os
from dotenv import load_dotenv
from django.http import JsonResponse
import httpx
load_dotenv()
FASTAPI_BASE_URL = os.getenv("FAST_API_URL")



async def dashboard_view(request):
    # Safely fetch user_info from session
    user_info = await sync_to_async(request.session.get)('user_info')
    context = await get_user_geo_context(request)
    if not user_info:
        # redirect() must be wrapped since it returns HttpResponse
        return await sync_to_async(redirect)('accounts:login')
    # render() must be wrapped too, and awaited to return HttpResponse
    return await sync_to_async(render)(request, "dashboard_template/dashboard.html", {"user": user_info, "flag": user_info.get("is_first_time_login"), **context})