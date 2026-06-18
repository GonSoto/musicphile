from dotenv import load_dotenv
import os
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import redirect, render_template, session
from functools import wraps

load_dotenv()

def get_spotify_client():
    client_id = os.environ.get("CLIENT_ID")
    client_secret = os.environ.get("CLIENT_SECRET")
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="http://127.0.0.1:5000/callback",
        scope="user-library-read user-top-read user-follow-read user-read-recently-played",
        cache_handler=spotipy.cache_handler.FlaskSessionCacheHandler(session)
    )

    token = auth_manager.get_cached_token()

    if not token:
        return None

    if auth_manager.is_token_expired(token):
        try:
            auth_manager.refresh_access_token(token["refresh_token"])
        except Exception as e:
            if "invalid_grant" in str(e):
                session.pop("token_info", None)
                return None
            raise
    
    if not auth_manager.validate_token(auth_manager.get_cached_token()):
        return None  # user hasn't connected Spotify yet
    
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