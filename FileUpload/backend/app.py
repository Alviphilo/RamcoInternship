from flask import Flask, render_template, request, jsonify
import pyodbc
import mysql.connector #type:ignore
import psycopg2 #type:ignore
import json
import os
import re
from datetime import datetime
from typing import List, Dict, Any

app = Flask(__name__, template_folder="templates", static_folder="static")

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVERS_PATH = os.path.join(BASE_DIR, "servers.json")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
LOG_FILE = os.path.join(BASE_DIR, "deployments.log.json")
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Ensure directories and files exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if not os.path.exists(SERVERS_PATH):
    raise RuntimeError("Missing servers.json - place it next to app.py")

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        json.dump([], f, indent=2)

# Load server configurations
with open(SERVERS_PATH) as f:
    SERVERS = json.load(f)

# --- Helper Functions ---

def normalize_mysql_to_mssql(script: str) -> str:
    """Convert MySQL syntax to MSSQL compatible syntax"""
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
    """Split SQL script into batches (for MSSQL GO statements)"""
    script = script.replace('\r\n', '\n').replace('\r', '\n')
    parts = re.split(r'(?im)^\s*GO\s*$', script)
    return [p.strip() for p in parts if p.strip()]

def make_statements(script: str) -> List[str]:
    """Split SQL script into individual statements"""
    statements = [s.strip() for s in script.split(";") if s.strip()]
    return statements

# Security: Dangerous SQL patterns to block
DANGEROUS_KEYWORDS = [
    r'\bxp_cmdshell\b', r'\bsp_configure\b', r'\bSHUTDOWN\b',
    r'\bDROP\s+DATABASE\b', r'\bALTER\s+SERVER\b', r'\bDROP\s+SCHEMA\b',
    r'\bDROP\s+LOGIN\b', r'\bCREATE\s+LOGIN\b', r'\bALTER\s+LOGIN\b'
]

def scan_for_dangerous(script: str) -> List[str]:
    """Scan script for dangerous SQL patterns"""
    return [kw for kw in DANGEROUS_KEYWORDS if re.search(kw, script, flags=re.IGNORECASE)]

def append_log(entry: Dict[str, Any]):
    """Append deployment log entry"""
    try:
        with open(LOG_FILE, "r+") as f:
            data = json.load(f)
            data.append(entry)
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
    except Exception:
        # Fallback: append as new line if JSON parsing fails
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")

def validate_employee_id(employee_id: str) -> tuple[bool, str]:
    """Validate employee ID format"""
    if not employee_id or not employee_id.strip():
        return False, "Employee ID is required"
    
    employee_id = employee_id.strip()
    if len(employee_id) > 20:
        return False, "Employee ID too long (max 20 characters)"
    
    if not re.match(r'^\d+$', employee_id):
        return False, "Employee ID should contain only numbers"
    
    return True, ""

def validate_file(file) -> tuple[bool, str]:
    """Validate uploaded SQL file"""
    if not file or not file.filename:
        return False, "No file selected"
    
    if not file.filename.lower().endswith('.sql'):
        return False, "Only .sql files are allowed"
    
    # Check file size (approximate)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    if file_size > MAX_FILE_SIZE:
        return False, f"File too large (max {MAX_FILE_SIZE // (1024*1024)}MB)"
    
    if file_size == 0:
        return False, "File is empty"
    
    return True, ""

