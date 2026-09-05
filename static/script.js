// ================= PAGE NAVIGATION =================

function showPage(pageId) {

    const pages = document.querySelectorAll(".page");

    pages.forEach(page => {
        page.classList.add("hidden");
    });

    const selectedPage = document.getElementById(pageId);

    if (selectedPage) {
        selectedPage.classList.remove("hidden");
    }

    if (pageId === "dashboard") {
        loadDashboard();
    }
}


// ================= START =================

document.addEventListener("DOMContentLoaded", function () {

    loadDashboard();

    const traineeForm = document.getElementById("traineeForm");

    if (traineeForm) {
        traineeForm.addEventListener("submit", addTrainee);
    }

    const followupForm = document.getElementById("followupForm");

    if (followupForm) {
        followupForm.addEventListener("submit", submitFollowup);
    }
});


// ================= DASHBOARD =================

async function loadDashboard() {

    try {

        const response = await fetch("/api/dashboard");

        const data = await response.json();

        document.getElementById("totalTrainees").textContent =
            data.total;

        document.getElementById("certified").textContent =
            data.certified;

        document.getElementById("employed").textContent =
            data.employed;

        document.getElementById("unemployed").textContent =
            data.unemployed;

        document.getElementById("employmentRate").textContent =
            data.employment_rate + "%";

        loadTrainees();

    } catch (error) {

        console.error("Dashboard error:", error);
    }
}


// ================= TRAINEE TABLE =================

async function loadTrainees() {

    try {

        const response = await fetch("/api/trainees");

        const trainees = await response.json();

        const table =
            document.getElementById("traineeTableBody");

        table.innerHTML = "";

        trainees.forEach(trainee => {

            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${trainee.trainee_id || ""}</td>
                <td>${trainee.name || ""}</td>
                <td>${trainee.district || ""}</td>
                <td>${trainee.course || ""}</td>
                <td>${trainee.employment || ""}</td>
                <td>${trainee.company || ""}</td>
            `;

            table.appendChild(row);
        });

    } catch (error) {

        console.error("Trainee error:", error);
    }
}


// ================= ADD TRAINEE =================

async function addTrainee(event) {

    event.preventDefault();

    const form = event.target;

    const formData = new FormData(form);

    const data = Object.fromEntries(formData.entries());

    try {

        const response = await fetch("/api/trainees", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {

            alert(result.message);

            form.reset();

            showPage("dashboard");

        } else {

            alert(result.error);
        }

    } catch (error) {

        alert("Server connection error.");

        console.error(error);
    }
}


// ================= FOLLOW-UP =================

async function submitFollowup(event) {

    event.preventDefault();

    const form = event.target;

    const formData = new FormData(form);

    const data = Object.fromEntries(formData.entries());

    try {

        const response = await fetch("/api/followup", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {

            alert(result.message);

            form.reset();

        } else {

            alert(result.error);
        }

    } catch (error) {

        alert("Server connection error.");

        console.error(error);
    }
}


// ================= SKILL GAP =================

async function loadskillgaps() {

    const result =
        document.getElementById("skillGapResults");

    result.innerHTML =
        "<p>Loading skill gap data...</p>";

    try {

        const response =
            await fetch("/api/skill-gaps");

        const data = await response.json();

        if (!data || data.length === 0) {

            result.innerHTML =
                "<p>No skill data available.</p>";

            return;
        }

        result.innerHTML = "";

        data.forEach(item => {

            const card =
                document.createElement("div");

            card.className = "skill-card";

            card.innerHTML = `
                <h3>${item.skill}</h3>
                <p>
                    Trainees with this skill:
                    <strong>${item.count}</strong>
                </p>
            `;

            result.appendChild(card);
        });

    } catch (error) {

        console.error("Skill Gap error:", error);

        result.innerHTML =
            "<p>Unable to load skill gap data.</p>";
    }
}