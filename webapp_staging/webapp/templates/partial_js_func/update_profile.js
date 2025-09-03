<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
<script>
    document.addEventListener("DOMContentLoaded", function () {
    // Assuming these values are passed from backend
    const currentAddress = "{{ user_info.current_address|escapejs }}";
    const designation = "{{ user_info.designation|escapejs }}";
    const userRole = "{{ user_info.usertype|escapejs }}";  // role id like '1', '2', etc.
    const entryPermission = "{{ user_info.entrypermission|escapejs }}";
    const status = "{{ user_info.status|escapejs }}"; // assuming 1 or 0
    const entrySelect = document.getElementById("userentry");
    const userInfo = {
    province_name: "{{ user_info.province_name|escapejs }}",
    division_name: "{{ user_info.division_name|escapejs }}",
    district_name: "{{ user_info.district_name|escapejs }}",
    tehsil_name: "{{ user_info.tehsil_name|escapejs }}"
    // Add more if needed
};

    function setSelectValueAndDisable(selectId, value) {
    if (value) {
    const select = document.getElementById(selectId);
    if (select) {
    select.innerHTML = `<option value="${value}" selected>${value}</option>`;
    select.disabled = true;
}
}
}

    setSelectValueAndDisable("provincename", userInfo.province_name);
    setSelectValueAndDisable("divisionname", userInfo.division_name);
    setSelectValueAndDisable("districtname", userInfo.district_name);
    setSelectValueAndDisable("tehsilname", userInfo.tehsil_name);

    const users = {
    usertype: "{{ user_info.usertype|escapejs }}"  // Assuming this is passed too
};
    if (users.usertype == "5") {  // usertype is string from Django template context

    const users = {
        user_ucs: "{{ user_info.user_ucs|escapejs }}",
        uc_codes: {{user_info.uc_codes|safe}} // assuming this is passed as a JSON array
    };

    const userUCsString = users.user_ucs.replace(/\u0027/g, '"');
    const userUCs = JSON.parse(userUCsString);
    const ucCodes = users.uc_codes;

    const ucSelect = document.getElementById("ucselection");
    ucSelect.innerHTML = ""; // Clear existing options

    userUCs.forEach(uc => {
    // Match UC code inside parentheses: e.g., "DEVI (11101004)"
    const match = uc.match(/^(.*)\s\((.*)\)$/);
    if (!match) return; // if format unexpected, skip

    const ucName = match[1].trim();   // "DEVI"
    const ucCode = match[2].trim();   // "11101004"

    // Only add if ucCode exists in ucCodes array
    if (ucCodes.includes(ucCode)) {
    const option = document.createElement("option");
    option.value = ucCode;      // value is UC code
    option.textContent = ucName; // text is UC name
    option.selected = true;
    option.disabled = true;     // prevents deselection individually
    ucSelect.appendChild(option);
}
});


    // Disable whole select so no changes allowed
    ucSelect.disabled = true;
    ucSelect.style.fontSize = "12px";           // Increase font size
    ucSelect.style.height = "40px";            // Height to show multiple options nicely
    ucSelect.style.width = "100%";               // Full width of container
    ucSelect.style.padding = "6px 10px";        // Optional padding for comfort
    ucSelect.style.borderRadius = "12px";       // Rounded corners as per your original style
    ucSelect.style.border = "1px solid #ccc";   // Border color
    ucSelect.style.backgroundColor = "#fefefe"; // Background color for clarity
    ucSelect.style.color = "#333";               // Text color for contrast

    // Disable whole select so no changes allowed
    ucSelect.disabled = true;
    if (entrySelect) {
    [...entrySelect.options].forEach(option => {
    if (option.value === entryPermission) {
    option.selected = true;
}
});
    entrySelect.disabled = true;
}
}
    // Set and disable Status select
    const statusSelect = document.getElementById("accountstatus");
    if (statusSelect) {
    const statusValue = status === "1" ? "Active" : "InActive";
    [...statusSelect.options].forEach(option => {
    if (option.value === statusValue) {
    option.selected = true;
}
});
    statusSelect.disabled = true;
}
    // Set Address textarea value
    const addressTextarea = document.getElementById("address");
    if (addressTextarea) {
    addressTextarea.value = currentAddress || "";
}

    // Set Designation input value
    const designationInput = document.getElementById("designation");
    if (designationInput) {
    designationInput.value = designation || "";
}

    // Set User Role select value
    const roleSelect = document.getElementById("userrole");
    if (roleSelect) {
    // Clear existing options
    roleSelect.innerHTML = '';

    // Add default disabled "Select" option
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Select';
    defaultOption.disabled = true;
    defaultOption.selected = true; // selected by default, unless userRole matches
    roleSelect.appendChild(defaultOption);

    // Your role options - you can hardcode or generate dynamically
    const roles = [
    {value: "1", text: "Administrator"},
    {value: "2", text: "National Manager"},
    {value: "3", text: "Province Manager"},
    {value: "11", text: "Division Manager"},
    {value: "4", text: "District Manager"},
    {value: "12", text: "Tehsil Manager"},
    {value: "5", text: "UC Manager"}
    ];
    roles.forEach(role => {
    const option = document.createElement('option');
    option.value = role.value;
    option.textContent = role.text;
    // console.log(role.value);
    if (userRole && role.value === userRole) {
    option.selected = true;
    defaultOption.selected = false;
    defaultOption.disabled = true;
}
    roleSelect.appendChild(option);
});
    defaultOption.disabled = true;
    roleSelect.disabled = true;

}

});

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
    const initialAffiliation = "{{ user_info.affiliation|escapejs }}";

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

    const userCnic = "{{user_info.cnic | escapejs}}";
    const userCnicExpiry = "{{user_info.cnicexpiry | escapejs}}"; // Assuming format DD-MM-YYYY
    const userContact = "{{user_info.mobile | escapejs}}";

    if (userCnic) {
    document.getElementById('cnic').value = userCnic;
}

    if (userCnicExpiry) {
    document.getElementById('dob').value = userCnicExpiry;
}

    if (userContact) {
    document.getElementById('contactnumber').value = userContact;
}

    const user_info = {
    email: "{{ user_info.email|escapejs }}",
    firstname: "{{ user_info.first_name|escapejs }}",
    lastname: "{{ user_info.last_name|escapejs }}",
    username: "{{ user_info.username|escapejs }}",
    gender: "{{ user_info.genderval|escapejs }}"
};
    console.log(user_info);
    document.getElementById('email').value = user_info.email || '';
    document.getElementById('firstname').value = user_info.firstname || '';
    document.getElementById('lastname').value = user_info.lastname || '';
    document.getElementById('username').value = user_info.username || '';

    const genderSelect = document.getElementById('gender');
    if (genderSelect && user_info && user_info.gender) {
    genderSelect.value = user_info.gender;

    // Optional: trigger change event if needed for any listeners or styling
    const event = new Event('change');
    genderSelect.dispatchEvent(event);
}
</script>


