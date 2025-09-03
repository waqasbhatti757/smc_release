<script type="module">
    import { API_BASE_URL } from "/static/apiConfig.js";
    window.API_BASE_URL = API_BASE_URL;
</script>

<script>
    const user_infos = JSON.parse(`{{profile_user_info | safe | escapejs}}`);
    const user_type_a = JSON.parse(`{{user_type | safe | escapejs}}`);
    console.log("afesdsdfsdsdsdsdsdsdef");
    console.log(user_type_a);
    console.log(user_infos);
</script>

<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>

<script>
    document.getElementById('email').value = user_infos.email || '';
    document.getElementById('firstname').value = user_infos.first_name || '';
    document.getElementById('lastname').value = user_infos.last_name || '';
    document.getElementById('username').value = user_infos.username || '';

    const genderSelect = document.getElementById('gender');
        if (genderSelect && user_infos && user_infos.genderval) {
        genderSelect.value = user_infos.genderval;

        // Optional: trigger change event if needed for any listeners or styling
        const event = new Event('change');
        genderSelect.dispatchEvent(event);
    }
    document.getElementById('cnic').value = user_infos.cnic;
    document.getElementById('dob').value = user_infos.cnicexpiry;
    document.getElementById('contactnumber').value = user_infos.mobile;
    function setAffiliation(affiliationValue) {
    const knownAffiliations = ["GOVERNMENT", "BMGF", "WHO"];
    const affiliationSelect = document.getElementById('affiliation');
    const otherWrapper = document.getElementById('otherWrapper');
    const affiliationWrapper = document.getElementById('affiliationWrapper');
    const otherInput = document.getElementById('otherAffiliation');

    // Set dropdown value
    if (knownAffiliations.includes(affiliationValue.toUpperCase())) {
            affiliationSelect.value = affiliationValue.toUpperCase();

            otherWrapper.classList.add('hidden');
            otherInput.disabled = true;
            otherInput.value = '';

            affiliationWrapper.classList.remove('md:col-span-1');
            affiliationWrapper.classList.add('md:col-span-3');
            otherWrapper.classList.remove('md:col-span-2');
        } else {
            affiliationSelect.value = "Others";

            otherWrapper.classList.remove('hidden');
            otherInput.disabled = false;
            otherInput.value = affiliationValue;

            affiliationWrapper.classList.remove('md:col-span-3');
            affiliationWrapper.classList.add('md:col-span-1');
            otherWrapper.classList.add('md:col-span-2');
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        const affiliationSelect = document.getElementById('affiliation');
        const initialAffiliation = user_infos.affiliation;

        // Set initial
        setAffiliation(initialAffiliation);

        // Handle dropdown change
        affiliationSelect.addEventListener('change', function () {
            if (this.value === "Others") {
                setAffiliation(""); // empty so input is visible
            } else {
                setAffiliation(this.value);
            }
        });
    });
</script>

<script src="https://cdn.jsdelivr.net/npm/litepicker/dist/litepicker.js"></script>



