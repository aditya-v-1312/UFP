from flask import Flask, request, redirect, send_from_directory
import psycopg2
import os

app = Flask(__name__)

# --- BASE DIR ---
# Uses the directory where app.py lives (Linux-friendly)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- ENVIRONMENT VARIABLES ---
# These should be set in Render dashboard
DATABASE_URL = os.environ.get("DATABASE_URL")
SECRET_KEY = os.environ.get("SECRET_KEY", "fallback_secret")

app.config['SECRET_KEY'] = SECRET_KEY


# --- DB CONNECTION FUNCTION ---
def get_connection():
    """
    Create a fresh connection to the Neon DB each time.
    Render keeps connections alive briefly, so this is safer
    than using one global connection.
    """
    return psycopg2.connect(DATABASE_URL, sslmode='require')


# --- ROUTES ---

@app.route("/", methods=["GET"])
def index():
    # Serve index.html from the same folder as app.py
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/login", methods=["POST"])
def login():
    student_id = request.form.get("username")
    password = request.form.get("password")

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM users WHERE id = %s AND password = %s",
                    (student_id, password)
                )
                user = cursor.fetchone()
    except Exception as e:
        return f"<h3 style='color:red;text-align:center;'>Database connection error: {e}</h3>"

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

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s", (student_id,))
                existing = cursor.fetchone()

                if existing:
                    return "<h3 style='color:red;text-align:center;'>User already exists!</h3>"

                cursor.execute(
                    "INSERT INTO users (id, password) VALUES (%s, %s)",
                    (student_id, password)
                )
                connection.commit()
    except Exception as e:
        return f"<h3 style='color:red;text-align:center;'>Database connection error: {e}</h3>"

    return "<h3 style='color:green;text-align:center;'>✅ Account created successfully! <a href='/'>Login here</a></h3>"


@app.route("/<path:path>", methods=["GET"])
def static_files(path):
    """
    Serves any file located in BASE_DIR.
    Example: /style.css will serve style.css from the repo root.
    """
    return send_from_directory(BASE_DIR, path)


@app.route("/db-test")
def db_test():
    """
    Quick route to check database connectivity.
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT NOW();")
                now = cur.fetchone()
        return f"✅ Database connected! Server time: {now}"
    except Exception as e:
        return f"❌ Database connection failed: {e}"


# --- MAIN ---
if __name__ == "__main__":
    # For local testing
    app.run(debug=True, host="0.0.0.0", port=5000)
