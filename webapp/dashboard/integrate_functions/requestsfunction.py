from asgiref.sync import sync_to_async

async def extract_geo_data(request):
    province_code = division_code = district_code = tehsil_code = 0
    province_name = division_name = district_name = tehsil_name = None
    user_info = await sync_to_async(request.session.get)('user_info')
    usertype = user_info.get("usertype") if user_info else None
    jwt_token = await sync_to_async(request.session.get)('jwt_token')  # Ensure this is set in session
    if usertype == 3:
        province_code = user_info.get("idoffice")
        province_name = {'code': user_info.get("idoffice"), 'pname': user_info.get("province_name")}
    elif usertype == 11:
        province_code = user_info.get("idoffice")
        province_name = {'code': user_info.get("idoffice"), 'pname': user_info.get("province_name")}
        division_code = user_info.get("division_code")
        division_name = {'code': user_info.get("division_code"), 'dname': user_info.get("division_name")}
    elif usertype == 4:
        province_code = user_info.get("idoffice")
        province_name = {'code': user_info.get("idoffice"), 'pname': user_info.get("province_name")}
        division_code = user_info.get("division_code")
        division_name = {'code': user_info.get("division_code"), 'dname': user_info.get("division_name")}
        district_code = user_info.get("district_code")
        district_name = {'code': user_info.get("district_code"), 'dname': user_info.get("district_name")}
    elif usertype == 12:
        province_code = user_info.get("idoffice")
        province_name = {'code': user_info.get("idoffice"), 'pname': user_info.get("province_name")}
        division_code = user_info.get("division_code")
        division_name = {'code': user_info.get("division_code"), 'dname': user_info.get("division_name")}
        district_code = user_info.get("district_code")
        district_name = {'code': user_info.get("district_code"), 'dname': user_info.get("district_name")}
        tehsil_code = user_info.get("tehsil_code")
        tehsil_name = {'code': user_info.get("tehsil_code"), 'dname': user_info.get("tehsil_name")}

    elif usertype in [1, 2]:
        pass  # All codes remain None

    payload = {
        "usertype": usertype,  # or request.session.get("user_id") if needed
        "device_type": 1,  # Change if needed 1 for web 2 for mobile
        "jwt_token": jwt_token,
        "province_code": province_code,
        "division_code": division_code,
        "district_code": district_code,
        "tehsil_code": tehsil_code,
    }
    return usertype,payload,province_name,division_name,district_name,tehsil_name


async def parsing_geo_api_data(api_data,province_name, division_name, district_name, tehsil_name):
    if "Provinces" in api_data:
        province_name = api_data["Provinces"]
    if "Divisions" in api_data:
        division_name = api_data["Divisions"]
    if "Districts" in api_data:
        district_name = api_data["Districts"]
    if "Tehsils" in api_data:
        tehsil_name = api_data["Tehsils"]

    context = {
        "province_info": province_name,
        "division_info": division_name,
        "district_info": district_name,
        "tehsil_info": tehsil_name,
    }
    return context



