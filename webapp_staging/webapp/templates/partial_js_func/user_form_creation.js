<script type="module">
    import { API_BASE_URL } from "/static/apiConfig.js";
    window.API_BASE_URL = API_BASE_URL;
</script>
<script>
    window.validationState = {
    username: false,
    firstname: false,
    lastname: false,
    email: false,
    password: true,
    repeatPassword: true,
    contactnumber: true,
  };
</script>
<script>
    // Declare a global variable
    window.user_info = null;

    async function loadUserInfo() {
        try {
            const res = await fetch("{% url 'usermanagement:get_user_info_for_js' %}");
            if (!res.ok) throw new Error("Failed to fetch user info");

            // Assign to the global variable
            window.user_info = await res.json();
            console.log("Global userinfo loaded:", window.user_info);
        } catch (error) {
            console.error("Error loading user info:", error);
        }
    }

    // Load user info immediately
    loadUserInfo();
</script>
<script>
    document.addEventListener("DOMContentLoaded", function () {
    const roleSelect = document.getElementById("userrole");
    const userType = parseInt("{{ usertype }}");
    const fields = {
    ProvinceMain: ["ProvinceSelected", "provinceToggle"],
    DivisionMain: ["DivisionSelected", "divisionToggle"],
    DistrictMain: ["DistrictSelected", "districtToggle"],
    TehsilMain: ["TehsilSelected", "tehsilToggle"],
    UCMain: []
};

    const roleHierarchy = [1, 2, 3, 11, 4, 12, 5];

    // Define limits based on userType
    const userTypeLimitMap = {
    3: 3,
    11: 11,
    4: 4,
    12: 12,
    5:5
};

    const levelFieldsMap = {
    3: ["ProvinceMain"],
    11: ["ProvinceMain", "DivisionMain"],
    4: ["ProvinceMain", "DivisionMain", "DistrictMain"],
    12: ["ProvinceMain", "DivisionMain", "DistrictMain", "TehsilMain"],
    5: ["ProvinceMain", "DivisionMain", "DistrictMain", "TehsilMain","UCMain"]

};

    function hideAll() {
    for (const [main, children] of Object.entries(fields)) {
    hideAndDisable(main);
    children.forEach(child => hideAndDisable(child));
}
}

    function hideAndDisable(id) {
    const el = document.getElementById(id);
    if (el) {
    el.classList.add("hidden");
    el.setAttribute("disabled", true);
    if (el.tagName === "SELECT" || el.tagName === "INPUT") {
    el.removeAttribute("required");
} else {
    const select = el.querySelector("select");
    if (select) select.removeAttribute("required");
}
}
}

    function showAndEnable(id, includeToggle = true) {
    const el = document.getElementById(id);
    if (el) {
    if (!includeToggle && id.toLowerCase().includes("toggle")) return;
    el.classList.remove("hidden");
    el.removeAttribute("disabled");

    if (el.tagName === "SELECT" || el.tagName === "INPUT") {
    el.setAttribute("required", true);
} else {
    const select = el.querySelector("select");
    if (select) select.setAttribute("required", true);
}
}
}

    function autoClickToggles() {
    const toggleElements = document.querySelectorAll('[data-toggle-scope] input[type="checkbox"].role-toggle');
    toggleElements.forEach(toggleCheckbox => {
    if (toggleCheckbox && toggleCheckbox.checked) {
    toggleCheckbox.click(); // trigger Alpine toggle
}
});
}

    function filterRoleOptions() {
    const options = roleSelect.querySelectorAll("option");
    const limit = userTypeLimitMap[userType];
    if (limit !== undefined) {
    const limitIndex = roleHierarchy.indexOf(limit);
    const toHide = roleHierarchy.slice(0, limitIndex + 1);
    options.forEach(option => {
    if (toHide.includes(parseInt(option.value))) {
    option.classList.add("hidden");
    option.setAttribute("disabled", true);
}
});
}
}

    function showInitialFieldsByUsertype() {
    const fieldsToShow = levelFieldsMap[userType];
    if (fieldsToShow) {
    fieldsToShow.forEach(main => {
    showAndEnable(main, false); // show fields without toggles
    (fields[main] || []).forEach(child => {
    if (!child.toLowerCase().includes("toggle")) {
    showAndEnable(child, false); // exclude toggles
}
});
});
}
}

    function handleRoleChange() {
    const role = parseInt(roleSelect.value);
    hideAll();
    autoClickToggles();

    if (role === 3) {
    showAndEnable("ProvinceMain");
    showAndEnable("ProvinceSelected");
    showAndEnable("provinceToggle");

} else if (role === 11) {
    showAndEnable("ProvinceMain");
    showAndEnable("ProvinceSelected");
    showAndEnable("DivisionMain");
    showAndEnable("DivisionSelected");
    showAndEnable("divisionToggle");

} else if (role === 4) {
    showAndEnable("ProvinceMain");
    showAndEnable("ProvinceSelected");

    showAndEnable("DivisionMain");
    showAndEnable("DivisionSelected");

    showAndEnable("DistrictMain");
    showAndEnable("DistrictSelected");
    showAndEnable("districtToggle");

} else if (role === 12) {
    showAndEnable("ProvinceMain");
    showAndEnable("ProvinceSelected");

    showAndEnable("DivisionMain");
    showAndEnable("DivisionSelected");

    showAndEnable("DistrictMain");
    showAndEnable("DistrictSelected");

    showAndEnable("TehsilMain");
    showAndEnable("TehsilSelected");
    showAndEnable("tehsilToggle");

} else if (role === 5) {
    showAndEnable("ProvinceMain");
    showAndEnable("ProvinceSelected");

    showAndEnable("DivisionMain");
    showAndEnable("DivisionSelected");

    showAndEnable("DistrictMain");
    showAndEnable("DistrictSelected");

    showAndEnable("TehsilMain");
    showAndEnable("TehsilSelected");

    showAndEnable("UCMain");
}
}

    // Initial setup
    hideAll();
    filterRoleOptions();
    showInitialFieldsByUsertype();

    roleSelect.addEventListener("change", handleRoleChange);
});
</script>

