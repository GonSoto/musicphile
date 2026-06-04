from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session
from helpers import login_required, get_spotify_client
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY")
client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri="http://localhost:5000/", scope="user-library-read user-top-read user-follow-read user-read-recently-played"))
@app.route("/")
@login_required
def index():
    return render_template("index.html", user=session["user_id"])

@app.route("/callback")
@login_required
def callback():
    auth_manager = SpotifyOAuth(
        client_id = client_id,
        client_secret = client_secret,
        redirect_uri = "http://127.0.0.1:5000/callback",
        scope = "user-library-read user-top-read user-follow-read user-read-recently-played",
        cache_handler=spotipy.cache_handler.FlaskSessionCacheHandler(session)
    )

    code = request.args.get("code")
    auth_manager.get_access_token(code)
    return redirect("/profile")

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

@app.route("/spotify-login")
@login_required
def connect_spotify():
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="http://127.0.0.1:5000/callback",
        scope="user-library-read user-top-read user-follow-read user-read-recently-played",
        cache_handler=spotipy.cache_handler.FlaskSessionCacheHandler(session)
    )
    auth_url = auth_manager.get_authorize_url()
    return redirect(auth_url)

@app.route("/profile")
@login_required
def profile():
    sp = get_spotify_client()
    if sp is None:
        return redirect("/spotify-login")
    top_artists_result = sp.current_user_top_artists(limit=10, time_range="medium_term")
    top_artists = top_artists_result["items"]

    top_tracks_result = sp.current_user_top_tracks(limit=10, time_range="medium_term")
    top_tracks = top_tracks_result["items"]

    return render_template("profile.html", top_artists=top_artists, top_tracks=top_tracks)