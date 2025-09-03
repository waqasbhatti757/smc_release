import time
from starlette.datastructures import URL
from asgiref.sync import sync_to_async
from django.core.handlers.asgi import ASGIRequest
from django.contrib.sessions.middleware import SessionMiddleware

EXCLUDED_PATHS = [
    "/accounts/login/",
    "/accounts/logout/",
    "/admin/",
    "/static/",
    "/favicon.ico",
]

class JWTSessionASGIMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = URL(scope["path"]).path

        # 🛑 Skip middleware for public paths
        if any(path.startswith(p) for p in EXCLUDED_PATHS):
            await self.app(scope, receive, send)
            return

        # Build Django request
        request = ASGIRequest(scope, receive)

        # Apply session middleware in async-safe way
        await sync_to_async(SessionMiddleware(lambda req: None).process_request)(request)

        jwt_token = await sync_to_async(request.session.get)("jwt_token")
        expires_in = await sync_to_async(request.session.get)("expires_in")

        print("JWT CHECK:", jwt_token, expires_in)

        # Redirect to login if invalid or expired
        if not jwt_token or not expires_in or int(time.time()) >= int(expires_in):
            await sync_to_async(request.session.flush)()
            await send({
                "type": "http.response.start",
                "status": 302,
                "headers": [
                    [b"location", b"/accounts/login/"],
                    [b"cache-control", b"no-store"],
                    [b"content-length", b"0"],
                ],
            })
            await send({"type": "http.response.body", "body": b""})
            return

        # Add request back to scope if needed later
        scope["django.request"] = request

        await self.app(scope, receive, send)