<script>
    const rawGeoData = JSON.parse(`{{context_data | safe | escapejs}}`);
</script>

<script>
    document.addEventListener("DOMContentLoaded", function () {
    const userType = String(rawGeoData.usertype);

    function normalize(item) {
    if (!item) return [];
    return Array.isArray(item) ? item : [item];
}

    function populateSelect(id, dataList, label) {
    const select = document.getElementById(id);
    if (!select || !Array.isArray(dataList)) return;

    select.innerHTML = "";

    if (dataList.length === 0) {
    const item = dataList[0];
    const option = document.createElement("option");
    option.value = item.code ?? item.division_id ?? item.district_id ?? item.tehsil_id;
    option.textContent = item.name ?? item.pname ?? item.dname ?? item.division_name ?? item.tname;
    option.selected = true;
    select.appendChild(option);
    select.disabled = true;
} else {
    const defaultOption = document.createElement("option");
    defaultOption.value = "";
    // defaultOption.disabled = true;
    // defaultOption.selected = true;
    defaultOption.textContent = `Select ${label}`;
    select.appendChild(defaultOption);

    dataList.forEach(item => {
    const option = document.createElement("option");
    option.value = item.code ?? item.division_id ?? item.district_id ?? item.tehsil_id;
    option.textContent = item.name ?? item.pname ?? item.dname ?? item.division_name ?? item.tname;
    select.appendChild(option);
});

    select.disabled = false;
}
}

    const provinceData = normalize(rawGeoData.province_info);
    const divisionData = normalize(rawGeoData.division_info);
    const districtData = normalize(rawGeoData.district_info);
    const tehsilData = normalize(rawGeoData.tehsil_info);

    if (userType === "3") {
    populateSelect("provincename", provinceData, "Province");
    const provinceCode = provinceData[0]?.code;
    if (provinceCode) {
    fetch(`/users/province/${provinceCode}/divisions`)
    .then(res => res.json())
    .then(data => populateSelect("divisionname", normalize(data), "Division"));
}
} else if (userType === "11") {
    populateSelect("provincename", provinceData, "Province");
    populateSelect("divisionname", divisionData, "Division");
    const divisionCode = divisionData[0]?.code;
    if (divisionCode) {
    fetch(`/users/division/${divisionCode}/district`)
    .then(res => res.json())
    .then(data => populateSelect("districtname", normalize(data), "District"));
}
} else if (userType === "4") {
    populateSelect("provincename", provinceData, "Province");
    populateSelect("divisionname", divisionData, "Division");
    populateSelect("districtname", districtData, "District");
    const districtCode = districtData[0]?.code;
    if (districtCode) {
    fetch(`/users/district/${districtCode}/tehsil`)
    .then(res => res.json())
    .then(data => populateSelect("tehsilname", normalize(data), "Tehsil"));
}
} else if (userType === "12") {
    populateSelect("provincename", provinceData, "Province");
    populateSelect("divisionname", divisionData, "Division");
    populateSelect("districtname", districtData, "District");
    populateSelect("tehsilname", tehsilData, "Tehsil");
    const tehsilCode = tehsilData[0]?.code;
    if (tehsilCode) {
    fetch(`/users/tehsil/${tehsilCode}/ucs`)
    .then(res => res.json())
    .then(data => populateSelect("ucname", normalize(data), "Union Council"));
}
} else {
    if (["1", "2"].includes(userType)) {
    populateSelect("provincename", provinceData, "Province");
}
}
});
</script>


<script>
    function loadDivisionsByProvince(provinceId) {
    fetch(`${window.API_BASE_URL}/users/province/${provinceId}/divisions`)
        .then(res => res.json())
        .then(result => {
            if (result.status === "Success") {
                const select = document.getElementById("divisionname");
                select.innerHTML = `<option value="" disabled selected>Select Division</option>`;
                result.data.forEach(item => {
                    select.innerHTML += `<option value="${item.division_id}">${item.division_name}</option>`;
                });
                select.disabled = false;

            }
        })
        .catch(err => console.error("Failed to load divisions:", err));
}


    function loadDistrictsByDivision(divisionId) {
    fetch(`${window.API_BASE_URL}/users/division/${divisionId}/district`)
        .then(res => res.json())
        .then(result => {
            if (result.status === "Success") {
                const select = document.getElementById("districtname");
                select.innerHTML = `<option value="" disabled selected>Select District</option>`;
                result.data.forEach(item => {
                    select.innerHTML += `<option value="${item.code}">${item.dname}</option>`;
                });
                select.disabled = false;
            }
        })
        .catch(err => console.error("Failed to load districts:", err));
}

    function loadTehsilsByDistrict(districtId) {
    fetch(`${window.API_BASE_URL}/users/district/${districtId}/tehsil`)
        .then(res => res.json())
        .then(result => {
            if (result.status === "Success") {
                const select = document.getElementById("tehsilname");
                select.innerHTML = `<option value="" disabled selected>Select Tehsil</option>`;
                result.data.forEach(item => {
                    select.innerHTML += `<option value="${item.code}">${item.tname}</option>`;
                });
                select.disabled = false;
            }
        })
        .catch(err => console.error("Failed to load tehsils:", err));
}

