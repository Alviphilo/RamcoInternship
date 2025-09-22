from flask import Flask, render_template, request, jsonify
import pyodbc
import mysql.connector #type:ignore
import psycopg2 #type:ignore
import json
import os
import re
from datetime import datetime
from typing import List

app = Flask(__name__, template_folder="templates", static_folder="static")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SERVERS_PATH = os.path.join(BASE_DIR, "servers.json")
if not os.path.exists(SERVERS_PATH):
    raise RuntimeError("Missing servers.json - place it next to app.py")

with open(SERVERS_PATH) as f:
    SERVERS = json.load(f)

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

LOG_FILE = os.path.join(BASE_DIR, "deployments.log.json")
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        json.dump([], f, indent=2)

# --- Helpers ---
def normalize_mysql_to_mssql(script: str) -> str:
    s = script
    s = s.replace('`', '')
    s = re.sub(r'\bAUTO_INCREMENT\b', 'IDENTITY(1,1)', s, flags=re.IGNORECASE)
    s = re.sub(r'\bCURRENT_TIMESTAMP\b', 'GETDATE()', s, flags=re.IGNORECASE)
    s = re.sub(r'\bNOW\(\)', 'GETDATE()', s, flags=re.IGNORECASE)
    s = re.sub(r'ENGINE\s*=\s*\w+', '', s, flags=re.IGNORECASE)
    s = re.sub(r'DEFAULT CHARSET\s*=\s*\w+', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\bUNSIGNED\b', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\bINT\s*\(\s*\d+\s*\)', 'INT', s, flags=re.IGNORECASE)
    s = re.sub(r'\bTINYINT\s*\(\s*1\s*\)', 'BIT', s, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', s)

def make_batches(script: str) -> List[str]:
    script = script.replace('\r\n', '\n').replace('\r', '\n')
    parts = re.split(r'(?im)^\s*GO\s*$', script)
    return [p.strip() for p in parts if p.strip()]

DANGEROUS_KEYWORDS = [
    r'\bxp_cmdshell\b', r'\bsp_configure\b', r'\bSHUTDOWN\b',
    r'\bDROP\s+DATABASE\b', r'\bALTER\s+SERVER\b'
]

def scan_for_dangerous(script: str):
    return [kw for kw in DANGEROUS_KEYWORDS if re.search(kw, script, flags=re.IGNORECASE)]

def append_log(entry: dict):
    try:
        with open(LOG_FILE, "r+") as f:
            data = json.load(f)
            data.append(entry)
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
    except Exception:
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")

# --- Routes ---
@app.route("/")
def home():
    return render_template("index.html", servers=list(SERVERS.keys()))

@app.route("/deploy-sql", methods=["POST"])
def deploy_sql():
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    employee_id = request.form.get("employeeId", "").strip()
    server_key = request.form.get("serverKey", "").strip()
    file = request.files.get("sqlFile")

    log_entry = {
        "timestamp": timestamp,
        "employee_id": employee_id,
        "server_key": server_key,
        "filename": None,
        "status": "pending",
        "message": None,
        "error": None,
        "batch_results": []
    }

    # --- Basic validation ---
    if not employee_id:
        log_entry.update({"status": "error", "message": "Employee ID required"})
        append_log(log_entry)
        return jsonify(log_entry), 400

    if not file or not file.filename.lower().endswith(".sql"):
        log_entry.update({"status": "error", "message": "Please upload a .sql file"})
        append_log(log_entry)
        return jsonify(log_entry), 400

    if server_key not in SERVERS:
        log_entry.update({"status": "error", "message": "Invalid server selected"})
        append_log(log_entry)
        return jsonify(log_entry), 400

    # --- Save uploaded file ---
    safe_filename = os.path.basename(file.filename)
    upload_path = os.path.join(UPLOAD_FOLDER, f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{safe_filename}")
    file.save(upload_path)
    log_entry["filename"] = safe_filename

    # --- Read script ---
    with open(upload_path, "r", encoding="utf-8", errors="ignore") as fh:
        raw_script = fh.read()

    # --- Normalize if looks like MySQL targeting MSSQL ---
    if "`" in raw_script or "AUTO_INCREMENT" in raw_script.upper():
        script = normalize_mysql_to_mssql(raw_script)
    else:
        script = raw_script

    # --- Security scan ---
    dangerous = scan_for_dangerous(script)
    if dangerous:
        log_entry.update({"status": "rejected", "message": "Script contains forbidden operations", "error": dangerous})
        append_log(log_entry)
        return jsonify(log_entry), 403

    # --- Split batches (MSSQL) ---
    batches = make_batches(script)

    # --- Connection info ---
    server_info = SERVERS[server_key]
    db_type = server_info.get("type", "mssql").lower()
    log_entry["db_type"] = db_type

    try:
        if db_type == "mssql":
            host = server_info["host"]
            username = server_info["username"]
            password = server_info["password"]
            database = server_info.get("database")

            conn_parts = [
                "DRIVER={ODBC Driver 17 for SQL Server}",
                f"SERVER={host}",
                f"UID={username}",
                f"PWD={password}"
            ]
            if database:
                conn_parts.append(f"DATABASE={database}")
            conn_str = ";".join(conn_parts)

            conn = pyodbc.connect(conn_str, autocommit=True)
            cursor = conn.cursor()

            for idx, batch in enumerate(batches, start=1):
                try:
                    cursor.execute(batch.strip())
                    log_entry["batch_results"].append({"batch": idx, "status": "success"})
                except pyodbc.Error as e:
                    err_msg = str(e)
                    if "2627" in err_msg:  # duplicate key violation
                        log_entry["batch_results"].append({"batch": idx, "status": "warning", "error": "Duplicate key skipped"})
                        continue
                    else:
                        log_entry["batch_results"].append({"batch": idx, "status": "error", "error": err_msg})
                        raise
            cursor.close()
            conn.close()

        elif db_type == "mysql":
            conn = mysql.connector.connect(
                host=server_info["host"],
                user=server_info["username"],
                password=server_info["password"],
                database=server_info.get("database")
            )
            cursor = conn.cursor()
            statements = [s.strip() for s in script.split(";") if s.strip()]
            for idx, stmt in enumerate(statements, start=1):
                try:
                    cursor.execute(stmt)
                    log_entry["batch_results"].append({"batch": idx, "status": "success"})
                except mysql.connector.Error as e:
                    err_msg = str(e)
                    if e.errno == 1062:  # duplicate key violation
                        log_entry["batch_results"].append({"batch": idx, "status": "warning", "error": "Duplicate key skipped"})
                        continue
                    else:
                        log_entry["batch_results"].append({"batch": idx, "status": "error", "error": err_msg})
                        raise
            conn.commit()
            cursor.close()
            conn.close()

        elif db_type == "postgres":
            conn = psycopg2.connect(
                host=server_info["host"],
                user=server_info["username"],
                password=server_info["password"],
                dbname=server_info["database"]
            )
            cursor = conn.cursor()
            statements = [s.strip() for s in script.split(";") if s.strip()]
            for idx, stmt in enumerate(statements, start=1):
                try:
                    cursor.execute(stmt)
                    log_entry["batch_results"].append({"batch": idx, "status": "success"})
                except psycopg2.Error as e:
                    err_msg = str(e)
                    if "duplicate key" in err_msg.lower():
                        log_entry["batch_results"].append({"batch": idx, "status": "warning", "error": "Duplicate key skipped"})
                        continue
                    else:
                        log_entry["batch_results"].append({"batch": idx, "status": "error", "error": err_msg})
                        raise
            conn.commit()
            cursor.close()
            conn.close()

        # Final status
        if any(r["status"] == "error" for r in log_entry["batch_results"]):
            log_entry.update({"status": "error", "message": "One or more batches failed"})
        elif any(r["status"] == "warning" for r in log_entry["batch_results"]):
            log_entry.update({"status": "warning", "message": "Script executed with warnings"})
        else:
            log_entry.update({"status": "success", "message": f"Deployed to {server_key}"})

        append_log(log_entry)
        return jsonify(log_entry)

    except Exception as ex:
        err_msg = str(ex)
        log_entry.update({"status": "error", "message": "Unexpected error", "error": err_msg})
        append_log(log_entry)
        return jsonify(log_entry), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
