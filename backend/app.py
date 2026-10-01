import os
import pymysql
from flask import Flask, jsonify, request

app = Flask(__name__)

def get_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "mariadb"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "appuser"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "employee_db"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )

def query(sql, args=None, fetch=True):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args or ())
            return cur.fetchall() if fetch else cur.lastrowid
    finally:
        conn.close()

@app.get("/health")
def health():
    return jsonify(status="ok")          # liveness: process is up

@app.get("/ready")
def ready():
    try:                                  # readiness: database reachable
        query("SELECT 1")
        return jsonify(status="ready")
    except Exception as e:
        return jsonify(status="not ready", error=str(e)), 503

@app.get("/api/employees")
def list_employees():
    return jsonify(query("SELECT * FROM employees ORDER BY id"))

@app.post("/api/employees")
def add_employee():
    d = request.get_json(force=True)
    if not d.get("name") or not d.get("email"):
        return jsonify(error="name and email are required"), 400
    new_id = query(
        "INSERT INTO employees (name, email, department) VALUES (%s,%s,%s)",
        (d["name"], d["email"], d.get("department")), fetch=False)
    return jsonify(id=new_id), 201

@app.get("/api/tasks")
def list_tasks():
    return jsonify(query(
        "SELECT t.id, t.task_name, t.status, t.employee_id, e.name AS employee_name "
        "FROM tasks t LEFT JOIN employees e ON e.id = t.employee_id ORDER BY t.id"))

@app.post("/api/tasks")
def add_task():
    d = request.get_json(force=True)
    if not d.get("task_name"):
        return jsonify(error="task_name is required"), 400
    new_id = query(
        "INSERT INTO tasks (employee_id, task_name, status) VALUES (%s,%s,%s)",
        (d.get("employee_id"), d["task_name"], d.get("status", "Pending")), fetch=False)
    return jsonify(id=new_id), 201

@app.put("/api/tasks/<int:task_id>")
def update_task(task_id):
    d = request.get_json(force=True)
    if d.get("status") not in ("Pending", "In Progress", "Completed"):
        return jsonify(error="invalid status"), 400
    query("UPDATE tasks SET status=%s WHERE id=%s", (d["status"], task_id), fetch=False)
    return jsonify(updated=task_id)

@app.delete("/api/tasks/<int:task_id>")
def delete_task(task_id):
    query("DELETE FROM tasks WHERE id=%s", (task_id,), fetch=False)
    return jsonify(deleted=task_id)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