</script>

<script>
    const userType = parseInt(rawGeoData.usertype);

    // Flags to track first-time changes
    let provinceChangedOnce = false;
    let divisionChangedOnce = false;
    let districtChangedOnce = false;
    let tehsilChangedOnce = false;

    function clearAndReset(selectId, placeholderText = 'Select') {
    const select = document.getElementById(selectId);
    if (select) {
    const isMultiple = select.multiple;
    select.innerHTML = ''; // Clear all options

    const placeholder = document.createElement('option');
    placeholder.value = '';
    placeholder.disabled = true;
    placeholder.textContent = placeholderText;

    if (!isMultiple) {
    placeholder.selected = true;
}

    select.appendChild(placeholder);
}
}

    // Province change
    document.getElementById("provincename").addEventListener("change", function () {
    if (provinceChangedOnce) {
    clearAndReset("divisionname", "Select Division");
    clearAndReset("districtname", "Select District");
    clearAndReset("tehsilname", "Select Tehsil");
    clearAndReset("ucselection", "Select UC(s)");
} else {
    provinceChangedOnce = true;
}

    if ([1, 2, 3].includes(userType)) {
    loadDivisionsByProvince(this.value);
}
});

    // Division change
    document.getElementById("divisionname").addEventListener("change", function () {
    if (divisionChangedOnce) {
    clearAndReset("districtname", "Select District");
    clearAndReset("tehsilname", "Select Tehsil");
    clearAndReset("ucselection", "Select UC(s)");
} else {
    divisionChangedOnce = true;
}

    if ([1, 2, 3, 11].includes(userType)) {
    loadDistrictsByDivision(this.value);
}
});

    // District change
    document.getElementById("districtname").addEventListener("change", function () {
    if (districtChangedOnce) {
    clearAndReset("tehsilname", "Select Tehsil");
    clearAndReset("ucselection", "Select UC(s)");
} else {
    districtChangedOnce = true;
}

    if ([1, 2, 3, 11, 4].includes(userType)) {
    loadTehsilsByDistrict(this.value);
}
});

    // Tehsil change
    document.getElementById("tehsilname").addEventListener("change", function () {
    if (tehsilChangedOnce) {
    clearAndReset("ucselection", "Select UC(s)");
} else {
    tehsilChangedOnce = true;
}

});
</script>


<script>
    function ucDropdownComponent() {
    return {
    open: false,
    options: [],
    selected: [],
    init() {
    // Optional init logic
},
    toggleSelect(option) {
    const exists = this.selected.find(o => o.code === option.code);
    if (exists) {
    this.selected = this.selected.filter(o => o.code !== option.code);
} else {
    this.selected.push(option);
}
},
    setOptions(newOptions) {
    this.options = newOptions;
    this.selected = []; // reset
}
}
}
</script>


<script>
    function resetUCSelection() {
    const $ucSelect = document.getElementById('ucselection');

    // Destroy previous Choices instance if exists
    if (ucChoices) {
    ucChoices.destroy();
    ucChoices = null;
}

    // Clear original <select>
    $ucSelect.innerHTML = '';

    // Add placeholder option
    const option = document.createElement('option');
    option.value = '';
    option.disabled = true;
    option.textContent = 'Select UC(s)';
    $ucSelect.appendChild(option);
}
</script>
<script>
    let ucChoices;
    document.querySelectorAll('.choices__inner, .choices__list--dropdown, .choices__item').forEach(el => {
    el.style.fontSize = '10px';
});
    function loadUCsByTehsil(tehsilId) {
    fetch(`${window.API_BASE_URL}/users/tehsil/${tehsilId}/ucs`)
        .then(res => res.json())
        .then(result => {
            const $ucSelect = document.getElementById('ucselection');
            $ucSelect.required = true;
            // Destroy old Choices if exists
            if (ucChoices) {
                ucChoices.destroy();
                ucChoices = null;
            }

            $ucSelect.innerHTML = ''; // Clear previous options
            if (result.status === "Success" && result.data.length > 0) {
                result.data.forEach(item => {
                    toggleSubmitButton(1);
                    const option = document.createElement('option');
                    option.value = item.code;
                    option.textContent = item.uctname;
                    $ucSelect.appendChild(option);
                });
            } else {
                // If no UCs returned
                const option = document.createElement('option');
                option.value = '';
                option.disabled = true;
                option.textContent = 'No New Union Councils available';
                $ucSelect.appendChild(option);
            }

            // Reinitialize Choices.js
            ucChoices = new Choices($ucSelect, {
                removeItemButton: true,
                shouldSort: false,
                placeholder: true,
                placeholderValue: 'Select UC(s)',
                noResultsText: 'No UCs found',
                noChoicesText: 'No New Union Councils available',
                itemSelectText: '',
            });

            // Optional: Force minimum height so UI doesn't collapse when empty
            document.querySelector('.choices__list--dropdown').style.maxHeight = '150px';
            document.querySelector('.choices__list--dropdown').style.overflowY = 'auto';
        })
        .catch(err => console.error("Failed to load UCs:", err));
}

    document.getElementById("tehsilname").addEventListener("change", function () {
    // resetUCSelection(); // Always clear before fetch


    if ([1, 2, 3, 11, 4, 12].includes(userType)) {
    loadUCsByTehsil(this.value);
}
});
</script>



