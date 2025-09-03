def session_user_info(request):
    print(request.session.get("user_info"))
    return {
        "user_info": request.session.get("user_info")
    }