def execute_mssql(server_info: Dict[str, str], script: str, log_entry: Dict[str, Any]) -> Dict[str, Any]:
    """Execute SQL script on MSSQL Server"""
    host = server_info["host"]
    username = server_info["username"]
    password = server_info["password"]
    database = server_info.get("database")

    conn_parts = [
        "DRIVER={ODBC Driver 17 for SQL Server}",
        f"SERVER={host}",
        f"UID={username}",
        f"PWD={password}",
        "CONNECTION TIMEOUT=30"
    ]
    if database:
        conn_parts.append(f"DATABASE={database}")
    
    conn_str = ";".join(conn_parts)
    
    # Split into batches for MSSQL
    batches = make_batches(script)
    
    conn = pyodbc.connect(conn_str, autocommit=True)
    cursor = conn.cursor()
    
    try:
        for idx, batch in enumerate(batches, start=1):
            if not batch.strip():
                continue
                
            try:
                cursor.execute(batch)
                log_entry["batch_results"].append({
                    "batch": idx, 
                    "status": "success",
                    "rows_affected": cursor.rowcount if hasattr(cursor, 'rowcount') else 0
                })
            except pyodbc.Error as e:
                err_msg = str(e)
                # Handle duplicate key violations as warnings
                if "2627" in err_msg or "duplicate key" in err_msg.lower():
                    log_entry["batch_results"].append({
                        "batch": idx, 
                        "status": "warning", 
                        "error": "Duplicate key constraint - record skipped"
                    })
                    continue
                else:
                    log_entry["batch_results"].append({
                        "batch": idx, 
                        "status": "error", 
                        "error": err_msg[:200]  # Truncate long errors
                    })
                    raise
    finally:
        cursor.close()
        conn.close()
    
    return log_entry

def execute_mysql(server_info: Dict[str, str], script: str, log_entry: Dict[str, Any]) -> Dict[str, Any]:
    """Execute SQL script on MySQL Server"""
    conn = mysql.connector.connect(
        host=server_info["host"],
        user=server_info["username"],
        password=server_info["password"],
        database=server_info.get("database"),
        connection_timeout=30
    )
    cursor = conn.cursor()
    
    try:
        statements = make_statements(script)
        for idx, stmt in enumerate(statements, start=1):
            if not stmt.strip():
                continue
                
            try:
                cursor.execute(stmt)
                log_entry["batch_results"].append({
                    "batch": idx, 
                    "status": "success",
                    "rows_affected": cursor.rowcount
                })
            except mysql.connector.Error as e:
                err_msg = str(e)
                # Handle duplicate key violations
                if e.errno == 1062:  # Duplicate entry error
                    log_entry["batch_results"].append({
                        "batch": idx, 
                        "status": "warning", 
                        "error": "Duplicate key constraint - record skipped"
                    })
                    continue
                else:
                    log_entry["batch_results"].append({
                        "batch": idx, 
                        "status": "error", 
                        "error": err_msg[:200]
                    })
                    raise
        
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    
    return log_entry

def execute_postgres(server_info: Dict[str, str], script: str, log_entry: Dict[str, Any]) -> Dict[str, Any]:
    """Execute SQL script on PostgreSQL Server"""
    conn = psycopg2.connect(
        host=server_info["host"],
        user=server_info["username"],
        password=server_info["password"],
        dbname=server_info["database"],
        connect_timeout=30
    )
    cursor = conn.cursor()
    
    try:
        statements = make_statements(script)
        for idx, stmt in enumerate(statements, start=1):
            if not stmt.strip():
                continue
                
            try:
                cursor.execute(stmt)
                log_entry["batch_results"].append({
                    "batch": idx, 
                    "status": "success",
                    "rows_affected": cursor.rowcount
                })
            except psycopg2.Error as e:
                err_msg = str(e)
                # Handle duplicate key violations
                if "duplicate key" in err_msg.lower():
                    log_entry["batch_results"].append({
                        "batch": idx, 
                        "status": "warning", 
                        "error": "Duplicate key constraint - record skipped"
                    })
                    continue
                else:
                    log_entry["batch_results"].append({
                        "batch": idx, 
                        "status": "error", 
                        "error": err_msg[:200]
                    })
                    raise
        
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    
    return log_entry

# --- Routes ---

@app.route("/")
def home():
    """Render the main deployment form"""
    return render_template("index.html", servers=list(SERVERS.keys()))