<script>
function toggleSubmitButton() {
    const btn = document.getElementById('submitbuttonenableornot');
    // Check if all fields in validationState are valid
    const allValid = Object.values(window.validationState).every(v => v === true);

    if (allValid) {
        // Enable button
        btn.disabled = false;
        btn.style.removeProperty('background-color');
        btn.style.removeProperty('background-image');
        btn.style.removeProperty('border-color');
        btn.style.removeProperty('cursor');
    } else {
        // Disable button
        btn.disabled = true;
        btn.style.setProperty('background-color', 'gray', 'important');
        btn.style.setProperty('background-image', 'none', 'important');
        btn.style.setProperty('border-color', 'gray', 'important');
        btn.style.setProperty('cursor', 'not-allowed', 'important');
    }
}
</script>
<script>
    document.addEventListener("DOMContentLoaded", function () {
    const usernameInput = document.getElementById("username");
    toggleSubmitButton();
    toastr.options = {
    "closeButton": true,
    "progressBar": true,
    "timeOut": "3000",
    "extendedTimeOut": "1000",
    "positionClass": "toast-top-right"
};

    usernameInput.addEventListener("blur", async function () {
    const value = usernameInput.value.trim();

    const isLowercase = value === value.toLowerCase();
    const hasWhitespace = /\s/.test(value);
    const specialChars = /[^a-z0-9_.]/g;
    const hasTripleRepeat = /(.)\1\1/.test(value);
    const onlyDigits = /^\d+$/.test(value);
    const hasLetters = /[a-z]/.test(value);
    const isTooShort = value.length < 5;
    const isTooLong = value.length > 20;
    const startsWithLetter = /^[a-z]/.test(value);
    const isAscii = /^[\x00-\x7F]+$/.test(value);
    const hasInvalidSpecials = /[^a-z0-9_.]/.test(value);
    const hasConsecutiveSpecials = /[_.]{2,}/.test(value);
    const endsWithSpecial = /[_.]$/.test(value);
    const hasMixedCase = /[A-Z]/.test(value);

    let error = "";

    if (!value) {
    error = "Username is required.";
} else if (!isAscii) {
    error = "Username must contain only English (ASCII) characters.";
    window.validationState.username = false;
    toggleSubmitButton();

} else if (hasMixedCase) {
    error = "Username must be all lowercase.";
    window.validationState.username = false;
    toggleSubmitButton();
} else if (hasWhitespace) {
    error = "Username must not contain spaces.";
    window.validationState.username = false;
    toggleSubmitButton();
} else if (hasInvalidSpecials) {
    error = "Only '_' and '.' are allowed as special characters.";
    window.validationState.username = false;
    toggleSubmitButton();
} else if (hasConsecutiveSpecials) {
    error = "Do not use consecutive special characters like '__' or '..'.";
    window.validationState.username = false;
    toggleSubmitButton();
} else if (endsWithSpecial) {
    error = "Username cannot end with '_' or '.'";
    window.validationState.username = false;
    toggleSubmitButton();
} else if (hasTripleRepeat) {
    error = "Username cannot have the same character three times in a row.";
    window.validationState.username = false;
    toggleSubmitButton();
} else if (!startsWithLetter) {
    error = "Username must start with a letter.";
    window.validationState.username = false;
    toggleSubmitButton();
} else if (isTooShort) {
    error = "Username must be at least 5 characters.";
    window.validationState.username = false;
    toggleSubmitButton();
} else if (isTooLong) {
    error = "Username cannot be more than 20 characters.";
    window.validationState.username = false;
    toggleSubmitButton();
} else if (onlyDigits) {
    error = "Username cannot be only numbers.";
    window.validationState.username = false;
    toggleSubmitButton();
} else if (!hasLetters) {
    error = "Username must contain at least one letter.";
    window.validationState.username = false;
    toggleSubmitButton();
}

    if (error) {
    toastr.error(error, "Username Issues");
    window.validationState.username = false;
    toggleSubmitButton();
    markInputInvalid();
    return;
}

    try {
    // First API: Geo name verification
    const geoResponse = await fetch(`${window.API_BASE_URL}/users/find_anomaly_name`, {
    method: "POST",
    headers: {
    "Content-Type": "application/json"
},
    body: JSON.stringify({text: value})
});

    const geoResult = await geoResponse.json();

    if (geoResult.verified === true) {
    toastr.error("Username contains a possible geo code or location.", "Naming Restriction");
    window.validationState.username = false;
    toggleSubmitButton();
    markInputInvalid();
    return;
}

    // Second API: Username/email existence check
    const userResponse = await fetch(`${window.API_BASE_URL}/users/check-username-or-email`, {
    method: "POST",
    headers: {
    "Content-Type": "application/json"
},
    body: JSON.stringify({value})
});

    const userResult = await userResponse.json();
    console.log(window.user_info.username);
    const currentUrl = window.location.href;
    if (userResult.already_exists === true) {
        if (currentUrl.includes("create_user")) {
            // Condition when creating a user
            if (value === window.user_info.username) {
                toastr.error("Username already exists. Please choose another.", "Already Taken");
                window.validationState.username = false;
                toggleSubmitButton();
                markInputInvalid();
                return;
            }
        } else {
            // Condition when updating/editing a user
            if (value !== user_info.username) {
                toastr.error("Username already exists. Please choose another.", "Already Taken");
                window.validationState.username = false;
                toggleSubmitButton();
                markInputInvalid();
                return;
            }
        }
    }

    toastr.success("Username is available and valid!", "Success");
    window.validationState.username = true;
    toggleSubmitButton();


} catch (err) {
    console.error("Validation error:", err);
    toastr.error("An error occurred during validation. Try again later.");
}

    function markInputInvalid() {
    usernameInput.classList.remove("border-gray-300");
    usernameInput.classList.add("border-red-500", "focus:ring-red-300");

    setTimeout(() => {
    usernameInput.classList.remove("border-red-500", "focus:ring-red-300");
    usernameInput.classList.add("border-gray-300");
}, 3000);
}
});
});
</script>

