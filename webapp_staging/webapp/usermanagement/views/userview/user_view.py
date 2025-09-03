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

async def create_user(request):
    user_info = await sync_to_async(request.session.get)('user_info')
    if user_info.get("is_first_time_login") == 1:
        return await sync_to_async(redirect)('dashboard:user_dashboard')

    if request.method == "POST":
        result = await process_user_data(request.POST)
        user_info = await sync_to_async(request.session.get)('user_info')
        ordered_data = await preparing_payload(result, user_info)
        url = FASTAPI_BASE_URL + "/users/createusers"

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=ordered_data)

        res_json = response.json()
        print(res_json)
        if res_json.get('message'):
            return JsonResponse({'message': res_json['message']})
        else:
            return JsonResponse({'detail': res_json.get('detail', 'Unknown error')}, status=400)

    else:
        context = await get_user_geo_context(request)
        return await sync_to_async(render)(request, "user_template/create_new_user.html", context)


async def update_user_profile(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    result = await process_user_data(request.POST)
    user_info = await sync_to_async(request.session.get)("user_info")
    ordered_data = await preparing_payload(result, user_info)

    update_url = FASTAPI_BASE_URL + "/users/updateuser"
    reset_url = FASTAPI_BASE_URL + "/users/resetsessionuserinfo"

    # Use one httpx.AsyncClient for both calls
    async with httpx.AsyncClient() as client:
        update_response = await client.post(update_url, json=ordered_data)

        if update_response.status_code != 200:
            return JsonResponse(
                {"error": "Failed to update user", "detail": update_response.text},
                status=update_response.status_code
            )

        session_data = dict(request.session)
        payload = {"jwt_token": session_data.get("jwt_token"), "user_id": session_data.get("user_info", {}).get("idusers")}
        try:
            reset_response = await client.post(reset_url, json=payload)
            reset_response.raise_for_status()
            api_data = reset_response.json()
        except httpx.HTTPStatusError as e:
            return JsonResponse({"error": "Reset API failed"}, status=e.response.status_code)
        except httpx.RequestError as e:
            return JsonResponse({"error": "Request to Reset API failed"}, status=500)

    await deep_merge_user_session(request, api_data)
    return JsonResponse(update_response.json())


async def manage_user(request):
    user_info = await sync_to_async(request.session.get)('user_info')
    if user_info.get("is_first_time_login") == 1:
        return await sync_to_async(redirect)('dashboard:user_dashboard')

    context = await get_user_geo_context(request)
    # headers = {'accept': 'application/json','Content-Type': 'application/json',}
    # json_data = {'limit': 400,'offset': 0,}
    # async with httpx.AsyncClient() as client:
    #     response = await client.post(f"{FASTAPI_BASE_URL}/users/getuserbasicinfo", headers=headers, json=json_data)
    #     response.raise_for_status()
    #     data = response.json()
    #     users = data.get('users', [])
    #     users = users.get('users', [])
    #
    # context['users'] = users
    # print(users[0])
    return await sync_to_async(render)(request, "user_template/manage_user_data.html",context)



async def get_users_api(request):
    limit = int(request.GET.get('limit', 40))
    offset = int(request.GET.get('offset', 0))
    user_info = await sync_to_async(request.session.get)('user_info')
    payload = {key: value[0] if isinstance(value, list) else value for key, value in request.GET.lists()}
    print(payload)
    for key, user_key in [('provincename', 'idoffice'),
                          ('divisionname', 'division_code'),
                          ('districtname', 'district_code'),
                          ('tehsilname', 'tehsil_code')]:
        if key not in payload:
            payload[key] = user_info[user_key]

    payload['user_id'] = user_info['usertype']
    payload.update({'limit': limit, 'offset': offset, 'user_id': user_info['usertype']})

    print(payload)
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{FASTAPI_BASE_URL}/users/getuserbasicinfo",
                                     headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
    users_data = data.get('users', {})
    total = users_data.get('total', 0)
    users = users_data.get('users', [])

    completed = (offset + limit) >= total

    return JsonResponse({
        "users": users,
        "completed": completed
    })


async def users_ajax(request):
    try:
        draw = int(request.GET.get("draw", 1))
        start = int(request.GET.get("start", 0))
        length = int(request.GET.get("length", 20))
        search_value = request.GET.get("search[value]", "")

        headers = {'accept': 'application/json','Content-Type': 'application/json'}
        json_data = {'limit': length, 'offset': start, 'search': search_value}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{FASTAPI_BASE_URL}/users/getuserbasicinfo",
                headers=headers, json=json_data
            )
            response.raise_for_status()
            data = response.json()

        total_count = data.get("total", 0)
        users = data.get("users", {}).get("users", [])

        return JsonResponse({
            "draw": draw,
            "recordsTotal": total_count,
            "recordsFiltered": total_count,
            "data": users
        })

    except Exception as e:
        import traceback
        print("Error in users_ajax:", e)
        traceback.print_exc()
        return JsonResponse({
            "draw": 0,
            "recordsTotal": 0,
            "recordsFiltered": 0,
            "data": [],
            "error": str(e)
        }, status=500)

