import sqlite3

conn = sqlite3.connect("musicphile.db")
c = conn.cursor()

c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        username TEXT NOT NULL UNIQUE,
        hash TEXT NOT NULL,
        spotify_token TEXT
    );
    CREATE TABLE IF NOT EXISTS top_albums (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        position INTEGER NOT NULL,
        title TEXT NOT NULL,
        artist TEXT NOT NULL,
        cover_url TEXT,
        mbid TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS top_artist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        name TEXT NOT NULL,
        image_url TEXT,
        mbid TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS top_track (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        title TEXT NOT NULL,
        artist TEXT NOT NULL,
        cover_url TEXT,
        mbid TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
""")

conn.commit()
conn.close()
print("Database initialised.")