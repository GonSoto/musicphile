from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session
from helpers import login_required, get_spotify_client, DBCacheHandler
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
        cache_handler=DBCacheHandler(session["user_id"]),
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
        cache_handler=DBCacheHandler(session["user_id"]),
        show_dialog=True
    )
    return redirect(auth_manager.get_authorize_url())

@app.route("/profile")
@login_required
def profile():
    sp = get_spotify_client()
    if sp is None:
        return redirect("/spotify-login")
    
    time_range = request.args.get("time_range", "short_term")
    if time_range not in ("short_term", "medium_term", "long_term"):
        time_range = "short_term"

    top_artists_result = sp.current_user_top_artists(limit=10, time_range=time_range)
    top_artists = top_artists_result["items"]

    top_tracks_result = sp.current_user_top_tracks(limit=10, time_range=time_range)
    top_tracks = top_tracks_result["items"]

    recent_result = sp.current_user_recently_played(limit=5)
    recent_tracks = recent_result["items"]
    
    import requests as http_requests
    from collections import Counter

    lastfm_api_key = os.environ.get("LASTFM_API_KEY")
    all_genres = []

    for artist in top_artists:
        try:
            response = http_requests.get("https://ws.audioscrobbler.com/2.0/", params={
                "method": "artist.getTopTags",
                "artist": artist["name"],
                "api_key": lastfm_api_key,
                "format": "json",
                "limit": 5
            })
            data = response.json()
            tags = data.get("toptags", {}).get("tag", [])
            for tag in tags:
                all_genres.append(tag["name"].lower())
        except Exception:
            continue

        genre_counts = Counter(all_genres) 

        top_tag_counts = genre_counts.most_common(10)
        top_total = sum(count for _, count in top_tag_counts) # Takes each count of the main genres and sums them together
        top_genres = [
            {"name": genre, "percentage": round((count / top_total) * 100, 1)}
            for genre, count in top_tag_counts
        ] if top_total > 0 else []

    conn = sqlite3.connect("musicphile.db")
    c = conn.cursor()
    rows = c.execute("SELECT id, position, title, artist, cover_url FROM top_albums WHERE user_id = ? ORDER BY position", (session["user_id"],)).fetchall()
    conn.close()
    top_albums = [{"id": r[0], "position": r[1], "title": r[2], "artist": r[3], "cover_url": r[4]} for r in rows]

    return render_template(
        "profile.html",
        top_artists=top_artists, top_tracks=top_tracks, top_genres=top_genres, recent_tracks=recent_tracks, top_albums=top_albums, time_range=time_range)

@app.route("/search-albums")
@login_required
def search_albums():
    query = request.args.get("q", "").strip()
    if not query:
        return {"results": []}
    
    lastfm_api_key = os.environ.get("LASTFM_API_KEY")
    import requests as http_requests
    response = http_requests.get("https://ws.audioscrobbler.com/2.0/", params={
        "method": "album.search",
        "album": query,
        "api_key": lastfm_api_key,
        "format": "json",
        "limit": 8})
    data = response.json()
    albums_raw = data.get("results", {}).get("albummatches", {}).get("album", [])   # .get is used instead of brackets (results["..."]["..."]) to avoid KeyError if the keys don't exist
                                                                                    # also, {} and [] are used as default fallbacks if the servers are down or there is any other problem
    results = []
    for album in albums_raw:
        images = album.get("image", [])
        cover = next((img["#text"] for img in reversed(images) if img["#text"]), None)  # Loops through all the images, from best to worst quality, until it finds one that exists
        results.append({
            "title": album.get("name"),
            "artist": album.get("artist"),
            "cover_url": cover,
            "mbid": album.get("mbid", "")
        })
    return {"results": results}

@app.route("/top-albums/add", methods=["POST"])
@login_required
def add_top_album():
    user_id = session["user_id"]
    data = request.get_json()

    conn = sqlite3.connect("musicphile.db")
    c = conn.cursor()
    count = c.execute(
        "SELECT COUNT(*) FROM top_albums WHERE user_id = ?", (user_id,)
    ).fetchone()[0]
    if count >= 5:
        conn.close()
        return {"error": "You already have 5 albums. Remove one first."}, 400

    next_position = count + 1
    c.execute(
        "INSERT INTO top_albums (user_id, position, title, artist, cover_url, mbid) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, next_position, data["title"], data["artist"], data.get("cover_url"), data.get("mbid", ""))
    )
    conn.commit()
    new_id = c.lastrowid
    conn.close()
    return {"success": True, "id": new_id}

@app.route("/top-albums/remove", methods=["POST"])
@login_required
def remove_top_album():
    user_id = session["user_id"]
    data = request.get_json()
    album_id = data["id"]

    conn = sqlite3.connect("musicphile.db")
    c = conn.cursor()

    row = c.execute(
        "SELECT position FROM top_albums WHERE id = ? AND user_id = ?", (album_id, user_id)
    ).fetchone()

    if not row:
        conn.close()
        return {"error": "Album not found"}, 404

    removed_position = row[0]

    c.execute("DELETE FROM top_albums WHERE id = ? AND user_id = ?", (album_id, user_id))

    c.execute("UPDATE top_albums SET position = position - 1 WHERE user_id = ? AND position > ?", (user_id, removed_position))

    conn.commit()
    conn.close()
    return {"success": True}

@app.route("/top-albums/reorder", methods=["POST"])
@login_required
def reorder_top_album():
    user_id = session["user_id"]
    data = request.get_json()
    album_id = data["id"]
    direction = data["direction"]

    conn = sqlite3.connect("musicphile.db")
    c = conn.cursor()

    current = c.execute(
        "SELECT id, position FROM top_albums WHERE id = ? AND user_id = ?", (album_id, user_id)
    ).fetchone()

    if not current:
        conn.close()
        return {"error": "Album not found"}, 404

    current_pos = current[1]
    swap_pos = current_pos - 1 if direction == "up" else current_pos + 1

    swap_album = c.execute(
        "SELECT id FROM top_albums WHERE user_id = ? AND position = ?", (user_id, swap_pos)
    ).fetchone()

    if not swap_album:
        conn.close()
        return {"error": "Can't move further"}, 400

    c.execute("UPDATE top_albums SET position = ? WHERE id = ?", (swap_pos, album_id))
    c.execute("UPDATE top_albums SET position = ? WHERE id = ?", (current_pos, swap_album[0]))

    conn.commit()
    conn.close()
    return {"success": True}