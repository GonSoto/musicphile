from dotenv import load_dotenv
import os
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import redirect, render_template, session
from functools import wraps
import sqlite3
import json

load_dotenv()

class DBCacheHandler(spotipy.cache_handler.CacheHandler):
    def __init__(self, user_id):
        self.user_id = user_id

    def get_cached_token(self):
        conn = sqlite3.connect("musicphile.db")
        c = conn.cursor()
        row = c.execute("SELECT spotify_token FROM users WHERE id = ?", (self.user_id,)).fetchone()
        conn.close()
        if row and row[0]:
            return json.loads(row[0])
        return None
    
    def save_token_to_cache(self, token_info):
        conn = sqlite3.connect("musicphile.db")
        c = conn.cursor()
        row = c.execute("UPDATE TABLE users SET spotify_token = ? WHERE id = ?", (json.dumps(token_info), self.user_id))
        conn.commit()
        conn.close()

def get_spotify_client():
    user_id = session.get("user_id")
    if not user_id:
        return None
    
    client_id = os.environ.get("CLIENT_ID")
    client_secret = os.environ.get("CLIENT_SECRET")

    cache_handler = DBCacheHandler(user_id)
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="http://127.0.0.1:5000/callback",
        scope="user-library-read user-top-read user-follow-read user-read-recently-played",
        cache_handler=cache_handler
    )

    token = cache_handler.get_cached_token()
    if not token:
        return None

    if auth_manager.is_token_expired(token):
        try:
            auth_manager.refresh_access_token(token["refresh_token"])
        except Exception as e:
            if "invalid_grant" in str(e):
                cache_handler.save_token_to_cache(None)
                return None
            raise

    return spotipy.Spotify(auth_manager=auth_manager)

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function