<script>
    let editingTeamId = null; // global variable, tracks Add vs Edit
    let editingChildRecord = null;
</script>
<script type="module">
    import {API_BASE_URL} from "/static/apiConfig.js";
    window.API_BASE_URL = API_BASE_URL; // expose it globally
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
    function setupTablePagination({
    tableBody,
    searchInput,
    prevBtn,
    nextBtn,
    pageInfo,
    rowsPerPage = 5
}) {
    let currentPage = 1;

    function paginate() {
    const rows = Array.from(tableBody.querySelectorAll("tr"));
    const filter = (searchInput?.value || "").toLowerCase();

    // Filter rows
    const filteredRows = filter
    ? rows.filter(row => row.innerText.toLowerCase().includes(filter))
    : rows;

    // Compute pages
    const totalPages = Math.max(1, Math.ceil(filteredRows.length / rowsPerPage));

    // Clamp current page
    currentPage = Math.min(Math.max(currentPage, 1), totalPages);

    // Hide all rows
    rows.forEach(row => (row.style.display = "none"));

    // Show only current page slice
    const start = (currentPage - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    filteredRows.slice(start, end).forEach(row => (row.style.display = ""));

    // Update UI
    pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    prevBtn.disabled = currentPage === 1 || filteredRows.length === 0;
    nextBtn.disabled = currentPage === totalPages || filteredRows.length === 0;
}

    // Reset pagination and rerun
    function resetPagination() {
    currentPage = 1;
    paginate();
}

    // Event listeners
    searchInput.addEventListener("input", resetPagination);

    prevBtn.addEventListener("click", () => {
    if (currentPage > 1) {
    currentPage--;
    paginate();
}
});

    nextBtn.addEventListener("click", () => {
    currentPage++;
    paginate();
});

    // Observe table changes
    const observer = new MutationObserver(resetPagination);
    observer.observe(tableBody, {childList: true});

    // Initial call
    if (tableBody.querySelector("tr")) resetPagination();

    // Return function to manually reapply pagination if needed
    return {paginate, resetPagination};
}

</script>
<script>
    const modal = document.getElementById("profileModal");
    const openBtn = document.getElementById("openModalBtn");
    const editdata = document.getElementById("editdata");
    const closeBtn = document.getElementById("closeModalBtn");

    // Open modal (main button + delete button)
    openBtn.addEventListener("click", () => modal.classList.remove("hidden"));
    editdata.addEventListener("click", () => modal.classList.remove("hidden"));

    // Close modal (X button)
    closeBtn.addEventListener("click", () => modal.classList.add("hidden"));

    // Close modal if clicking outside
    window.addEventListener("click", (e) => {
    if (e.target === modal) {
    modal.classList.add("hidden");
}
});
</script>

<script>
    // Open modal
    document.getElementById('openChildModal').addEventListener('click', function () {
    document.getElementById('childModal').classList.remove('hidden');
});
</script>
<script>
function openTeamModal() {
    document.getElementById('teamModal').classList.remove('hidden');
    document.getElementById('teamModal').classList.add('flex');
}
function closeTeamModal() {
    document.getElementById('teamModal').classList.remove('flex');
    document.getElementById('teamModal').classList.add('hidden');
}
</script>
<script>
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('expectedReturn').setAttribute('max', today);
</script>
<script src="https://cdn.jsdelivr.net/npm/litepicker/dist/litepicker.js"></script>

<script>
document.addEventListener("DOMContentLoaded", function () {
    const today = new Date(); // Current date

    const picker = new Litepicker({
        element: document.getElementById("date"),
        format: "DD-MM-YYYY",
        autoApply: true,
        allowRepick: true,
        minDate: today, // Only allow today or future dates
        dropdowns: {
            minYear: today.getFullYear(), // start from current year
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
    const openBtn = document.getElementById("openModalBtn");
    const closeBtn = document.getElementById("closeModalBtn");
    const modal = document.getElementById("profileModal");

    openBtn.addEventListener("click", () => {
    modal.classList.remove("hidden");
});

    closeBtn.addEventListener("click", () => {
    modal.classList.add("hidden");
});

    // Optional: close if clicked outside modal
    window.addEventListener("click", (e) => {
    if (e.target === modal) {
    modal.classList.add("hidden");
}
});
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

    // Apply your case:
    hideDiv("childinformation");
    enableDiv("aicinformation");
    disableDiv("teaminformation");
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
    const select = document.getElementById('campaignname');

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
    document.addEventListener("userInfoReady", () => {
    window.user_info.usertype
});
</script>

<script>
    document.addEventListener("DOMContentLoaded", () => {
    const campaignSelect = document.getElementById('campaignname');
    const provinceSelect = document.getElementById('provincename');
    const divisionSelect = document.getElementById('divisionname');
    const districtSelect = document.getElementById('districtname');
    const tehsilSelect = document.getElementById('tehsilname');
    const ucSelect = document.getElementById('ucname');

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
<script src="https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>

<!-- toastr -->
<link href="https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.css" rel="stylesheet"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.js"></script>

<!-- sweetalert2 -->
<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>

<script>
document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");
    const submitBtn = document.getElementById("submitmydata");
    toastr.options = {
        closeButton: true,
        progressBar: true,
        positionClass: "toast-top-right",
        preventDuplicates: true,
        timeOut: 4000,
        extendedTimeOut: 2000,
        showClass: "animate__animated animate__fadeInDown",
        hideClass: "animate__animated animate__fadeOutUp"
    };
    submitBtn.addEventListener("click", async (e) => {
        e.preventDefault(); // stop native submit

        let valid = true;
        let firstInvalid = null;

        // validate all required fields
        form.querySelectorAll("[required]").forEach(field => {
            if (!field.value || field.value.trim() === "") {
                valid = false;
                if (!firstInvalid) firstInvalid = field;

                toastr.error(
                    `${field.name.replace(/name/i, " Name")} is required`,
                    "Validation Error"
                );
            }
        });

        if (!valid) {
            if (firstInvalid) firstInvalid.focus();
            return;
        }

        // collect data
        const payload = {
            idcampaign: form.querySelector("#campaignname").value,
            iduc: form.querySelector("#ucname").value,
            supervisor_name: form.querySelector("#aicname").value,
            supervisor_full_name: form.querySelector("#fullname").value,
            enteredby: window.user_info?.idusers || 10 // fallback
        };

        try {
            const response = await fetch(`${window.API_BASE_URL}/campaign/campaign/createheader`, {
                method: "POST",
                headers: {
                    "accept": "application/json",
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (data && data.status === "success") {
                // success alert
                Swal.fire({
                    icon: "success",
                    title: "AIC Successfully Added",
                    text: `Header ID: ${data.idheader ?? "N/A"}`,
                    showConfirmButton: false,
                    confirmButtonColor: "#3085d6",
                    timer: 1500,          // Auto close after 1500ms
                    timerProgressBar: true
                });

                // reset form
                // form.reset();
                const aicSpan = document.getElementById("addaiccode");
                if (aicSpan) {
                    aicSpan.textContent = `SMC Sheet#: SMC-${data.idheader}`;
                }
                disableDiv("aicinformation");
                enableDiv("teaminformation");

            } else {
                // error alert
                Swal.fire({
                    icon: "error",
                    title: "Failed to Add AIC",
                    text: data.detail || data.message || "Something went wrong.",
                    confirmButtonColor: "#d33"
                });
            }
        } catch (err) {
            Swal.fire({
                icon: "error",
                title: "Server Error",
                text: err.message || "Could not connect to server.",
                confirmButtonColor: "#d33"
            });
        }
    });
});
</script>
<script>

    document.addEventListener("DOMContentLoaded", () => {
    const submitBtn = document.getElementById("submitTeam");
    const form = document.querySelector("#teamModal form"); // grab form inside modal
    const modal = document.getElementById("teamModal");    // grab the modal itself

    submitBtn.addEventListener("click", async (e) => {
        e.preventDefault(); // stop native submit
        // Grab values
        const team_no = document.getElementById("teamNumber").value.trim();
        const team_member = document.getElementById("teamName").value.trim();

        if (!team_no) {
            Swal.fire({
                icon: "error",
                title: "Validation Error",
                text: "Please fill in all required fields",
                confirmButtonColor: "#d33"
            });
            return;
        }

        // Get current AIC header
        const aicSpan = document.getElementById("addaiccode");
        const match = aicSpan.textContent.match(/SMC-(\d+)/);
        const idheader = match ? parseInt(match[1], 10) : null;

        if (!idheader) {
            Swal.fire({
                icon: "error",
                title: "AIC Header Missing",
                text: "Cannot find current AIC number",
                confirmButtonColor: "#d33"
            });
            return;
        }

        const enteredby = window.user_info?.idusers ?? null;
        if (!enteredby) {
            Swal.fire({
                icon: "error",
                title: "User Info Missing",
                text: "Cannot determine the logged-in user",
                confirmButtonColor: "#d33"
            });
            return;
        }

        const payload = { idheader, team_no, team_member, enteredby, teamtype: 1 };
        const payload2 = { idteam: editingTeamId, team_no, team_member};
        let res;
        try {
            if (editingTeamId){
                res = await fetch(`${window.API_BASE_URL}/campaign/campaign/updateteam`, {
                    method: "POST",
                    headers: { "Accept": "application/json", "Content-Type": "application/json" },
                    body: JSON.stringify(payload2)
                });
            }
            else {
                res = await fetch(`${window.API_BASE_URL}/campaign/campaign/createteam`, {
                    method: "POST",
                    headers: { "Accept": "application/json", "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
            }


            const data = await res.json();

            if (data.status === "success") {
                Swal.fire({
                    icon: "success",
                    title: "Team Info Successfully Proceed",
                    text: `Team ID: ${data.idteam}`,
                    showConfirmButton: false,
                    confirmButtonColor: "#3085d6",
                    timer: 1500,          // Auto close after 1500ms
                    timerProgressBar: true

                });
                form.reset(); // now works
                modal.removeAttribute("open");
                loadTeamData(idheader);
                editingTeamId=null;
                showDiv("childinformation");
                loadTeamOptions(idheader);
                toggleElementsById(["openModalBtn", "missedChildrenTable", "currentPage2", "nextpage2","pageInfo2", "prevpage2","tableSearch2"],"hide");
            } else {
                Swal.fire({
                    icon: "error",
                    title: "Failed to Add/Edit Team",
                    text: data.message || "Something went wrong.",
                    showConfirmButton: false,
                    confirmButtonColor: "#3085d6",
                    timer: 1500,          // Auto close after 1500ms
                    timerProgressBar: true

                });
            }
        } catch (err) {
            Swal.fire({
                icon: "error",
                title: "Server Error",
                text: err.message || "Could not connect to server",
                showConfirmButton: false,
                confirmButtonColor: "#3085d6",
                timer: 1500,          // Auto close after 1500ms
                timerProgressBar: true

            });
        }
    });
});
    const paginations = setupTablePagination({
    tableBody: document.getElementById("tableBody"),
    searchInput: document.getElementById("tableSearch"),
    prevBtn: document.getElementById("prevPage"),
    nextBtn: document.getElementById("nextPage"),
    pageInfo: document.getElementById("pageInfo"),
    rowsPerPage: 3 // any number you want
});

    // If you fetch new rows dynamically later, just call:
    paginations.resetPagination();

</script>

<script>
const rowsPerPage = 3;
let currentPage = 1;
const tableBody = document.getElementById("tableBody");
const searchInput = document.getElementById("tableSearch");

async function loadTeamData(idheader) {
    if (!tableBody) return;

    // Clear table
    tableBody.innerHTML = "";

    try {
        const response = await fetch(`${window.API_BASE_URL}/campaign/campaign/get/teamdata?idheader=${idheader}`, {
            method: "POST",
            headers: { "accept": "application/json" }
        });
        const data = await response.json();

        if (data.status !== "success" || !data.data || data.data.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="4" class="text-center py-4">No team members found</td></tr>`;
        } else {
            data.data.forEach((team,i) => {
                const row = document.createElement("tr");
                row.classList.add("hover:bg-gray-50", "transition-colors", "duration-150");
                row.innerHTML = `
                    <td class="px-6 py-2 border-b border-gray-200">${i+1}</td>
                    <td class="px-6 py-2 border-b border-gray-200">${team.idteam}</td>
                    <td class="px-6 py-2 border-b border-gray-200 font-medium text-gray-900">${team.team_no}</td>
                    <td class="px-6 py-2 border-b border-gray-200">${team.team_member}</td>
                    <td class="px-6 py-2 border-b border-gray-200 text-center flex justify-center space-x-2">
                        <button type="button"
                                class="edit-btn text-blue-600 hover:text-blue-800 px-3 py-2 bg-blue-100 hover:bg-blue-200 rounded-lg flex items-center justify-center transition"
                                data-idteam="${team.idteam}"
                                data-teamno="${team.team_no}"
                                data-teammember="${team.team_member}">
                          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
                               fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                               stroke-linejoin="round">
                            <path d="M13 21h8"/>
                            <path d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z"/>
                          </svg>
                        </button>
                        <button onclick="deleteTeamMember('${team.idteam}')"
                                class="text-red-600 hover:text-red-800 px-3 py-2 bg-red-100 hover:bg-red-200 rounded-lg flex items-center justify-center transition">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
                                 fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                 stroke-linejoin="round">
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/>
                                <path d="M3 6h18"/>
                                <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                            </svg>
                        </button>
                    </td>
                `;

                tableBody.appendChild(row);
            });
        }

        // Save rows for pagination

    } catch (err) {
        console.error("Failed to load team data:", err);
        tableBody.innerHTML = `<tr><td colspan="4" class="text-center py-4 text-red-600">Error loading data</td></tr>`;
        tableBody.filteredRows = Array.from(tableBody.getElementsByTagName("tr"));
    }
}

</script>
<script>

// Utilities to show/hide the modal (Tailwind: hidden <-> flex)
function showTeamModal() {
  const modal = document.getElementById('teamModal');
  modal.classList.remove('hidden');
  modal.classList.add('flex');
}
function hideTeamModal() {
  const modal = document.getElementById('teamModal');
  modal.classList.remove('flex');
  modal.classList.add('hidden');

  // reset state
  editingTeamId = null;
  document.getElementById('teamNumber').value = '';
  document.getElementById('teamName').value = '';
  // optional: reset title
  const title = document.getElementById('modalTitle');
  if (title) title.querySelector('span.flex-none').textContent = 'ADD TEAM INFORMATION';
}

// Expose close for your ✕ button if it uses onclick
window.closeTeamModal = hideTeamModal;

// Open for "Add Team" button (if you have one calling this)
window.openTeamModal = function () {
  const title = document.getElementById('modalTitle');
  if (title) title.querySelector('span.flex-none').textContent = 'ADD TEAM INFORMATION';
  showTeamModal();
};

// Delegate clicks for ANY .edit-btn (no globals needed on the button)
document.addEventListener('click', function (e) {
  const btn = e.target.closest('.edit-btn');
  if (!btn) return;

  const idteam = btn.dataset.idteam;
  const team_no = btn.dataset.teamno;
  const team_member = btn.dataset.teammember;

  // Fill fields
  document.getElementById('teamNumber').value = team_no || '';
  document.getElementById('teamName').value = team_member || '';

  // Title: Edit mode
  const title = document.getElementById('modalTitle');
  if (title) title.querySelector('span.flex-none').textContent = 'EDIT TEAM INFORMATION';

  editingTeamId = idteam || null;
  showTeamModal();
});

// Quality-of-life: close on backdrop click + ESC
document.getElementById('teamModal')?.addEventListener('click', function (e) {
  if (e.target.id === 'teamModal') hideTeamModal();
});
document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') hideTeamModal();
});
</script>

<script>
async function loadTeamOptions(idheader) {
    const select = document.getElementById("setoptions");

    // Reset the select box before loading
    select.innerHTML = `<option value="">Choose a Team</option>`;

    try {
        const res = await fetch(`${window.API_BASE_URL}/campaign/campaign/get/setentryheader?idheader=${idheader}`, {
            method: "POST",
            headers: { "Accept": "application/json" }
        });

        const data = await res.json();

        if (data.status === "success" && data.data.length > 0) {
            data.data.forEach(team => {
                const option = document.createElement("option");
                option.value = team.value;
                option.textContent = team.label;
                select.appendChild(option);
            });
        } else {
            // No team members
            const opt = document.createElement("option");
            opt.value = "";
            opt.textContent = "No teams found";
            select.appendChild(opt);
        }
    } catch (err) {
        console.error("Error loading team options:", err);
        const opt = document.createElement("option");
        opt.value = "";
        opt.textContent = "Error loading teams";
        select.appendChild(opt);
    }
}
</script>
<script>
function toggleElementsById(ids, state) {
    ids.forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;

        if (state === 'show') {
            el.classList.remove('hidden');
        } else if (state === 'hide') {
            el.classList.add('hidden');
        } else {
            // toggle
            el.classList.toggle('hidden');
        }
    });
}

</script>
<script>
    document.getElementById("setoptions").addEventListener("change", function () {
        toggleElementsById(["openModalBtn", "missedChildrenTable", "currentPage2","pageInfo2", "nextpage2", "prevpage2","tableSearch2"],'show');
    });
</script>
<script>
const missedReason = document.getElementById("missedReason");
const subReason = document.getElementById("subReason");

// Predefined sub reasons
const optionsMap = {
  NotAvailable: [
    { value: "In School", label: "In School" },
    { value: "Inside District", label: "Inside District" },
    { value: "Outside District", label: "Outside District" },
    { value: "Outside UC", label: "Outside UC" },
    { value: "Sleeping", label: "Sleeping" }
  ],
  Refusal: [
    { value: "Religious Matter", label: "Religious Matter" },
    { value: "Misconception", label: "Misconception" },
    { value: "Safety", label: "Safety" },
    { value: "Demands", label: "Demands" },
    { value: "Repeated Campaigns", label: "Repeated Campaigns" },
    { value: "Direct Refusal", label: "Direct Refusal" },
    { value: "Sickness", label: "Sickness" },
    { value: "Silent Refusal", label: "Silent Refusal" }
  ]
};

// Handle change
missedReason.addEventListener("change", function () {
  const selected = this.value;
  subReason.innerHTML = '<option value="" disabled selected>Sub Reason</option>';

  if (!selected) {
    subReason.disabled = true;
    return;
  }

  if (selected === "LockedHouse") {
    subReason.disabled = true; // disable sub reason
    return;
  }

  // Load sub reasons dynamically
  const opts = optionsMap[selected] || [];
  opts.forEach(o => {
    const option = document.createElement("option");
    option.value = o.value;
    option.textContent = o.label;
    subReason.appendChild(option);
  });

  subReason.disabled = false; // enable only if options exist
});
document.getElementById("subReason").addEventListener("change", function () {
    const locationContainer = document.getElementById("locationContainer");
    const locationInput = document.getElementById("location");
    const value = this.value;

    if (value === "Outside District" || value === "Outside UC") {
        locationContainer.classList.remove("hidden");
        locationInput.setAttribute("required", "true");
    } else {
        locationContainer.classList.add("hidden");
        locationInput.removeAttribute("required");
        locationInput.value = ""; // clear old input if hidden
    }
});
</script>

<script>

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("update_user_profile");

    const tableBody2 = document.getElementById("tableBody2");
    let allRows2 = [];
    let filteredRows2 = [];

    // Fetch data from API
    async function fetchChildData(idheader, idteam) {
        try {
            const res = await fetch(`${window.API_BASE_URL}/campaign/campaign/get/childata`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ idheader, idteam })
            });
            const json = await res.json();

            if (json.status === "success" && Array.isArray(json.data)) {
                renderChildData(json.data);
            } else {
                tableBody2.innerHTML = `<tr><td colspan="14" class="px-6 py-4 text-center text-red-500">No records found</td></tr>`;
            }
        } catch (err) {
            console.error("API error:", err);
            tableBody2.innerHTML = `<tr><td colspan="14" class="px-6 py-4 text-center text-red-500">Failed to load data</td></tr>`;
        }
    }

    // Render rows into table
    function renderChildData(data) {
        tableBody2.innerHTML = "";

        data.forEach(child => {
            const row = document.createElement("tr");
            row.className = "hover:bg-gray-50 transition-colors";

            const dayText = `Day ${child.day}`;

            row.innerHTML = `
                <td class="px-6 py-4 border-b">${dayText}</td>
                <td class="px-6 py-4 border-b">${child.house || "-"}</td>
                <td class="px-6 py-4 border-b font-medium text-gray-900">${child.name || "-"}</td>
                <td class="px-6 py-4 border-b">${child.father || "-"}</td>
                <td class="px-6 py-4 border-b">${child.gender}</td>
                <td class="px-6 py-4 border-b">${child.age || "-"}</td>
                <td class="px-6 py-4 border-b">${child.nofmc || "-"}</td>
                <td class="px-6 py-4 border-b">${child.address || "-"}</td>
                <td class="px-6 py-4 border-b">${child.nodose}</td>
                <td class="px-6 py-4 border-b">${child.reject || "-"}</td>
                <td class="px-6 py-4 border-b">${child.location || "-"}</td>
                <td class="px-6 py-4 border-b">${child.hrmp}</td>
                <td class="px-6 py-4 border-b">${child.returndate || "-"}</td>
                <td class="px-6 py-4 border-b text-center flex justify-center space-x-2">
                    <button id="editdata" class="edit-button text-blue-600 hover:text-blue-800 px-3 py-2 bg-blue-100 hover:bg-blue-200 rounded-lg flex items-center justify-center transition" data-idchildren="${child.idchildren}">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18"
                             fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M13 21h8M21.174 6.812a1
                            1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321
                            4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0
                            .83-.497z"/>
                        </svg>
                    </button>
                    <button class="delete-button text-red-600 hover:text-red-800 px-3 py-2 bg-red-100 hover:bg-red-200 rounded-lg flex items-center justify-center transition" data-idchildren="${child.idchildren}">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18"
                             fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M19 6v14a2 2
                            0 0 1-2 2H7a2 2 0 0 1-2-2V6M3 6h18M8 6V4a2 2
                            0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                        </svg>
                    </button>
                </td>
            `;
            tableBody2.appendChild(row);
        });
        // Add event listeners after rendering
        tableBody2.querySelectorAll(".edit-button").forEach(btn => {
            btn.addEventListener("click", (e) => {
                const id = e.currentTarget.dataset.idchildren;
                handleEditChild(id);
            });
        });

        tableBody2.querySelectorAll(".delete-button").forEach(btn => {
            btn.addEventListener("click", (e) => {
                const id = e.currentTarget.dataset.idchildren;
                console.log("Delete clicked for idchildren:", idchildren);
                // Call your custom delete function
                handleDeleteChild(id);
            });
        });

        // Example custom functions
        async function handleEditChild(id) {
            try {
                // Open modal first
                const modal = document.getElementById("profileModal");
                modal.classList.remove("hidden");
                editingChildRecord = id
                // Fetch data from FastAPI endpoint
                const response = await fetch(`${window.API_BASE_URL}/campaign/campaign/get/childata/${id}`);
                const result = await response.json();

                if (result.status !== "success") {
                    console.error("Failed to fetch child data:", result.message);
                    return;
                }

                const data = result.data;

                // Populate form fields
                document.getElementById("dayname").value = data.day ?? "";
                document.getElementById("housenumber").value = data.house ?? "";
                document.getElementById("childname").value = data.name ?? "";
                document.getElementById("fathername").value = data.father ?? "";
                document.getElementById("gender").value = data.gender; // adjust according to your DB
                document.getElementById("age").value = data.age ?? "";
                document.getElementById("missingRounds").value = data.nofmc ?? "";
                document.getElementById("address").value = data.address ?? "";
                document.getElementById("missedReason").value = data.nodose ?? "";
                document.getElementById("subReason").value = data.reject ?? ""; // if you have mapping
                document.getElementById("location").value = data.location ?? "";
                document.getElementById("hrmp").value = data.hrmp;
                if (data.returndate) {
                    const parts = data.returndate.split('-'); // ["yyyy","mm","dd"]
                    if (parts.length === 3) {
                        document.getElementById("date").value = `${parts[2]}-${parts[1]}-${parts[0]}`;
                    } else {
                        document.getElementById("date").value = data.returndate; // fallback
                    }
                } else {
                    document.getElementById("date").value = "";
                }

                console.log("Modal form populated with child data:", data);

            } catch (error) {
                console.error("Error fetching child data:", error);
            }

        }

        function handleDeleteChild(id) {
            console.log("Custom delete logic for:", id);
        }


    }


    async function submitChildData(payload, editChildRecord = null) {
        try {
            let url = "";
            let method = "";

            if (editChildRecord) {
                // Editing an existing child → use PUT
                url = `${window.API_BASE_URL}/campaign/update/${editChildRecord}`;
                method = "PUT";
                delete payload.idheader;
                delete payload.idteam;

            } else {
                // Creating a new child → use POST
                url = `${window.API_BASE_URL}/campaign/campaign/add/childata`;
                method = "POST";
            }

            // Hit the API
            const response = await fetch(url, {
                method: method,
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            if (!response.ok) {
            Swal.fire({
                    icon: 'error',
                    title: 'Error!',
                    text: data.message || "Failed to submit child data",
                    timer: 2000,
                    timerProgressBar: true,
                    showConfirmButton: false,
                });
                console.error("Error submitting child data:", data);
                return;
            }

            Swal.fire({
                icon: 'success',
                title: 'Success!',
                text: data.message || "Child data proceed successfully",
                timer: 2000,
                timerProgressBar: true,
                showConfirmButton: false,
            });
            document.getElementById("locationContainer").classList.add("hidden");
            return data;
        } catch (err) {
            Swal.fire({
                icon: 'error',
                title: 'Unexpected Error!',
                text: "Something went wrong",
                timer: 2000,
                timerProgressBar: true,
                showConfirmButton: false,
            });
        }
    }


    const setoptions = document.getElementById("setoptions");
    setoptions.addEventListener("change", () => {
        const selectedValue = setoptions.value;
        if (!selectedValue) return; // nothing selected

        let [aicid, teamid] = selectedValue.split(",").map(v => v.trim());
        if (!aicid || !teamid) return;

        fetchChildData(parseInt(aicid, 10), parseInt(teamid, 10));
    });

    form.addEventListener("submit", async (e) => {
        e.preventDefault(); // ✅ Prevent page reload

        try {
            // Grab AIC + Team from dropdown
            const selectedValue = document.getElementById("setoptions").value;
            let aicid = null, teamid = null;
            if (selectedValue) {
                [aicid, teamid] = selectedValue.split(",").map(v => v.trim());
            }
            let dateValue = document.getElementById("date").value; // e.g. "08-08-2025"

            let returndate = null;

            if (dateValue && dateValue.trim() !== "") {
                // split dd-mm-yyyy into parts
                let [day, month, year] = dateValue.split("-");
                // rearrange into yyyy-mm-dd
                returndate = `${year}-${month}-${day}`;
            }

            // Build payload
            const payload = {
                idheader: parseInt(aicid, 10),
                idteam: parseInt(teamid, 10),
                day: parseInt(document.getElementById("dayname").value, 10),
                house: document.getElementById("housenumber").value.trim().toUpperCase(),
                name: document.getElementById("childname").value.trim().toUpperCase(),
                father: document.getElementById("fathername").value.trim().toUpperCase(),
                gender: document.getElementById("gender").value.trim(),
                age: parseInt(document.getElementById("age").value, 10),
                address: document.getElementById("address").value.trim().toUpperCase(),
                nofmc: parseInt(document.getElementById("missingRounds").value, 10),
                reasontype: "1", // default hidden
                nodose: document.getElementById("missedReason").value.trim(),
                reject: document.getElementById("subReason").value.trim(),
                location: document.getElementById("location").value.trim().toUpperCase() || null,
                hrmp: document.getElementById("hrmp").value.trim(),
                returndate: returndate,
                dateofvacc: null,
                idusers: window.user_info?.idusers || 10
            };
            await submitChildData(payload, editingChildRecord || null);
            fetchChildData(parseInt(aicid, 10), parseInt(teamid, 10));
            form.reset();
            editingChildRecord = null;

        } catch (error) {
            console.error("Error submitting form:", error);
            Swal.fire({
                icon: "error",
                title: "Oops!",
                text: error.message || "Something went wrong",
            showConfirmButton: false,
                confirmButtonColor: "#3085d6",
                timer: 1500,          // Auto close after 1500ms
                timerProgressBar: true

            });
        }
    });
});
        const pagination = setupTablePagination({
    tableBody: document.getElementById("tableBody2"),
    searchInput: document.getElementById("tableSearch2"),
    prevBtn: document.getElementById("prevPage2"),
    nextBtn: document.getElementById("nextPage2"),
    pageInfo: document.getElementById("pageInfo2"),
    rowsPerPage: 5 // any number you want
});

    // If you fetch new rows dynamically later, just call:
    pagination.resetPagination();
</script>
<script>

document.getElementById("openModalBtn").addEventListener("click", (e) => {
    e.preventDefault(); // prevent default form submission
    document.getElementById("update_user_profile").reset(); // reset the form
    editingChildRecord=null;
});

</script>

<script>
document.addEventListener("DOMContentLoaded", function () {
    // Initialize validation states
    window.validationStates = {
        fathername: false,
        childname: false,
    };

    // Toggle submit button
    function toggleSubmitButtonedit() {
        const btn = document.getElementById('submitchildata');
        if (!btn) return;

        const allValid = Object.values(window.validationStates).every(v => v === true);

        if (allValid) {
            btn.disabled = false;
            btn.style.removeProperty('background-color');
            btn.style.removeProperty('background-image');
            btn.style.removeProperty('border-color');
            btn.style.removeProperty('cursor');
        } else {
            btn.disabled = true;
            btn.style.setProperty('background-color', 'gray', 'important');
            btn.style.setProperty('background-image', 'none', 'important');
            btn.style.setProperty('border-color', 'gray', 'important');
            btn.style.setProperty('cursor', 'not-allowed', 'important');
        }
    }

    // Strict name validation
    function validateName(input, fieldKey, fieldDisplayName) {
        const value = input.value;

        const minLength = 3;
        const maxLength = 50;
        const onlyLettersSpaces = /^[A-Za-z ]+$/;
        const repeatedWords = /\b(\w+)\s+\1\b/i; // 2 repeated words
        const tripleRepeatedWords = /\b(\w+)\s+\1\s+\1\b/i; // 3 repeated words
        const doubleSpaces = /\s{2,}/;
        const tripleLetters = /(.)\1\1/;
        const hasNumbers = /\d/;
        const singleLetterWord = /\b\w\b/;

        let error = "";

        if (!value.trim()) {
            error = `${fieldDisplayName} is required.`;
        } else if (value !== value.trim()) {
            error = `${fieldDisplayName} cannot have spaces at the start or end.`;
        } else if (value.length < minLength) {
            error = `${fieldDisplayName} must be at least ${minLength} characters.`;
        } else if (value.length > maxLength) {
            error = `${fieldDisplayName} cannot exceed ${maxLength} characters.`;
        } else if (!onlyLettersSpaces.test(value)) {
            error = `${fieldDisplayName} can only contain letters and spaces.`;
        } else if (doubleSpaces.test(value)) {
            error = `${fieldDisplayName} cannot contain consecutive spaces.`;
        } else if (repeatedWords.test(value)) {
            error = `${fieldDisplayName} cannot contain repeated words.`;
        } else if (tripleRepeatedWords.test(value)) {
            error = `${fieldDisplayName} cannot contain three identical words in sequence.`;
        } else if (tripleLetters.test(value)) {
            error = `${fieldDisplayName} cannot contain the same letter three times in a row.`;
        } else if (hasNumbers.test(value)) {
            error = `${fieldDisplayName} cannot contain numbers.`;
        } else if (singleLetterWord.test(value)) {
            error = `${fieldDisplayName} cannot contain single-letter words.`;
        }

        if (error) {
            input.classList.remove("border-gray-300");
            input.classList.add("border-red-500", "focus:ring-red-300");

            setTimeout(() => {
                input.classList.remove("border-red-500", "focus:ring-red-300");
                input.classList.add("border-gray-300");
            }, 3000);

            toastr.error(error, "Validation Error");
            window.validationStates[fieldKey] = false;
        } else {
            window.validationStates[fieldKey] = true;
        }

        toggleSubmitButtonedit();
    }

    // Inputs
    const fatherInput = document.getElementById("fathername");
    const childInput = document.getElementById("childname");

    // Event listeners
    fatherInput.addEventListener("blur", () => validateName(fatherInput, "fathername", "Father Name"));
    childInput.addEventListener("blur", () => validateName(childInput, "childname", "Child Name"));

    // Toastr options
    toastr.options = {
        "closeButton": true,
        "progressBar": true,
        "timeOut": "3000",
        "extendedTimeOut": "1000",
        "positionClass": "toast-top-right"
    };

    // Initialize button state
    toggleSubmitButtonedit();
});
</script>