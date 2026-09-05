from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

DATABASE = "skilltrack.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def add_column_if_missing(conn, table, column, definition):
    columns = conn.execute(f"PRAGMA table_info({table})").fetchall()
    existing = [row["name"] for row in columns]

    if column not in existing:
        conn.execute(
            f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
        )


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS trainees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trainee_id TEXT UNIQUE,
            name TEXT,
            phone TEXT,
            district TEXT,
            course TEXT,
            training_completed TEXT,
            certificate_status TEXT,
            employment TEXT,
            company TEXT,
            job_role TEXT,
            salary REAL,
            skills TEXT
        )
    """)

    # Add missing columns if an older database already exists
    add_column_if_missing(conn, "trainees", "phone", "TEXT")
    add_column_if_missing(conn, "trainees", "training_completed", "TEXT")
    add_column_if_missing(conn, "trainees", "certificate_status", "TEXT")
    add_column_if_missing(conn, "trainees", "company", "TEXT")
    add_column_if_missing(conn, "trainees", "job_role", "TEXT")
    add_column_if_missing(conn, "trainees", "salary", "REAL")
    add_column_if_missing(conn, "trainees", "skills", "TEXT")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS followups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trainee_id TEXT,
            followup_period TEXT,
            employment TEXT,
            company TEXT,
            current_job_role TEXT,
            current_salary REAL,
            consent TEXT
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")


# ---------------- TRAINEES ----------------

@app.route("/api/trainees", methods=["GET"])
def get_trainees():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM trainees ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])


@app.route("/api/trainees", methods=["POST"])
def add_trainee():
    data = request.get_json()

    trainee_id = data.get("trainee_id", "").strip()
    name = data.get("name", "").strip()

    if not trainee_id or not name:
        return jsonify({"error": "Trainee ID and Name are required"}), 400

    conn = get_db()

    try:
        conn.execute("""
            INSERT INTO trainees
            (trainee_id, name, phone, district, course,
             training_completed, certificate_status, employment,
             company, job_role, salary, skills)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trainee_id,
            name,
            data.get("phone", ""),
            data.get("district", ""),
            data.get("course", ""),
            data.get("training_completed", data.get("training", "")),
            data.get("certificate_status", data.get("certificate", "")),
            data.get("employment", ""),
            data.get("company", ""),
            data.get("job_role", ""),
            data.get("salary", 0) or 0,
            data.get("skills", "")
        ))

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Trainee added successfully"
        })

    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({
            "error": "Trainee ID already exists"
        }), 400


# ---------------- FOLLOW-UP ----------------

@app.route("/api/followup", methods=["POST"])
def add_followup():
    data = request.get_json()

    conn = get_db()

    conn.execute("""
        INSERT INTO followups
        (trainee_id, followup_period, employment,
         company, current_job_role, current_salary, consent)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("trainee_id", ""),
        data.get("followup_period", ""),
        data.get("employment", ""),
        data.get("company", ""),
        data.get("current_job_role", ""),
        data.get("current_salary", 0) or 0,
        data.get("consent", "")
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Follow-up submitted successfully"
    })


# ---------------- DASHBOARD ----------------

@app.route("/api/dashboard")
def dashboard():
    conn = get_db()

    total = conn.execute(
        "SELECT COUNT(*) FROM trainees"
    ).fetchone()[0]

    certified = conn.execute("""
        SELECT COUNT(*) FROM trainees
        WHERE LOWER(COALESCE(certificate_status, '')) = 'certified'
    """).fetchone()[0]

    employed = conn.execute("""
        SELECT COUNT(*) FROM trainees
        WHERE LOWER(COALESCE(employment, '')) = 'employed'
    """).fetchone()[0]

    unemployed = total - employed

    employment_rate = round(
        (employed / total) * 100, 2
    ) if total else 0

    conn.close()

    return jsonify({
        "total": total,
        "certified": certified,
        "employed": employed,
        "unemployed": unemployed,
        "employment_rate": employment_rate
    })


# ---------------- SKILL GAP ----------------

@app.route("/api/skill-gaps")
def skill_gaps():

    conn = get_db()

    rows = conn.execute(
        "SELECT skills FROM trainees"
    ).fetchall()

    conn.close()

    skill_counts = {}

    for row in rows:
        skills = row["skills"]

        if not skills:
            continue

        for skill in skills.split(","):
            skill = skill.strip()

            if skill:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1

    result = []

    for skill, count in sorted(
        skill_counts.items(),
        key=lambda x: x[1],
        reverse=True
    ):
        result.append({
            "skill": skill,
            "count": count
        })

    return jsonify(result)

init_db()
if __name__ == "__main__":
    app.run(debug=True)


