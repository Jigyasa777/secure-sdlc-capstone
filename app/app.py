# app/app.py
from flask import (
    Flask, request, render_template, redirect, url_for, session, flash
)
import sqlite3
import os

# -------------------- Flask setup --------------------
app = Flask(__name__)
app.secret_key = "demo-secret-not-secure"  # <-- intentionally hardcoded (for demo)

# Stored feedback in memory (for stored XSS demo)
FEEDBACKS = []  # each item: {"user": "...", "msg": "..."}

# -------------------- Tiny SQLite DB -----------------
DB_PATH = os.path.join(os.path.dirname(__file__), "site.db")

def init_db():
    """Create a small users table and seed an insecure admin user."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    # plaintext, weak password on purpose
    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('admin', 'admin123')")
    conn.commit()
    conn.close()

# ----------------------- Routes ----------------------

@app.route("/")
def home():
    return render_template("home.html", title="Home")

@app.route("/echo", methods=["GET"])
def echo_page():
    # reflected XSS demo: template uses {{ echoed|safe }}
    echoed = request.args.get("msg")
    return render_template("echo.html", title="Echo", echoed=echoed)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")

        # ⚠️ INTENTIONALLY VULNERABLE: SQL injection via string concatenation
        # Try username:  ' OR '1'='1
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        query = f"SELECT id, username FROM users WHERE username = '{u}' AND password = '{p}'"
        try:
            row = c.execute(query).fetchone()
        finally:
            conn.close()

        if row:
            session["user"] = row[1]
            flash("Login successful (but SQLi made this too easy!)")
            return redirect(url_for("admin"))
        flash("Invalid credentials.")
    return render_template("login.html", title="Login")

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out.")
    return redirect(url_for("home"))

@app.route("/admin")
def admin():
    # very weak "protection" – demo only
    if not session.get("user"):
        flash("Please login first.")
        return redirect(url_for("login"))
    return render_template("admin.html", title="Dashboard", feedback_count=len(FEEDBACKS))

@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if request.method == "POST":
        user = session.get("user") or "anon"
        msg = request.form.get("msg", "")
        # stored XSS demo: no sanitization
        FEEDBACKS.append({"user": user, "msg": msg})
        flash("Thanks for your feedback!")
        return redirect(url_for("feedback"))
    return render_template("feedback.html", title="Feedback", items=FEEDBACKS)

# small info-leak route (optional talking point)
@app.route("/debug")
def debug():
    return f"Headers: {dict(request.headers)}"

# ----------------------- Boot ------------------------
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