<script>
    document.addEventListener("DOMContentLoaded", function () {
    const user_type_a = JSON.parse(`{{user_type | safe | escapejs}}`);
    const roleSelect = document.getElementById("userrole");
    const userType = user_type_a;
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
function populateSelectone(selectId, data, placeholder, selectedValue = null) {
    const select = document.getElementById(selectId);
    if (!select) return;

    // Create placeholder
    const placeholderOption = document.createElement("option");

    // Populate options
    data.forEach(item => {
        const opt = document.createElement("option");
        opt.value = item.id;
        opt.textContent = item.name;
        if (String(item.id) === String(selectedValue)) {
            opt.selected = true;
        }
    });

    // Ensure select.value reflects the selected option
    if (selectedValue !== null && selectedValue !== "") {
        select.value = String(selectedValue);
    }

    // Trigger change event
    select.dispatchEvent(new Event("change", { bubbles: true }));
}
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
    if (userType === "1") {
        populateSelect("provincename", provinceData, "Province");
        console.log("asdfsdfsdfsdfsdefasdfgergerererger");
        console.log(userType);
        console.log("asdfsdfsdfsdfsdefasdfgergerererger");
        // Set all 4 fields based on user_infos
        const provinceCode = provinceData[0]?.code;
        populateSelectone("provincename", provinceData, "Province", String(user_infos.idoffice));
        // populateSelectone("divisionname", divisionData, "Division", String(user_infos.division_code));
        // populateSelectone("districtname", districtData, "District", String(user_infos.dcode));
        // populateSelectone("tehsilname", tehsilData, "Tehsil", String(user_infos.tehsil_code));
    }
    else if (userType === "3") {
    populateSelect("provincename", provinceData, "Province");
    const provinceCode = provinceData[0]?.code;
    populateSelectone("provincename", provinceData, "Province", String(user_infos.idoffice));
    if (provinceCode) {
    fetch(`/users/province/${provinceCode}/divisions`)
    .then(res => res.json())
    .then(data => populateSelect("divisionname", normalize(data), "Division"));
}
} else if (userType === "11") {
    populateSelect("provincename", provinceData, "Province");
    populateSelect("divisionname", divisionData, "Division");
    const divisionCode = divisionData[0]?.code;
    populateSelectone("provincename", provinceData, "Province", String(user_infos.idoffice));
    populateSelectone("divisionname", divisionData, "Division", String(user_infos.division_code));
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
    populateSelectone("provincename", provinceData, "Province", String(user_infos.idoffice));
    populateSelectone("divisionname", divisionData, "Division", String(user_infos.division_code));
    populateSelectone("districtname", districtData, "District", String(user_infos.dcode));

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
    populateSelectone("provincename", provinceData, "Province", String(user_infos.idoffice));
    populateSelectone("divisionname", divisionData, "Division", String(user_infos.division_code));
    populateSelectone("districtname", districtData, "District", String(user_infos.dcode));
    populateSelectone("tehsilname", tehsilData, "Tehsil", String(user_infos.tehsil_code));
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
document.addEventListener("DOMContentLoaded", function () {
    const roleSelect = document.getElementById("userrole");
    const user_infos = JSON.parse(`{{profile_user_info | safe | escapejs}}`);
    console.log(user_infos.usertype);
    if (roleSelect && user_infos.usertype != null) {
        roleSelect.value = String(user_infos.usertype);

        // Optional: trigger change event
        roleSelect.dispatchEvent(new Event("change"));
    }
});
</script>
<script>
function loadDivisionsByProvince(provinceId) {
    const user_infos = JSON.parse(`{{profile_user_info | safe | escapejs}}`);

    fetch(`${window.API_BASE_URL}/users/province/${provinceId}/divisions`)
        .then(res => res.json())
        .then(result => {
            if (result.status === "Success") {
                const select = document.getElementById("divisionname");
                select.innerHTML = `<option disabled selected>Select Division</option>`;

                result.data.forEach(item => {
                    select.innerHTML += `<option value="${item.division_id}">${item.division_name}</option>`;
                });

                // Set selected value from user_infos.division_code
                if (user_infos.division_code) {
                    select.value = String(user_infos.division_code);
                }

                select.disabled = false;
                select.dispatchEvent(new Event("change", { bubbles: true }));
            }
        })
        .catch(err => console.error("Failed to load divisions:", err));
}

function loadDistrictsByDivision(divisionId) {
    const user_infos = JSON.parse(`{{profile_user_info | safe | escapejs}}`);

    fetch(`${window.API_BASE_URL}/users/division/${divisionId}/district`)
        .then(res => res.json())
        .then(result => {
            if (result.status === "Success") {
                const select = document.getElementById("districtname");
                select.innerHTML = `<option disabled selected>Select District</option>`;

                result.data.forEach(item => {
                    select.innerHTML += `<option value="${item.code}">${item.dname}</option>`;
                });

                // Set selected value from user_infos.dcode
                if (user_infos.district_code) {
                    select.value = String(user_infos.district_code);
                }

                select.disabled = false;
                select.dispatchEvent(new Event("change", { bubbles: true }));
            }
        })
        .catch(err => console.error("Failed to load districts:", err));
}

function loadTehsilsByDistrict(districtId) {
    const user_infos = JSON.parse(`{{profile_user_info | safe | escapejs}}`);

    fetch(`${window.API_BASE_URL}/users/district/${districtId}/tehsil`)
        .then(res => res.json())
        .then(result => {
            if (result.status === "Success") {
                const select = document.getElementById("tehsilname");
                select.innerHTML = `<option disabled selected>Select Tehsil</option>`;

                result.data.forEach(item => {
                    select.innerHTML += `<option value="${item.code}">${item.tname}</option>`;
                });

                // Set selected value from user_infos.tehsil_code
                if (user_infos.tehsil_code) {
                    select.value = String(user_infos.tehsil_code);
                }

                select.disabled = false;
                select.dispatchEvent(new Event("change", { bubbles: true }));
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

            // Destroy old Choices if exists
            if (ucChoices) {
                ucChoices.destroy();
                ucChoices = null;
            }

            $ucSelect.innerHTML = ''; // Clear previous options

            const user_infos = JSON.parse(`{{profile_user_info | safe | escapejs}}`);
            let userUcCodes = [];
            if (user_infos.uc_codes) {
                userUcCodes = user_infos.uc_codes.split(',').map(code => code.trim());
            }

            if (result.status === "Success" && result.data.length > 0) {
                result.data.forEach(item => {
                    const option = document.createElement('option');
                    option.value = item.code;
                    option.textContent = item.uctname;
                    // Do NOT set selected here for Choices.js
                    $ucSelect.appendChild(option);
                });
            } else {
                const option = document.createElement('option');
                option.value = '';
                option.disabled = true;
                option.textContent = 'No New Union Councils available';
                $ucSelect.appendChild(option);
            }

            // Initialize Choices with pre-selected values
            ucChoices = new Choices($ucSelect, {
                removeItemButton: true,
                shouldSort: false,
                placeholder: true,
                placeholderValue: 'Select UC(s)',
                noResultsText: 'No UCs found',
                noChoicesText: 'No New Union Councils available',
                itemSelectText: '',
            });

            // Set pre-selected UCs AFTER Choices is initialized
            userUcCodes.forEach(code => {
                ucChoices.setChoiceByValue(code);
            });

            // Ensure dropdown scroll
            const dropdown = document.querySelector('.choices__list--dropdown');
            if (dropdown) {
                dropdown.style.maxHeight = '150px';
                dropdown.style.overflowY = 'auto';
            }
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
document.addEventListener("DOMContentLoaded", function () {
    const user_infos = JSON.parse(`{{ profile_user_info | safe | escapejs }}`);
    const userType = user_infos.usertype;

    const adminFlags = {
        province: user_infos.is_province_admin,
        division: user_infos.is_divisional_admin,
        district: user_infos.is_district_admin,
        tehsil: user_infos.is_tehsil_admin
    };

    console.log("User type:", userType);
    console.log("Admin flags:", adminFlags);

    function disableToggle(toggleId) {
        const toggleContainer = document.getElementById(toggleId);
        if (!toggleContainer) return;

        toggleContainer.style.pointerEvents = "none";
        toggleContainer.style.opacity = "0.5";

        const checkbox = toggleContainer.querySelector('input[type="checkbox"].role-toggle');
        if (checkbox) {
            checkbox.disabled = true;
        }
    }

    function enableAndTurnOnToggle(toggleId) {
        const toggleContainer = document.getElementById(toggleId);
        if (!toggleContainer) return;

        toggleContainer.classList.remove("hidden");
        toggleContainer.style.display = "block";

        const checkbox = toggleContainer.querySelector('input[type="checkbox"].role-toggle');
        if (checkbox) {
            checkbox.checked = true; // turn ON
            checkbox.dispatchEvent(new Event("change", { bubbles: true })); // notify Alpine
        }
    }

    function enableTogglesByAdminFlags() {
        if (adminFlags.province === 1 && userType === 3) {
            enableAndTurnOnToggle("provinceToggle");
        }
        if (adminFlags.division === 1 && userType === 11) {
            enableAndTurnOnToggle("divisionToggle");
        }
        if (adminFlags.district === 1 && userType === 4) {
            enableAndTurnOnToggle("districtToggle");
        }
        if (adminFlags.tehsil === 1 && userType === 12) {
            enableAndTurnOnToggle("tehsilToggle");
        }
    }

    // Run after a slight delay to ensure Alpine-rendered elements exist
    setTimeout(enableTogglesByAdminFlags, 200);
});
</script>

<script>
document.addEventListener('DOMContentLoaded', () => {
    const user_infos = JSON.parse(`{{ profile_user_info | safe | escapejs }}`);

    // 1. Set current address
    const addressField = document.getElementById('address');
    if (addressField) {
        addressField.value = user_infos.current_address || '';
    }

    // 2. Set entry permission select
    const entrySelect = document.getElementById('userentry');
    if (entrySelect && user_infos.entrypermission) {
        entrySelect.value = user_infos.entrypermission;
        // Optional: trigger change for Alpine.js reactivity
        entrySelect.dispatchEvent(new Event('change', { bubbles: true }));
    }

    // 3. Set status select
    const statusSelect = document.getElementById('accountstatus');
    const statusText = user_infos.status === 1 ? "Active" : "InActive";
    if (statusSelect) {
        statusSelect.value = statusText;
        statusSelect.dispatchEvent(new Event('change', { bubbles: true }));
    }
});
</script>
<script>
    window.validationStates = {
    username: false,
    email: false,
    firstname: false,
    lastname: false,

  };
</script>
<script>
function toggleSubmitButton() {
    const btn = document.querySelector('button[type="submit"]');
    console.log("afeef");
    // Check if all fields in validationState are valid
    const allValid = Object.values(window.validationStates).every(v => v === true);

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
        window.validationStates.username = false;
    toggleSubmitButton();

} else if (!isAscii) {
    error = "Username must contain only English (ASCII) characters.";
    window.validationStates.username = false;
    toggleSubmitButton();

} else if (hasMixedCase) {
    error = "Username must be all lowercase.";
    window.validationStates.username = false;
    toggleSubmitButton();

} else if (hasWhitespace) {
    error = "Username must not contain spaces.";
    window.validationStates.username = false;
    toggleSubmitButton();

} else if (hasInvalidSpecials) {
    error = "Only '_' and '.' are allowed as special characters.";
    window.validationStates.username = false;
    toggleSubmitButton();

} else if (hasConsecutiveSpecials) {
    error = "Do not use consecutive special characters like '__' or '..'.";
    window.validationStates.username = false;
    toggleSubmitButton();
} else if (endsWithSpecial) {
    error = "Username cannot end with '_' or '.'";
    window.validationStates.username = false;
    toggleSubmitButton();

} else if (hasTripleRepeat) {
    error = "Username cannot have the same character three times in a row.";
    window.validationStates.username = false;
    toggleSubmitButton();

} else if (!startsWithLetter) {
    error = "Username must start with a letter.";
    window.validationStates.username = false;
    toggleSubmitButton();

} else if (isTooShort) {
    error = "Username must be at least 5 characters.";
    window.validationStates.username = false;
    toggleSubmitButton();

} else if (isTooLong) {
    error = "Username cannot be more than 20 characters.";
    window.validationStates.username = false;
    toggleSubmitButton();

} else if (onlyDigits) {
    error = "Username cannot be only numbers.";
    window.validationStates.username = false;
    toggleSubmitButton();

} else if (!hasLetters) {
    error = "Username must contain at least one letter.";
    window.validationStates.username = false;
    toggleSubmitButton();

}

    if (error) {
    toastr.error(error, "Username Issues");
    window.validationStates.username = false;
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
    window.validationStates.username = false;
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
    if (userResult.already_exists === true && value != user_infos.username) {
    toastr.error("Username already exists. Please choose another.", "Already Taken");
    window.validationStates.username = false;
    toggleSubmitButton();

    markInputInvalid();
    return;
}

    toastr.success("Username is available and valid!", "Success");
    window.validationStates.username = true;
    toggleSubmitButton();


} catch (err) {
    console.error("Validation error:", err);
    window.validationStates.username = false;
    toggleSubmitButton();

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
    window.validationStates.email = false;
    toggleSubmitButton();

} else if (!isAscii) {
    error = "Only English (ASCII) characters are allowed.";
    window.validationStates.email = false;
    toggleSubmitButton();

} else if (!isValidFormat) {
    error = "Email format is invalid.";
    window.validationStates.email = false;
    toggleSubmitButton();

} else if (!hasOnlyAllowedSpecials) {
    error = "Only '_', '.' and alphanumeric characters are allowed before '@'.";
    window.validationStates.email = false;
    toggleSubmitButton();

} else if (hasDoubleSpecials) {
    error = "Do not use '__' or '..' in the username.";
    window.validationStates.email = false;
    toggleSubmitButton();

} else if (startsInvalid) {
    error = "Email must start with a letter.";
    window.validationStates.email = false;
    toggleSubmitButton();

} else if (onlyDigitsBeforeAt) {
    error = "Email cannot have only numbers before '@'.";
    window.validationStates.email = false;
    toggleSubmitButton();

} else if (localTooShort) {
    error = "Email username must be at least 4 characters.";
    window.validationStates.email = false;
    toggleSubmitButton();

} else if (localTooLong) {
    error = "Email username must be at most 20 characters.";
    window.validationStates.email = false;
    toggleSubmitButton();
} else if (hasTripleRepeat) {
    error = "Email username cannot contain 3 repeated characters (e.g., aaa, 111).";
    window.validationStates.email = false;
    toggleSubmitButton();
} else if (domainTooShort) {
    error = "Domain must be at least 2 characters before '.com'";
    window.validationStates.email = false;
    toggleSubmitButton();
} else if (domainBlacklisted) {
    error = "Email domain is not allowed.";
    window.validationStates.email = false;
    toggleSubmitButton();
}

    if (error) {
    toastr.error(error, "Email Issues");
    window.validationStates.email = false;
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
    window.validationStates.email = false;
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
                window.validationStates.email = false;
                toggleSubmitButton();
                return;
            }
            else {
                toastr.error("This email is already registered.", "Already In Use");
                markInputInvalid();
                window.validationStates.email = false;
                toggleSubmitButton();
                return;
            }


        } else {
            // Condition when updating/editing a user
            if (value !== user_info.email) {
                toastr.error("This email is already registered.", "Already In Use");
                window.validationStates.email = false;
                toggleSubmitButton();
                markInputInvalid();
                return;
            }
        }
    }

    toastr.success("Email is valid and available!", "Success");
    window.validationStates.email = true;
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
    window.validationStates.firstname=false;
    window.validationStates.lastname=false;
    toggleSubmitButton();
} else if (isBlacklisted) {
    error = "This name is not allowed.";
    window.validationStates.firstname=false;
    window.validationStates.lastname=false;
    toggleSubmitButton();
} else if (isEmailFormat) {
    error = "Name cannot be an email address.";
    window.validationStates.firstname=false;
    window.validationStates.lastname=false;
    toggleSubmitButton();
} else if (!startsWithLetter) {
    error = "Name must start with a letter.";
    window.validationStates.firstname=false;
    window.validationStates.lastname=false;
    toggleSubmitButton();
} else if (isTooShort) {
    error = "Name must be at least 3 characters long.";
    window.validationStates.firstname=false;
    window.validationStates.lastname=false;
    toggleSubmitButton();
} else if (hasTripleRepeat) {
    error = "Name must not contain the same character three times in a row.";
    window.validationStates.firstname=false;
    window.validationStates.lastname=false;
    toggleSubmitButton();
} else if (isOnlyDigits) {
    error = "Name cannot be only digits.";
    window.validationStates.firstname=false;
    window.validationStates.lastname=false;
    toggleSubmitButton();
} else if (hasSpecialChars) {
    error = "Special characters are not allowed.";
    window.validationStates.firstname=false;
    window.validationStates.lastname=false;
    toggleSubmitButton();
} else if (isMixedAlphanumeric) {
    error = "Name must not be a mix of letters and numbers (e.g., Afeef123).";
    window.validationStates.firstname=false;
    window.validationStates.lastname=false;
    toggleSubmitButton();
}

    if (error) {
    toastr.error(error, "First and Last Name Issues");
    window.validationStates.firstname = false;
    window.validationStates.lastname = false;
    toggleSubmitButton();
    input.classList.remove("border-gray-300");
    input.classList.add("border-red-500", "focus:ring-red-300");

    setTimeout(() => {
    input.classList.remove("border-red-500", "focus:ring-red-300");
    input.classList.add("border-gray-300");
}, 3000);
}else {
                // Set validation state to true when input is valid
    window.validationStates.firstname = true;
    window.validationStates.lastname = true;
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
    window.validationStates.password = false;
    window.validationStates.repeatPassword = false;
    toggleSubmitButton();
}
    if (pwd.length < 8 || pwd.length > 32) {
    errors.push("Password must be between 8 and 32 characters.");
    window.validationStates.password = false;
    window.validationStates.repeatPassword = false;
    toggleSubmitButton();
}
    if (!/[A-Z]/.test(pwd)) {
    errors.push("At least 1 uppercase letter required.");
    window.validationStates.password = false;
    window.validationStates.repeatPassword = false;
    toggleSubmitButton();
}
    if ((pwd.match(/[a-z]/g) || []).length < 2) {
    errors.push("At least 2 lowercase letters required.");
    window.validationStates.password = false;
    window.validationStates.repeatPassword = false;
    toggleSubmitButton();
}
    if (!/[0-9]/.test(pwd)) {
    errors.push("At least 1 digit required.");
    window.validationStates.password = false;
    window.validationStates.repeatPassword = false;
    toggleSubmitButton();
}
    if (!/[!@#$%^&*(),.?":{}|<>_\-+=]/.test(pwd)) {
    errors.push("At least 1 special character required.");
    window.validationStates.password = false;
    window.validationStates.repeatPassword = false;
    toggleSubmitButton();
}
    if (/(.)\1\1/.test(pwd)) {
    errors.push("No 3 repeated characters allowed.");
    window.validationStates.password = false;
    window.validationStates.repeatPassword = false;
    toggleSubmitButton();
}
    if (/\s/.test(pwd)) {
    errors.push("No spaces allowed.");
    window.validationStates.password = false;
    window.validationStates.repeatPassword = false;
    toggleSubmitButton();
}
    if (!/^[\x20-\x7E]+$/.test(pwd)) {
    errors.push("Only printable ASCII characters allowed.");
    window.validationStates.password = false;
    window.validationStates.repeatPassword = false;
    toggleSubmitButton();
}

    return errors;
}

    function showError(inputElement, message) {
    toastr.error(message, "Password Error");
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
            window.validationStates.password = true;
            window.validationStates.repeatPassword = true; // enable submit
            toggleSubmitButton();
        }
});

    repeatInput.addEventListener("blur", () => {
    if (repeatInput.value !== passwordInput.value) {
        showError(repeatInput, "Both Passwords do not match.");
        window.validationStates.password = false;
        window.validationStates.repeatPassword = false;
        toggleSubmitButton();
    }
    else {
            window.validationStates.password = true;
            window.validationStates.repeatPassword = true; // enable submit
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
    window.validationStates.contactnumber = false;
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
    window.validationStates.contactnumber = false;
    toggleSubmitButton();
    return "Phone number must be exactly 11 digits.";
}
    else {
        window.validationStates.contactnumber = true;
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
        window.validationStates.contactnumber = false;
        toggleSubmitButton();
    return `Invalid prefix (${prefix}). Must be a valid mobile network code.`;
}

    if (/^0{7}$/.test(last7)) {
        window.validationStates.contactnumber = false;
        toggleSubmitButton();
    return "Phone number cannot have all zeroes after prefix.";
}

    if (/^(\d)\1{6}$/.test(last7)) {
        window.validationStates.contactnumber = false;
        toggleSubmitButton();
    return "Phone number cannot have the same digit repeated 7 times.";
}

    if (isSequential(last7)) {
        window.validationStates.contactnumber = false;
        toggleSubmitButton();
    return "Phone number cannot have sequential digits like 1234567.";
}
    window.validationStates.contactnumber = true;
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