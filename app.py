from flask import Flask, request, redirect, send_from_directory
import psycopg2
import os

app = Flask(__name__)

BASE_DIR = r"C:\Users\adity\iCloudDrive\Documents\advanced"

DATABASE_URL = "postgresql://neondb_owner:npg_v5UnzHmfSRj1@ep-falling-hat-aep2j8gp-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require"

try:
    connection = psycopg2.connect(DATABASE_URL)
    connection.autocommit = True
    print("✅ Connected to Neon PostgreSQL")
except Exception as e:
    print("❌ Database connection failed:", e)
    connection = None


@app.route("/", methods=["GET"])
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/login", methods=["POST"])
def login():
    student_id = request.form.get("username")
    password = request.form.get("password")

    if not connection:
        return "<h3 style='color:red;text-align:center;'>Database connection unavailable!</h3>"

    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE id = %s AND password = %s",
        (student_id, password)
    )
    user = cursor.fetchone()
    cursor.close()

    if user:
        return redirect("/mainpage")
    else:
        return "<h3 style='color:red;text-align:center;'>Invalid ID or Password!</h3>"


@app.route("/mainpage", methods=["GET"])
def mainpage():
    return send_from_directory(BASE_DIR, "mainpage.html")


@app.route("/register", methods=["GET"])
def register_page():
    return send_from_directory(BASE_DIR, "register.html")


@app.route("/register", methods=["POST"])
def register_user():
    student_id = request.form.get("username")
    password = request.form.get("password")

    if not connection:
        return "<h3 style='color:red;text-align:center;'>Database connection unavailable!</h3>"

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users WHERE id = %s", (student_id,))
    existing = cursor.fetchone()

    if existing:
        cursor.close()
        return "<h3 style='color:red;text-align:center;'>User already exists!</h3>"

    cursor.execute(
        "INSERT INTO users (id, password) VALUES (%s, %s)",
        (student_id, password)
    )
    connection.commit()
    cursor.close()

    return "<h3 style='color:green;text-align:center;'>✅ Account created successfully! <a href='/'>Login here</a></h3>"


@app.route("/<path:path>", methods=["GET"])
def static_files(path):
    return send_from_directory(BASE_DIR, path)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
