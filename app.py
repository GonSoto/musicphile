from flask import Flask, redirect, render_template, request, session
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sqlite3
import os
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
from helpers import login_required
load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY")

@app.route("/")
@login_required
def index():
    return render_template("index.html", user=session["user_id"])

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        user = request.form.get("username")
        password = request.form.get("password")
        if not user:
            return render_template("login.html", error="must provide username")
        elif not password:
            return render_template("login.html", error="must provide password")
        else:
            conn = sqlite3.connect("musicphile.db")
            c = conn.cursor()
            info = c.execute("SELECT * FROM users WHERE username = ?", (user,))
            rows = info.fetchone()
            if rows == None or not check_password_hash(rows[2], password):
                return render_template("login.html", error="invalid username and/or password", user=user, password=password)
            else:
                session["user_id"] = rows[0]
                return redirect("/")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        user = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirm-password")
        if not user:
            return render_template("register.html", error="must provide username")
        elif not password:
            return render_template("register.html", error="must provide password")
        elif not confirmation:
            return render_template("register.html", error="must confirm password")
        elif password != confirmation:
            return render_template("register.html", error="passwords do not match")
        else:
            hash = generate_password_hash(password)
            conn = sqlite3.connect("musicphile.db")
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (user, hash))
                conn.commit()
                return render_template("login.html", success="account created successfully, please log in")
            except sqlite3.IntegrityError:
                conn.close()
                return render_template("register.html", error="username already exists")
            return redirect("/login")