<script>
    document.addEventListener("DOMContentLoaded", function () {
    const emailInput = document.getElementById("email");
    toggleSubmitButton();
    toastr.options = {
    "closeButton": true,
    "progressBar": true,
    "timeOut": "3000",
    "extendedTimeOut": "1000",
    "positionClass": "toast-top-right"
};

    const blacklistDomains = [
    "mailinator.com", "tempmail.com", "10minutemail.com", "example.com"
    ];

    emailInput.addEventListener("blur", async function () {
    const value = emailInput.value.trim();
    const [local, domain] = value.split("@") || [];

    const isValidFormat = /^[a-zA-Z0-9._]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(value);
    const hasOnlyAllowedSpecials = /^[a-zA-Z0-9._]+$/.test(local || "");
    const hasDoubleSpecials = /[._]{2,}/.test(local || "");
    const startsInvalid = /^[^a-zA-Z]/.test(local || "");
    const onlyDigitsBeforeAt = /^\d+$/.test(local || "");
    const isAscii = /^[\x00-\x7F]+$/.test(value);
    const domainTooShort = domain && domain.split(".")[0].length < 2;
    const domainBlacklisted = domain && blacklistDomains.includes(domain.toLowerCase());
    const localTooShort = (local || "").length < 4;
    const localTooLong = (local || "").length > 20;
    const hasTripleRepeat = /(.)\1\1/.test(local || "");

    let error = "";

    if (!value) {
    error = "Email is required.";
    window.validationState.email = false;
    toggleSubmitButton();

} else if (!isAscii) {
    error = "Only English (ASCII) characters are allowed.";
    window.validationState.email = false;
    toggleSubmitButton();

} else if (!isValidFormat) {
    error = "Email format is invalid.";
    window.validationState.email = false;
    toggleSubmitButton();

} else if (!hasOnlyAllowedSpecials) {
    error = "Only '_', '.' and alphanumeric characters are allowed before '@'.";
    window.validationState.email = false;
    toggleSubmitButton();

} else if (hasDoubleSpecials) {
    error = "Do not use '__' or '..' in the username.";
    window.validationState.email = false;
    toggleSubmitButton();

} else if (startsInvalid) {
    error = "Email must start with a letter.";
    window.validationState.email = false;
    toggleSubmitButton();

} else if (onlyDigitsBeforeAt) {
    error = "Email cannot have only numbers before '@'.";
    window.validationState.email = false;
    toggleSubmitButton();

} else if (localTooShort) {
    error = "Email username must be at least 4 characters.";
    window.validationState.email = false;
    toggleSubmitButton();

} else if (localTooLong) {
    error = "Email username must be at most 20 characters.";
    window.validationState.email = false;
    toggleSubmitButton();
} else if (hasTripleRepeat) {
    error = "Email username cannot contain 3 repeated characters (e.g., aaa, 111).";
    window.validationState.email = false;
    toggleSubmitButton();
} else if (domainTooShort) {
    error = "Domain must be at least 2 characters before '.com'";
    window.validationState.email = false;
    toggleSubmitButton();
} else if (domainBlacklisted) {
    error = "Email domain is not allowed.";
    window.validationState.email = false;
    toggleSubmitButton();
}

    if (error) {
    toastr.error(error, "Email Issues");
    window.validationState.email = false;
    toggleSubmitButton();
    markInputInvalid();
    return;
}

    try {
    // Check geo/political codes in local part
    const geoResponse = await fetch(`${window.API_BASE_URL}/users/find_anomaly_name`, {
    method: "POST",
    headers: {
    "Content-Type": "application/json"
},
    body: JSON.stringify({text: local})
});

    const geoResult = await geoResponse.json();

    if (geoResult.verified === true) {
    toastr.error("Email username contains a possible geo/location code.", "Naming Restriction");
    window.validationState.email = false;
    toggleSubmitButton();
    markInputInvalid();
    return;
}

    // Check if email already exists
    const existsResponse = await fetch(`${window.API_BASE_URL}/users/check-username-or-email`, {
    method: "POST",
    headers: {
    "Content-Type": "application/json"
},
    body: JSON.stringify({value})
});

    const existsResult = await existsResponse.json();
    const currentUrl = window.location.href;
    if (existsResult.already_exists === true) {
        if (currentUrl.includes("create_user")) {
            console.log("awefasdfsadfsdaf");
            // Condition when creating a user
            if (value === window.user_info.email) {
                toastr.error("This email is already registered.", "Already In Use");
                markInputInvalid();
                window.validationState.email = false;
                toggleSubmitButton();
                return;
            }
            else {
                toastr.error("This email is already registered.", "Already In Use");
                markInputInvalid();
                window.validationState.email = false;
                toggleSubmitButton();
                return;
            }


        } else {
            // Condition when updating/editing a user
            if (value !== user_info.email) {
                toastr.error("This email is already registered.", "Already In Use");
                window.validationState.email = false;
                toggleSubmitButton();
                markInputInvalid();
                return;
            }
        }
    }

    toastr.success("Email is valid and available!", "Success");
    window.validationState.email = true;
    toggleSubmitButton();


} catch (err) {
    console.error("Email validation failed:", err);
    toastr.error("Something went wrong. Please try again later.");
}

    function markInputInvalid() {
    emailInput.classList.remove("border-gray-300");
    emailInput.classList.add("border-red-500", "focus:ring-red-300");

    setTimeout(() => {
    emailInput.classList.remove("border-red-500", "focus:ring-red-300");
    emailInput.classList.add("border-gray-300");
}, 3000);
}
});
});
</script>

