from asgiref.sync import sync_to_async

async def extract_geo_data(request):
    province_code = division_code = district_code = tehsil_code = 0
    province_name = division_name = district_name = tehsil_name = None
    user_info = await sync_to_async(request.session.get)('user_info')
    usertype = user_info.get("usertype")
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


async def process_user_data(data):
    processed = data.copy()

    # Map userrole code to role name
    role_map = {
        '3': 'province',
        '11': 'division',
        '4': 'district',
        '12': 'tehsil'
    }

    userrole = str(processed.get('userrole'))

    # Special case: user type 1 or 2
    if userrole in ['1', '2']:
        keys_to_remove = ['provincename', 'divisionname', 'districtname', 'tehsilname', 'ucname[]']
        for k in keys_to_remove:
            processed.pop(k, None)
        processed['is_admin'] = 1
        return processed

    # Role-based processing
    role = role_map.get(userrole, 'uc')  # default to uc if not matched
    role = role.lower()

    if role == "province":
        keys_to_remove = ['divisionname', 'districtname', 'tehsilname', 'ucname[]']
        for k in keys_to_remove:
            processed.pop(k, None)
        processed['is_admin'] = 1 if processed.get('is_province_admin') == 'true' else 0

    elif role == "division":
        keys_to_remove = ['districtname', 'tehsilname', 'ucname[]']
        for k in keys_to_remove:
            processed.pop(k, None)
        processed['is_admin'] = 1 if processed.get('is_division_admin') == 'true' else 0

    elif role == "district":
        keys_to_remove = ['tehsilname', 'ucname[]']
        for k in keys_to_remove:
            processed.pop(k, None)
        processed['is_admin'] = 1 if processed.get('is_district_admin') == 'true' else 0

    elif role == "tehsil":
        keys_to_remove = ['ucname[]']
        for k in keys_to_remove:
            processed.pop(k, None)
        processed['is_admin'] = 1 if processed.get('is_tehsil_admin') == 'true' else 0

    elif role == "uc":
        processed['is_admin'] = 0

    return processed




async def preparing_payload(result,user_info):
    if result.get("affiliation")=='Others':
        result["affiliation"] = result.get("otherAffiliation")
    required_order = [
        "is_admin",
        "provincename",
        "firstname",
        "dob",
        "affiliation",
        "address",
        "gender",
        "accountstatus",  # appears twice in your list
        "username",
        "cnic",
        "designation",
        "districtname",
        "userrole",
        "userentry",
        "tehsilname",
        "password",
        "lastname",
        "email",
        "divisionname",
        "contactnumber",
        "ucname[]",
    ]

    # Prepare reordered dictionary with None for missing
    ordered_data = {}
    for field in required_order:
        if field in result:
            try:
                if field == "ucname[]":
                    ordered_data[field] = result.getlist(field)  # keeps all values in list
                else:
                    ordered_data[field] = result[field] if result[field] else None
            except:
                ordered_data[field] = None
        else:
            ordered_data[field] = None
    ordered_data["created_by"] = user_info.get('idusers')
    ordered_data['is_admin'] = 0 if ordered_data['is_admin'] is None else ordered_data['is_admin']
    ordered_data['ucname'] = ordered_data['ucname[]']

    return ordered_data


async def deep_merge_user_session(request, api_data: dict):
    """
    Async-safe: Merge API 'user' fields into session['user_info']
    without losing old data.
    """
    if not api_data or api_data.get("status") != "success":
        return

    new_user_data = api_data.get("user", {})
    if not isinstance(new_user_data, dict):
        return

    # Get current session data (sync_to_async so it's thread-safe in async view)
    current_info = await sync_to_async(request.session.get)("user_info", {})

    # Merge only non-null values
    for key, value in new_user_data.items():
        if value is not None:
            current_info[key] = value

    # Save updated session
    request.session["user_info"] = current_info
    request.session.modified = True

