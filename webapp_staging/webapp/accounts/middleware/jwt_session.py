import time
from django.shortcuts import redirect
from asgiref.sync import sync_to_async


class JWTSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    async def __call__(self, request):
        # public_paths = ['/login/', '/logout/', '/admin/', '/static/']
        #
        # if any(request.path.startswith(path) for path in public_paths):
        #     response = await self._get_response_async(request)
        #     return response

        jwt_token = await sync_to_async(request.session.get)('jwt_token')
        token_expiry = await sync_to_async(request.session.get)('expires_in')

        if not jwt_token or not token_expiry:
            return redirect('login')

        if int(time.time()) >= token_expiry:
            await sync_to_async(request.session.flush)()
            return redirect('login')

        response = await self._get_response_async(request)
        return response

    async def _get_response_async(self, request):
        response = self.get_response
        if callable(response):
            response = await sync_to_async(response)(request)
        return response