<script>
    document.addEventListener("DOMContentLoaded", function () {
    const inputs = [document.getElementById("firstname"), document.getElementById("lastname")];
    toggleSubmitButton();
    toastr.options = {
    "closeButton": true,
    "progressBar": true,
    "timeOut": "3000",
    "extendedTimeOut": "1000",
    "positionClass": "toast-top-right"
};

    const blacklist = ["admin", "test", "user", "root", "system"];

    inputs.forEach((input) => {
    input.addEventListener("blur", function () {
    const value = input.value.trim();

    const hasLetters = /[a-zA-Z]/.test(value);
    const hasDigits = /\d/.test(value);
    const isMixedAlphanumeric = hasLetters && hasDigits;
    const hasSpecialChars = /[^a-zA-Z0-9]/.test(value);
    const isOnlyDigits = /^\d+$/.test(value);
    const isTooShort = value.length < 3;
    const hasTripleRepeat = /(.)\1\1/i.test(value);
    const hasWhitespace = /\s/.test(value);
    const startsWithLetter = /^[a-zA-Z]/.test(value);
    const isEmailFormat = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    const isBlacklisted = blacklist.includes(value.toLowerCase());
    const isAsciiOnly = /^[\x00-\x7F]*$/.test(value);

    let error = "";

    if (!isAsciiOnly) {
    error = "Only English (ASCII) characters are allowed.";
    window.validationState.firstname=false;
    window.validationState.lastname=false;
    toggleSubmitButton();
} else if (isBlacklisted) {
    error = "This name is not allowed.";
    window.validationState.firstname=false;
    window.validationState.lastname=false;
    toggleSubmitButton();
} else if (isEmailFormat) {
    error = "Name cannot be an email address.";
    window.validationState.firstname=false;
    window.validationState.lastname=false;
    toggleSubmitButton();
} else if (!startsWithLetter) {
    error = "Name must start with a letter.";
    window.validationState.firstname=false;
    window.validationState.lastname=false;
    toggleSubmitButton();
} else if (isTooShort) {
    error = "Name must be at least 3 characters long.";
    window.validationState.firstname=false;
    window.validationState.lastname=false;
    toggleSubmitButton();
} else if (hasTripleRepeat) {
    error = "Name must not contain the same character three times in a row.";
    window.validationState.firstname=false;
    window.validationState.lastname=false;
    toggleSubmitButton();
} else if (isOnlyDigits) {
    error = "Name cannot be only digits.";
    window.validationState.firstname=false;
    window.validationState.lastname=false;
    toggleSubmitButton();
} else if (hasSpecialChars) {
    error = "Special characters are not allowed.";
    window.validationState.firstname=false;
    window.validationState.lastname=false;
    toggleSubmitButton();
} else if (isMixedAlphanumeric) {
    error = "Name must not be a mix of letters and numbers (e.g., Afeef123).";
    window.validationState.firstname=false;
    window.validationState.lastname=false;
    toggleSubmitButton();
}

    if (error) {
    toastr.error(error, "First and Last Name Issues");
    window.validationState.firstname = false;
    window.validationState.lastname = false;
    toggleSubmitButton();
    input.classList.remove("border-gray-300");
    input.classList.add("border-red-500", "focus:ring-red-300");

    setTimeout(() => {
    input.classList.remove("border-red-500", "focus:ring-red-300");
    input.classList.add("border-gray-300");
}, 3000);
}else {
                // Set validation state to true when input is valid
    window.validationState.firstname = true;
    window.validationState.lastname = true;
    toggleSubmitButton();
}
});
});
});
</script>
<script>
    document.addEventListener("DOMContentLoaded", function () {
    const passwordInput = document.getElementById("password");
    const repeatInput = document.getElementById("repeatpassword");
    toggleSubmitButton();
    toastr.options = {
    "closeButton": true,
    "progressBar": true,
    "timeOut": "3000",
    "extendedTimeOut": "1000",
    "positionClass": "toast-top-right"
};

    function validatePassword(pwd) {
    const errors = [];

    if (!pwd) {
    errors.push("Password is required.");
    window.validationState.password = false;
    window.validationState.repeatPassword = false;
    toggleSubmitButton();
}
    if (pwd.length < 8 || pwd.length > 32) {
    errors.push("Password must be between 8 and 32 characters.");
    window.validationState.password = false;
    window.validationState.repeatPassword = false;
    toggleSubmitButton();
}
    if (!/[A-Z]/.test(pwd)) {
    errors.push("At least 1 uppercase letter required.");
    window.validationState.password = false;
    window.validationState.repeatPassword = false;
    toggleSubmitButton();
}
    if ((pwd.match(/[a-z]/g) || []).length < 2) {
    errors.push("At least 2 lowercase letters required.");
    window.validationState.password = false;
    window.validationState.repeatPassword = false;
    toggleSubmitButton();
}
    if (!/[0-9]/.test(pwd)) {
    errors.push("At least 1 digit required.");
    window.validationState.password = false;
    window.validationState.repeatPassword = false;
    toggleSubmitButton();
}
    if (!/[!@#$%^&*(),.?":{}|<>_\-+=]/.test(pwd)) {
    errors.push("At least 1 special character required.");
    window.validationState.password = false;
    window.validationState.repeatPassword = false;
    toggleSubmitButton();
}
    if (/(.)\1\1/.test(pwd)) {
    errors.push("No 3 repeated characters allowed.");
    window.validationState.password = false;
    window.validationState.repeatPassword = false;
    toggleSubmitButton();
}
    if (/\s/.test(pwd)) {
    errors.push("No spaces allowed.");
    window.validationState.password = false;
    window.validationState.repeatPassword = false;
    toggleSubmitButton();
}
    if (!/^[\x20-\x7E]+$/.test(pwd)) {
    errors.push("Only printable ASCII characters allowed.");
    window.validationState.password = false;
    window.validationState.repeatPassword = false;
    toggleSubmitButton();
}

    return errors;
}

    function showError(inputElement, message) {
    toastr.error(message, "Password Error");
    toggleSubmitButton(1);
    inputElement.classList.remove("border-gray-300");
    inputElement.classList.add("border-red-500", "focus:ring-red-300");

    setTimeout(() => {
    inputElement.classList.remove("border-red-500", "focus:ring-red-300");
    inputElement.classList.add("border-gray-300");
}, 3000);
}

    passwordInput.addEventListener("blur", () => {
    const errors = validatePassword(passwordInput.value);

    if (errors.length > 0) {
        showError(passwordInput, errors[0]); // Show first error only
    }
    else {
            window.validationState.password = true;
            window.validationState.repeatPassword = true; // enable submit
            toggleSubmitButton();
        }
});

    repeatInput.addEventListener("blur", () => {
    if (repeatInput.value !== passwordInput.value) {
        showError(repeatInput, "Both Passwords do not match.");
        window.validationState.password = false;
        window.validationState.repeatPassword = false;
        toggleSubmitButton();
    }
    else {
            window.validationState.password = true;
            window.validationState.repeatPassword = true; // enable submit
            toggleSubmitButton();

        }
});
});
</script>

<script>
    document.addEventListener("DOMContentLoaded", function () {
    const cnicInput = document.getElementById("cnic");

    cnicInput.addEventListener("input", function (e) {
    let value = cnicInput.value.replace(/\D/g, ''); // Remove non-digits

    if (value.length > 13) value = value.slice(0, 13);

    // Auto-insert hyphens
    let formatted = value;
    if (value.length > 5 && value.length <= 12) {
    formatted = value.slice(0, 5) + '-' + value.slice(5);
}
    if (value.length > 12) {
    formatted = value.slice(0, 5) + '-' + value.slice(5, 12) + '-' + value.slice(12);
}

    cnicInput.value = formatted;
});
});


    function validateCNIC(cnic) {
    const formatted = cnic.replace(/-/g, ""); // Remove hyphens

    if (!/^\d{13}$/.test(formatted)) {
    return "CNIC must be exactly 13 digits.";
}

    if (formatted.startsWith("0")) {
    return "CNIC cannot start with 0.";
}

    const middle = formatted.slice(5, 12);
    if (/^0{7}$/.test(middle)) {
    return "Middle 7 digits cannot all be zero.";
}

    const hyphenatedFormat = /^\d{5}-\d{7}-\d{1}$/;
    if (cnic.includes("-") && !hyphenatedFormat.test(cnic)) {
    return "CNIC format should be 12345-1234567-1.";
}

    return ""; // Valid
}


    const cnicInput = document.getElementById("cnic");

    cnicInput.addEventListener("blur", () => {
    const error = validateCNIC(cnicInput.value.trim());

    if (error) {
    toastr.error(error, "CNIC Error");

    cnicInput.classList.remove("border-gray-300");
    cnicInput.classList.add("border-red-500", "focus:ring-red-300");

    setTimeout(() => {
    cnicInput.classList.remove("border-red-500", "focus:ring-red-300");
    cnicInput.classList.add("border-gray-300");
}, 3000);
}
});
</script>

<script>

    document.addEventListener("DOMContentLoaded", function () {
    const contactInput = document.getElementById("contactnumber");
    toastr.options = {
    "closeButton": true,
    "progressBar": true,
    "timeOut": "3000",
    "extendedTimeOut": "1000",
    "positionClass": "toast-top-right"
};

    toggleSubmitButton();
    contactInput.addEventListener("input", function () {
    let value = contactInput.value.replace(/\D/g, ''); // Only digits
    if (value.length > 11) value = value.slice(0, 11); // Limit to 11 digits

    // Auto-insert hyphen after 4 digits
    let formatted = value;
    if (value.length > 4) {
    formatted = value.slice(0, 4) + '-' + value.slice(4);
}

    contactInput.value = formatted;
});

    contactInput.addEventListener("blur", function () {
    const error = validatePakPhone(contactInput.value.trim());

    if (error) {
    toastr.error(error, "Contact Number Issue");
    window.validationState.contactnumber = false;
    toggleSubmitButton();
    contactInput.classList.remove("border-gray-300");
    contactInput.classList.add("border-red-500", "focus:ring-red-300");

    setTimeout(() => {
    contactInput.classList.remove("border-red-500", "focus:ring-red-300");
    contactInput.classList.add("border-gray-300");
}, 3000);
}
});

    function validatePakPhone(phone) {
    const clean = phone.replace(/\D/g, '');

    if (clean.length !== 11 && clean.length > 0) {
        window.validationState.contactnumber = false;
        toggleSubmitButton();
        return "Phone number must be exactly 11 digits.";
    }
        else {
            window.validationState.contactnumber = true;
            toggleSubmitButton();
            return "";
    }

    const validPrefixes = [
    "0300","0301","0302","0303","0304","0305","0306","0307","0308","0309",
    "0310","0311","0312","0313","0314","0315","0316","0317","0318","0319",
    "0320","0321","0322","0323","0324","0325","0326","0327","0328","0329",
    "0330","0331","0332","0333","0334","0335","0336","0337","0338","0339",
    "0340","0341","0342","0343","0344","0345","0346","0347","0348","0349",
    "0355"
    ];

    const prefix = clean.slice(0, 4);
    const last7 = clean.slice(4);

    if (!validPrefixes.includes(prefix)) {
        window.validationState.contactnumber = false;
        toggleSubmitButton();
    return `Invalid prefix (${prefix}). Must be a valid mobile network code.`;
}

    if (/^0{7}$/.test(last7)) {
        window.validationState.contactnumber = false;
        toggleSubmitButton();
    return "Phone number cannot have all zeroes after prefix.";
}

    if (/^(\d)\1{6}$/.test(last7)) {
        window.validationState.contactnumber = false;
        toggleSubmitButton();
    return "Phone number cannot have the same digit repeated 7 times.";
}

    if (isSequential(last7)) {
        window.validationState.contactnumber = false;
        toggleSubmitButton();
    return "Phone number cannot have sequential digits like 1234567.";
}
    window.validationState.contactnumber = true;
    toggleSubmitButton();
    return ""; // Valid


}

    function isSequential(num) {
    const inc = "0123456789";
    const dec = "9876543210";
    return inc.includes(num) || dec.includes(num);
}
});
</script>


<script src="https://cdn.jsdelivr.net/npm/litepicker/dist/litepicker.js"></script>
<script>
    document.addEventListener("DOMContentLoaded", function () {
    const picker = new Litepicker({
    element: document.getElementById("dob"),
    format: "DD-MM-YYYY",
    autoApply: true,
    allowRepick: true,
    dropdowns: {
    minYear: 2024,
    maxYear: 2050,
    months: true,
    years: true,
},
    setup: (picker) => {
    picker.on("show", () => {
    setTimeout(() => {
    const panel = document.querySelector(".litepicker");
    if (panel) {
    panel.style.borderRadius = "12px";
    panel.style.padding = "10px";
    panel.style.fontSize = "13px";
    panel.style.transition = "all 0.3s ease-in-out";
}
}, 10);
});
}
});
});
</script>


<script>
    function handleAffiliationChange() {
    const affiliation = document.getElementById("affiliation").value;
    const otherInput = document.getElementById("otherAffiliation");
    const otherWrapper = document.getElementById("otherWrapper");
    const affiliationWrapper = document.getElementById("affiliationWrapper");

    if (affiliation === "Others") {
    // Enable 'Other' input
    otherInput.disabled = false;
    otherInput.setAttribute("required", "required");
    // Show the other input and reduce original dropdown
    otherWrapper.classList.remove("hidden");
    affiliationWrapper.classList.remove("md:col-span-3");
    affiliationWrapper.classList.add("md:col-span-1");
} else {
    // Disable and clear
    otherInput.disabled = true;
    otherInput.removeAttribute("required");
    otherInput.value = "";
    // Hide the other input and restore original dropdown width
    otherWrapper.classList.add("hidden");
    affiliationWrapper.classList.remove("md:col-span-1");
    affiliationWrapper.classList.add("md:col-span-3");
}
}
</script>



