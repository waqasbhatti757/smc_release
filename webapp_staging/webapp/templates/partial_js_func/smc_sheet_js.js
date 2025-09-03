<script>
    let editingTeamId = null; // global variable, tracks Add vs Edit
    let editingChildRecord = null;
    let aicid=null;
</script>
<script type="module">
    import {API_BASE_URL} from "/static/apiConfig.js";
    window.API_BASE_URL = API_BASE_URL; // expose it globally
</script>
<script>
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('expectedReturn').setAttribute('max', today);
</script>
<script src="https://cdn.jsdelivr.net/npm/litepicker/dist/litepicker.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
<link href="https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.css" rel="stylesheet"/>

<script>
document.addEventListener("DOMContentLoaded", function () {
    function attachLitepickers() {
        document.querySelectorAll(".date-input").forEach(input => {
            // prevent duplicate Litepicker bindings
            if (input.dataset.pickerAttached) return;

            new Litepicker({
                element: input,
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

            input.dataset.pickerAttached = "true";
        });
    }

    // attach immediately for static inputs
    attachLitepickers();

    // re-attach after dynamically adding rows
    const tableBody = document.getElementById("childrenTableBody");
    const observer = new MutationObserver(() => attachLitepickers());
    observer.observe(tableBody, { childList: true, subtree: true });
});
</script>

<script defer>
    (async function () {
    window.user_info = null;
    window.userVars = null;

    async function loadUserInfo() {
    const res = await fetch("{% url 'usermanagement:get_user_info_for_js' %}");
    if (!res.ok) throw new Error("Failed to fetch user info");
    window.user_info = await res.json();
    buildUserVars(window.user_info);
    console.log("Global userinfo loaded:", window.user_info);
}

    function buildUserVars(i) {
    const t = i?.usertype ?? null;
    const sanitize = v => (v === undefined || v === null || v === '' ? null : v);
    const onlyIf = (cond, val) => (cond ? sanitize(val) : null);

    window.userVars = {
    idoffice: onlyIf([3, 11, 4, 12, 5].includes(t), i.idoffice),
    division_code: onlyIf([11, 4, 12, 5].includes(t), i.division_code),
    districtcode: onlyIf([4, 12, 5].includes(t), i.district_code ?? i.districtcode),
    tehsilcode: onlyIf([12, 5].includes(t), i.tehsil_code ?? i.tehsilcode),
    uc_codes: t === 5
    ? (Array.isArray(i.uc_codes)
    ? i.uc_codes.map(x => parseInt(x, 10))
    : (typeof i.uc_codes === "string"
    ? i.uc_codes.split(",").map(x => parseInt(x, 10))
    : null
    )
    )
    : null
};
    document.dispatchEvent(new Event("userInfoReady"));
    console.log("userVars:", window.userVars);
}

    // ✅ Wait for user info BEFORE running the rest
    await loadUserInfo();

    // 🔥 Now safe: rest of your code here
    console.log("Ready to run rest of script, userVars:", window.userVars);

})();
</script>
<script>
    // Generic functions
    function disableDiv(divId) {
    const div = document.getElementById(divId);
    if (div) {
    div.style.pointerEvents = "none";   // stops clicks, typing, etc.
    div.style.opacity = "0.5";          // dim it
}
}

    function enableDiv(divId) {
    const div = document.getElementById(divId);
    if (div) {
    div.style.pointerEvents = "auto";   // restore interaction
    div.style.opacity = "1";            // full brightness
}
}

    function hideDiv(divId) {
    const div = document.getElementById(divId);
    if (div) {
    div.style.display = "none";         // hide completely
}
}

    function showDiv(divId) {
    const div = document.getElementById(divId);
    if (div) {
    div.style.display = "block";        // show again
}
}

    hideDiv("hideformlist");
</script>
<script>
    async function loadCampaigns() {
    try {
    // make sure global is defined
    if (!window.API_BASE_URL) {
    console.error("API_BASE_URL not available");
    return;
}

    const response = await fetch(`${window.API_BASE_URL}/campaign/campaigns/list`, {
    headers: {'accept': 'application/json'}
});

    const data = await response.json();
    const select = document.getElementById('campaign');

    // clear existing options
    select.innerHTML = "";

    if (data.status === "success" && Array.isArray(data.campaigns)) {
    // add placeholder option
    const placeholder = document.createElement('option');
    placeholder.textContent = "Select a campaign...";
    placeholder.disabled = true;
    placeholder.selected = true;
    select.appendChild(placeholder);

    data.campaigns.forEach(campaign => {
    const option = document.createElement('option');
    option.value = campaign.idcampaign;
    option.textContent = campaign.name;
    select.appendChild(option);
});
} else {
    const option = document.createElement('option');
    option.textContent = "No campaigns available";
    option.disabled = true;
    option.selected = true;
    select.appendChild(option);
}
} catch (error) {
    console.error("Error fetching campaigns:", error);
}
}

    // wait until DOM is ready AND API_BASE_URL is set
    document.addEventListener("DOMContentLoaded", () => {
    if (window.API_BASE_URL) {
    loadCampaigns();
} else {
    // in rare cases the module is still loading: poll until ready
    const checkInterval = setInterval(() => {
    if (window.API_BASE_URL) {
    clearInterval(checkInterval);
    loadCampaigns();
}
}, 50);
}
});
</script>
<script>
    document.addEventListener("DOMContentLoaded", () => {
    const campaignSelect = document.getElementById('campaign');
    const provinceSelect = document.getElementById('province');
    const divisionSelect = document.getElementById('division');
    const districtSelect = document.getElementById('district');
    const tehsilSelect = document.getElementById('tehsil');
    const ucSelect = document.getElementById('uc');

    const selects = [provinceSelect, divisionSelect, districtSelect, tehsilSelect, ucSelect];

    // Reset dropdown
    const resetDropdown = (selectEl, placeholder) => {
    selectEl.innerHTML = `<option value="" disabled selected>${placeholder}</option>`;
};

    // Populate dropdown
    const populateDropdown = (selectEl, data, valueKey, textKey) => {
    resetDropdown(selectEl, `Select ${selectEl.name}`);
    data.forEach(item => {
    const option = document.createElement('option');
    option.value = item[valueKey];
    option.textContent = item[textKey];
    selectEl.appendChild(option);
});
};

    // Clear all lower-level selects
    const resetLower = (fromIndex) => {
    for (let i = fromIndex; i < selects.length; i++) {
    resetDropdown(selects[i], `Select ${selects[i].name}`);
}
};

    // --- Campaign change ---
    campaignSelect.addEventListener("change", async () => {
    const campaignId = parseInt(campaignSelect.value, 10);
    const userType = window.user_info?.usertype ?? null;
    const geoid = [3,4,5,11,12].includes(userType) ? window.userVars?.idoffice ?? null : null;

    resetLower(0);


    try {
    const res = await fetch(`${window.API_BASE_URL}/campaign/campaign/aic/provinces`, {
    method: 'POST',
    headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
    body: JSON.stringify({campaignid: campaignId, geoid})
});
    const data = await res.json();
    if (data.status === "success" && Array.isArray(data.provinces)) {
    populateDropdown(provinceSelect, data.provinces, 'code', 'name');
    if (provinceSelect && geoid !== null) {
    const option = [...provinceSelect.options].find(opt => opt.value == geoid);
    if (option) {
    option.selected = true;
    provinceSelect.dispatchEvent(new Event("change")); // optional if you want cascade
} else {
    console.warn("No matching option found for geoid:", geoid);
}
}
}
} catch(err){console.error(err);}
});

    // --- Province change ---
    provinceSelect.addEventListener("change", async () => {
    const campaignId = parseInt(campaignSelect.value, 10);
    const provinceId = parseInt(provinceSelect.value, 10);
    const userType = window.user_info?.usertype ?? null;
    const geodivid = [4,5,11,12].includes(userType) ? window.userVars?.division_code ?? null : null;

    resetLower(1);

    try {
    const res = await fetch(`${window.API_BASE_URL}/campaign/campaign/aic/division`, {
    method: 'POST',
    headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
    body: JSON.stringify({campaignid: campaignId, geoprovid: provinceId, geodivid})
});
    const data = await res.json();
    if (data.status === "success" && Array.isArray(data.divisions)) {
    populateDropdown(divisionSelect, data.divisions, 'code', 'dname');
    if (divisionSelect && geodivid !== null) {
    const option = [...divisionSelect.options].find(opt => opt.value == geodivid);
    if (option) {
    option.selected = true;
    divisionSelect.dispatchEvent(new Event("change")); // optional if you want cascade
} else {
    console.warn("No matching option found for geoid:", geodivid);
}
}
}
} catch(err){console.error(err);}
});

    // --- Division change ---
    divisionSelect.addEventListener("change", async () => {
    const campaignId = parseInt(campaignSelect.value, 10);
    const divisionId = parseInt(divisionSelect.value, 10);
    const provinceId = parseInt(provinceSelect.value, 10);
    const userType = window.user_info?.usertype ?? null;
    const districtcode = [4,5,12].includes(userType) ? window.userVars?.districtcode ?? null : null;

    resetLower(2);

    try {
    const res = await fetch(`${window.API_BASE_URL}/campaign/campaign/aic/district`, {
    method: 'POST',
    headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
    body: JSON.stringify({campaignid: campaignId, geodivid: divisionId, geodisid: districtcode})
});
    const data = await res.json();
    if (data.status === "success" && Array.isArray(data.districts)) {
    populateDropdown(districtSelect, data.districts, 'code', 'dname');
    if (districtSelect && districtcode !== null) {
    const option = [...districtSelect.options].find(opt => opt.value == districtcode);
    if (option) {
    option.selected = true;
    districtSelect.dispatchEvent(new Event("change")); // optional if you want cascade
} else {
    console.warn("No matching option found for geoid:", districtcode);
}
}
}
} catch(err){console.error(err);}
});

    // --- District change ---
    districtSelect.addEventListener("change", async () => {
    const campaignId = parseInt(campaignSelect.value, 10);
    const districtId = parseInt(districtSelect.value, 10);
    const userType = window.user_info?.usertype ?? null;
    const tehsilcode = [5,12].includes(userType) ? window.userVars?.tehsilcode ?? null : null;

    resetLower(3);

    try {
    const res = await fetch(`${window.API_BASE_URL}/campaign/campaign/aic/tehsil`, {
    method: 'POST',
    headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
    body: JSON.stringify({campaignid: campaignId, geodisid: districtId, geotehid: tehsilcode})
});
    const data = await res.json();
    if (data.status === "success" && Array.isArray(data.tehsils)) {
    populateDropdown(tehsilSelect, data.tehsils, 'tehsil_code', 'tehsil_name');
    if (tehsilSelect && tehsilcode !== null) {
    const option = [...tehsilSelect.options].find(opt => opt.value == tehsilcode);
    if (option) {
    option.selected = true;
    tehsilSelect.dispatchEvent(new Event("change")); // optional if you want cascade
} else {
    console.warn("No matching option found for geoid:", tehsilcode);
}
}
}
} catch(err){console.error(err);}
});

    // --- Tehsil change ---
    tehsilSelect.addEventListener("change", async () => {
    const campaignId = parseInt(campaignSelect.value, 10);
    const tehsilId = parseInt(tehsilSelect.value, 10);
    const userType = window.user_info?.usertype ?? null;
    const uccodes = (userType === 5 && Array.isArray(window.userVars?.uc_codes))
    ? window.userVars.uc_codes
    : null;

    resetLower(4);

    try {
    const res = await fetch(`${window.API_BASE_URL}/campaign/campaign/aic/ucs`, {
    method: 'POST',
    headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
    body: JSON.stringify({campaignid: campaignId, geotehid: tehsilId, geoucid: uccodes})
});
    const data = await res.json();
    if (data.status === "success" && Array.isArray(data.ucs)) {
    populateDropdown(ucSelect, data.ucs, 'code', 'uctname');
}
} catch(err){console.error(err);}
});


});
</script>
<script>
const editSmcForm = document.getElementById("editsmcform");
const tableBody = document.getElementById("childrenTableBody");

editSmcForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    showDiv("hideformlist");
    try {
        const payload = {
            idcampaign: parseInt(document.getElementById("campaign").value, 10),
            iduc: parseInt(document.getElementById("uc").value, 10)
        };

        const res = await fetch(`${window.API_BASE_URL}/campaign/read/smc-sheet-stats`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const json = await res.json();

        // clear table body
        tableBody.innerHTML = "";

        if (json.status === "success" && Array.isArray(json.data)) {
            json.data.forEach((row) => {
                const tr = document.createElement("tr");

                tr.innerHTML = `
                    <td class="px-3 py-2">${row.campaign_name}</td>
                    <td class="px-3 py-2">${row.pname}</td>
                    <td class="px-3 py-2">${row.divname}</td>
                    <td class="px-3 py-2">${row.districtname}</td>
                    <td class="px-3 py-2">${row.tehsilname}</td>
                    <td class="px-3 py-2">${row.ucname}</td>
                    <td class="px-3 py-2">${row.aicid}</td>
                    <td class="px-3 py-2">${row.supervisor_name}</td>
                    <td class="px-3 py-2">${row.totalteams}</td>
                    <td class="px-3 py-2">${row.totalchildren}</td>
                    <td class="px-3 py-2">${row.username}</td>
                    <td class="px-3 py-2 text-center">
                        <button class="inline-flex items-center px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded-md shadow-sm transition-all duration-150">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                                 stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                                 class="lucide lucide-trash-icon lucide-trash mr-1">
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/>
                                <path d="M3 6h18"/>
                                <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                            </svg>
                            Delete
                        </button>
                    </td>
                `;

                tableBody.appendChild(tr);
            });
        } else {
            const tr = document.createElement("tr");
            tr.innerHTML = `<td colspan="12" class="px-3 py-2 text-center text-gray-500">No records found</td>`;
            tableBody.appendChild(tr);
        }
    } catch (err) {
        console.error("Error fetching data:", err);
    } finally {
        submitBtn.disabled = false;
    }
});

</script>
