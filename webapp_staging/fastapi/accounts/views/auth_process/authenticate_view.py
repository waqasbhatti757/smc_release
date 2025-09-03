from django.shortcuts import render, redirect
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


async def login_view(request):
    if FASTAPI_BASE_URL:
        print(f".env loaded successfully. FAST_API_URL = {FASTAPI_BASE_URL}")
    else:
        print("Failed to load .env or FAST_API_URL not set.")

    jwt_token = await sync_to_async(request.session.get)('jwt_token')
    expires_in = await sync_to_async(request.session.get)('expires_in')

    if jwt_token and expires_in and int(time.time()) < int(expires_in):
        return await sync_to_async(redirect)('dashboard:user_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        async with httpx.AsyncClient() as client:
            response = await client.post(FASTAPI_BASE_URL+"/auth/login", json={
                'username': username,
                'password': password
            })

        # print(response.json())

        if response.status_code == 200 and response.json()['data'].get("access_token"):
            # You might set a session or token here
            data = response.json()['data']
            jwt_token = data['access_token']
            payload = jwt.decode(jwt_token, options={"verify_signature": False})

            # Save JWT and user info in session
            request.session['jwt_token'] = jwt_token
            request.session['user_info'] = data['users']

            # Save token expiry time (UNIX timestamp)
            request.session['expires_in'] = data['expires_in']
            User = get_user_model()
            username = data['users']['username']

            user, _ = await sync_to_async(User.objects.get_or_create)(
                username=username,
                defaults={
                    "email": data['users'].get("email") or "",
                    "first_name": data['users'].get("first_name") or "",
                    "last_name": data['users'].get("last_name") or ""  # ✅ fallback to empty string
                }
            )

            await sync_to_async(login)(request, user)

            return await sync_to_async(redirect)('dashboard:user_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'auth/login.html')




async def logout(request):
    await sync_to_async(request.session.flush)()
    return await sync_to_async(redirect)('accounts:login')




# def login_view(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         print(username, password)
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             return redirect('dashboard')  # Change 'dashboard' if needed
#         else:
#             messages.error(request, 'Invalid username or password.')
#
#     return render(request, 'auth/login.html')