<script>
    const userUCsString = "{{ user_info.user_ucs|default:'[]'|escapejs }}"; // safe default empty list
    const fixedString = userUCsString.replace(/'/g, '"');
    const userUCs = JSON.parse(fixedString);

    const ucNamesString = userUCs
      .map(uc => uc.split(' (')[0])   // get part before '('
      .join(', ');                    // join with commas

    const isDivisionAdmin = Number("{{ user_info.is_division_admin|default:'0'|escapejs }}");
    const isProvinceAdmin = Number("{{ user_info.is_province_admin|default:'0'|escapejs }}");
    const isTehsilAdmin = Number("{{ user_info.is_tehsil_admin|default:'0'|escapejs }}");
    const isDistrictAdmin = Number("{{ user_info.is_district_admin|default:'0'|escapejs }}");

    const totalAdmins = isDivisionAdmin + isProvinceAdmin + isTehsilAdmin + isDistrictAdmin;

    const flag = (totalAdmins === 1) ? "Yes" : "No";

    const user_infos = {
    email: "{{ user_info.email|escapejs }}",
    firstname: "{{ user_info.first_name|escapejs }}",
    lastname: "{{ user_info.last_name|escapejs }}",
    username: "{{ user_info.username|escapejs }}",
    gender: "{{ user_info.genderval|escapejs }}",
    phone: "{{ user_info.mobile|escapejs }}",
    cnic: "{{ user_info.cnic|escapejs }}",
    province: "{{ user_info.province_name|escapejs }}",
    division: "{{ user_info.division_name|escapejs }}",
    district: "{{ user_info.district_name|escapejs }}",
    designation: "{{ user_info.designation|escapejs }}",
    tehsil: "{{ user_info.tehsil_name|escapejs }}",
    uc: ucNamesString,
    is_admin: flag,
    status: "{{ user_info.status|yesno:'true,false' }}".toLowerCase() === "true",
    entry_allowed: "{{ user_info.entrypermission|default:'No'|escapejs }}"
};

    document.addEventListener("DOMContentLoaded", () => {
    const mapping = {
    "First Name": user_infos.firstname,
    "Last Name": user_infos.lastname,
    "Email Address": user_infos.email,
    "Phone": user_infos.phone,
    "CNIC #": user_infos.cnic,
    "Gender": user_infos.gender,
    "Province": user_infos.province,
    "Division": user_infos.division,
    "District": user_infos.district,
    "Tehsil": user_infos.tehsil,
    "UC": user_infos.uc,
    "Is Admin?": user_infos.is_admin,
    "Status": user_infos.status ? "Active" : "Inactive",
    "Entry Allowed": user_infos.entry_allowed
};

    const container = document.getElementById("user-details");
    if (!container) return;

    container.querySelectorAll("div").forEach(div => {
    const label = div.querySelector("p:first-child")?.textContent?.trim();
    if (label && mapping.hasOwnProperty(label)) {
    const valueP = div.querySelector("p:last-child");
    if (valueP) valueP.textContent = mapping[label];
}
});

    const usernameEl = document.getElementById("usernames");
    if (usernameEl) {
    usernameEl.textContent = `${user_info.firstname} ${user_info.lastname}`;
}

    // Set designation
    const designationEl = document.getElementById("userdesignation");
    if (designationEl) {
    designationEl.textContent = user_infos.designation || "N/A";  // Replace with actual user_info field for role
}

});
</script>

<script>
    document.addEventListener("DOMContentLoaded", function () {
    const roleSelect = document.getElementById("userrole");
    const userType = parseInt("{{ user_info.usertype }}");
    console.log(userType)
    // Admin flags from backend (set to "1" or "0" as strings)
    const adminFlags = {
    province: "{{ user_info.is_province_admin|default:'0'|escapejs }}",
    division: "{{ user_info.is_division_admin|default:'0'|escapejs }}",
    district: "{{ user_info.is_district_admin|default:'0'|escapejs }}",
    tehsil: "{{ user_info.is_tehsil_admin|default:'0'|escapejs }}"
};
    console.log(adminFlags)
    const fields = {
    ProvinceMain: ["ProvinceSelected", "provinceToggle"],
    DivisionMain: ["DivisionSelected", "divisionToggle"],
    DistrictMain: ["DistrictSelected", "districtToggle"],
    TehsilMain: ["TehsilSelected", "tehsilToggle"],
    UCMain: []
};

    // Your existing functions hideAll, hideAndDisable, showAndEnable, etc.
    function disableToggle(toggleId) {
    const toggleContainer = document.getElementById(toggleId);
    if (!toggleContainer) return;

    // Hide container or keep visible but disabled — your choice
    // toggleContainer.classList.add("hidden");
    // toggleContainer.style.display = "none";

    // Or just disable input and gray out UI, but keep visible:
    toggleContainer.style.pointerEvents = "none"; // disable mouse events
    toggleContainer.style.opacity = "0.5"; // make it visually disabled

    // Disable the checkbox inside
    const checkbox = toggleContainer.querySelector('input[type="checkbox"].role-toggle');
    if (checkbox) {
    checkbox.disabled = true;
}
}

    function enableAndTurnOnToggle(toggleId) {
    const toggleContainer = document.getElementById(toggleId);
    if (!toggleContainer) return;

    // Show container
    toggleContainer.classList.remove("hidden");
    toggleContainer.style.display = "block";

    // Enable container
    toggleContainer.removeAttribute("disabled");

}
    function autoClickToggles() {
    const toggleElements = document.querySelectorAll('[data-toggle-scope] input[type="checkbox"].role-toggle');
    toggleElements.forEach(toggleCheckbox => {
    if (toggleCheckbox) {
    toggleCheckbox.click(); // trigger Alpine toggle
}
});
}

    function enableTogglesByAdminFlags() {
    // Province toggle
    if (adminFlags.province === "1" && userType === 3) {
    enableAndTurnOnToggle("provinceToggle", true);
    autoClickToggles();
    disableToggle("provinceToggle");

}

    // Division toggle
    if (adminFlags.division === "1" && userType === 11) {
    enableAndTurnOnToggle("divisionToggle", true);
    autoClickToggles();
    disableToggle("divisionToggle");

}

    // District toggle
    if (adminFlags.district === "1" && userType === 4) {
    enableAndTurnOnToggle("districtToggle", true);
    autoClickToggles();
    disableToggle("districtToggle");
}

    // Tehsil toggle
    if (adminFlags.tehsil === "1" && userType === 12) {
    enableAndTurnOnToggle("tehsilToggle", true);
    autoClickToggles();
    disableToggle("tehsilToggle");
}
}

    enableTogglesByAdminFlags();
});

</script>


<script>
    document.getElementById('password').removeAttribute('required');
    document.getElementById('repeatpassword').removeAttribute('required');

    document.getElementById("update_user_profile").addEventListener("submit", async function (e) {
    e.preventDefault();
    const pwd = document.getElementById('password').value.trim();
    const repeatPwd = document.getElementById('repeatpassword').value.trim();

    // If user typed anything in password
    if (pwd.length > 0) {
    // Check repeat password exists and matches
    if (repeatPwd.length === 0 || pwd !== repeatPwd) {
      e.preventDefault(); // stop form submission
      toastr.error('Both password and repeat password must be filled and match.');
      // optionally focus on repeat password
      document.getElementById('repeatpassword').focus();
      return false;
    }
    }

    const form = e.target;
    const formData = new FormData(form);
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    // Show loading indicator
  Swal.fire({
    title: 'Updating...',
    didOpen: () => {
      Swal.showLoading();
    },
    allowOutsideClick: false
  });
    try {
    const response = await fetch(form.action, {
    method: "POST",
    headers: {
    "X-CSRFToken": csrfToken
},
    body: formData
});

    const data = await response.json();

    if (response.ok) {
    Swal.fire({
    icon: 'success',
    title: 'Success',
    text: 'User updated successfully!',
    timer: 2500,
    timerProgressBar: true,
    showConfirmButton: false
});
    showProfileModal = false;
    location.reload();
} else {
    Swal.fire({
    icon: 'error',
    title: 'Error',
    text: data.message || data.detail || 'Something went wrong.',
    timer: 3000,
    timerProgressBar: true
});
}
} catch (error) {
    Swal.fire({
    icon: 'error',
    title: 'Network Error',
    text: 'Network error. Try again.',
    timer: 3000,
    timerProgressBar: true
});
    console.error(error);
}
});
</script>