# This need to be more update later on.
async def update_settings(request):
    context = await get_user_geo_context(request)
    return await sync_to_async(render)(request, "user_template/update_user_profile.html",context)

async def get_user_info_for_js(request):
    # Fetch 'user_info' from session asynchronously
    user_info = await sync_to_async(request.session.get)('user_info', {})

    # Return it as JSON for JS
    return JsonResponse(user_info)


async def edit_user_profile(request):
    context = await get_user_geo_context(request)

    if request.method == "POST":
        user_id = request.POST.get("user_id")  # ✅ read POST payload
    else:
        user_id = request.GET.get("id")

    print("afeef here is my userid", user_id)
    jwt_token = "string"  # real token here
    url = FASTAPI_BASE_URL + "/users/profile_detail"
    if user_id:
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(
                    url,
                    json={
                        "jwt_token": jwt_token,
                        "user_id": user_id
                    },
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    users = data.get("users", {}).get("result", [])
                    if users:
                        user_info= users[0]
                    else:
                        user_info = None
                else:
                    user_info = None
            except httpx.RequestError as exc:
                print(f"Request failed: {exc}")
                user_info = None
    else:
        user_info = None

    print(user_info)
    return await sync_to_async(render)(
        request, "user_template/edit_profile_user.html", {"user_type": context["usertype"],"context_data": context["context_data"], "profile_user_info": json.dumps(user_info)}
    )



async def full_profile_update(request):
    """
    Django async view to update a user profile via FastAPI.
    Only handles POST requests and returns JSON for frontend alerts.
    """
    result = await process_user_data(request.POST)
    user_info = await sync_to_async(request.session.get)('user_info')
    ordered_data = await preparing_payload(result, user_info)
    ordered_data['idusers']=result['idusers']
    print(ordered_data)
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "Method not allowed"}, status=405)


    url = f"{FASTAPI_BASE_URL}/users/reupdate_user_info"  # Assume update endpoint

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(
                url,
                json=ordered_data,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
            )
            if response.status_code == 200:
                data = response.json()
                return JsonResponse({"success": True, "msg": "User updated successfully!", "data": data})
            else:
                return JsonResponse({"success": False, "msg": f"FastAPI error: {response.text}"}, status=response.status_code)
        except httpx.RequestError as exc:
            return JsonResponse({"success": False, "msg": f"Request failed: {exc}"}, status=500)



async def change_my_profile(request):
    """
    Django async view that receives the request from JS,
    forwards it to FastAPI endpoint, and returns status & message.
    """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method"})

    body = json.loads(request.body)
    user_id = body.get("idusers")

    if not user_id:
        return JsonResponse({"status": "error", "message": "User ID missing"})

    try:
        # Async call to FastAPI endpoint
        async with httpx.AsyncClient() as client:
            url = FASTAPI_BASE_URL + f"/campaign/toggle/user/status?idusers={user_id}"
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
