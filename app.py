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

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

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
        cache_handler=spotipy.cache_handler.FlaskSessionCacheHandler(session),
        show_dialog=True
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

    import requests
    from collections import Counter

    lastfm_api_key = os.environ.get("LASTFM_API_KEY")
    all_genres = []

    for artist in top_artists:
        try:
            response = requests.get("https://ws.audioscrobbler.com/2.0/", params={
                "method": "artist.getTopTags",
                "artist": artist["name"],
                "api_key": lastfm_api_key,
                "format": "json",
                "limit": 3  # top 3 tags per artist is enough
            })
            data = response.json()
            tags = data.get("toptags", {}).get("tag", [])
            for tag in tags:
                all_genres.append(tag["name"].lower())
        except Exception:
            continue  # if one artist fails, skip it and carry on

        genre_counts = Counter(all_genres)
        total = sum(genre_counts.values())
        top_genres = [
            {"name": genre, "percentage": round((count / total) * 100, 1)}
            for genre, count in genre_counts.most_common(5)
        ] if total > 0 else []
    return render_template("profile.html", top_artists=top_artists, top_tracks=top_tracks, top_genres=top_genres)
'''
Deprecated code for showing genres with spotipy, now using Last.fm API instead
    artist_ids = [artist["id"] for artist in top_artists]
    full_artists = sp.artists(artist_ids)["artists"] # Coge el perfil del artista en base al id

    all_genres = []
    for artist in full_artists:
        if artist.get("genres"): # Busca los géneros del artista según el id
            all_genres.extend(artist["genres"])
    from collections import Counter
    genre_counts = Counter(all_genres)
    total = sum(genre_counts.values())
    top_genres = [
        {"name": genre, "percentage": round((count / total) * 100, 1)}
        for genre, count in genre_counts.most_common(5)
    ] # Genera los porcentajes de los géneros más escuchados
'''