@app.route("/deploy-sql", methods=["POST"])
def deploy_sql():
    """Handle SQL deployment request"""
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Get form data
    employee_id = request.form.get("employeeId", "").strip()
    server_key = request.form.get("serverKey", "").strip()
    file = request.files.get("sqlFile")

    # Initialize log entry
    log_entry = {
        "timestamp": timestamp,
        "employee_id": employee_id,
        "server_key": server_key,
        "filename": None,
        "status": "pending",
        "message": None,
        "error": None,
        "batch_results": [],
        "db_type": None
    }

    # --- Validation Phase ---
    
    # Validate employee ID
    is_valid, error_msg = validate_employee_id(employee_id)
    if not is_valid:
        log_entry.update({"status": "error", "message": error_msg})
        append_log(log_entry)
        return jsonify(log_entry), 400

    # Validate file
    is_valid, error_msg = validate_file(file)
    if not is_valid:
        log_entry.update({"status": "error", "message": error_msg})
        append_log(log_entry)
        return jsonify(log_entry), 400

    # Validate server selection
    if server_key not in SERVERS:
        log_entry.update({"status": "error", "message": "Invalid server environment selected"})
        append_log(log_entry)
        return jsonify(log_entry), 400

    # --- File Processing Phase ---
    
    try:
        # Save uploaded file with timestamp
        safe_filename = os.path.basename(file.filename)
        timestamp_prefix = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        upload_path = os.path.join(UPLOAD_FOLDER, f"{timestamp_prefix}_{safe_filename}")
        file.save(upload_path)
        log_entry["filename"] = safe_filename

        # Read script content
        with open(upload_path, "r", encoding="utf-8", errors="ignore") as fh:
            raw_script = fh.read().strip()

        if not raw_script:
            log_entry.update({"status": "error", "message": "SQL file is empty"})
            append_log(log_entry)
            return jsonify(log_entry), 400

        # Auto-detect and normalize MySQL syntax for MSSQL
        server_info = SERVERS[server_key]
        db_type = server_info.get("type", "mssql").lower()
        log_entry["db_type"] = db_type
        
        if db_type == "mssql" and ("`" in raw_script or "AUTO_INCREMENT" in raw_script.upper()):
            script = normalize_mysql_to_mssql(raw_script)
            log_entry["normalized"] = True
        else:
            script = raw_script

        # Security scan
        dangerous_patterns = scan_for_dangerous(script)
        if dangerous_patterns:
            log_entry.update({
                "status": "rejected", 
                "message": "Script contains potentially dangerous operations", 
                "error": f"Blocked patterns: {', '.join(dangerous_patterns)}"
            })
            append_log(log_entry)
            return jsonify(log_entry), 403

        # --- Database Execution Phase ---
        
        if db_type == "mssql":
            log_entry = execute_mssql(server_info, script, log_entry)
        elif db_type == "mysql":
            log_entry = execute_mysql(server_info, script, log_entry)
        elif db_type == "postgres":
            log_entry = execute_postgres(server_info, script, log_entry)
        else:
            log_entry.update({"status": "error", "message": f"Unsupported database type: {db_type}"})
            append_log(log_entry)
            return jsonify(log_entry), 400

        # --- Final Status Determination ---
        
        error_batches = [r for r in log_entry["batch_results"] if r["status"] == "error"]
        warning_batches = [r for r in log_entry["batch_results"] if r["status"] == "warning"]
        success_batches = [r for r in log_entry["batch_results"] if r["status"] == "success"]

        if error_batches:
            log_entry.update({
                "status": "error", 
                "message": f"Deployment failed - {len(error_batches)} batch(es) had errors"
            })
        elif warning_batches:
            log_entry.update({
                "status": "warning", 
                "message": f"Deployment completed with warnings - {len(warning_batches)} batch(es) had warnings, {len(success_batches)} succeeded"
            })
        else:
            total_rows = sum(r.get("rows_affected", 0) for r in success_batches)
            log_entry.update({
                "status": "success", 
                "message": f"Successfully deployed to {server_key} - {len(success_batches)} batch(es) executed, {total_rows} rows affected"
            })

        append_log(log_entry)
        return jsonify(log_entry)

    except Exception as ex:
        error_msg = str(ex)
        log_entry.update({
            "status": "error", 
            "message": "Deployment failed due to unexpected error", 
            "error": error_msg[:500]  # Truncate very long errors
        })
        append_log(log_entry)
        return jsonify(log_entry), 500

@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})

@app.route("/logs")
def view_logs():
    """View deployment logs (for debugging)"""
    try:
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
        # Return last 50 entries
        return jsonify({"logs": logs[-50:], "total": len(logs)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print(f"SQL Deployment Tool starting...")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Available servers: {', '.join(SERVERS.keys())}")
    print(f"Security patterns monitored: {len(DANGEROUS_KEYWORDS)}")
    app.run(host="0.0.0.0", port=5000, debug=True)