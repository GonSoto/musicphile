# Musicphile

#### Video Demo: [Musicphile | CS50x 2026 Final Project](https://www.youtube.com/watch?v=Yr3ZCOoy1xs)
#### Description:
Musicphile is a hub that recollects both your Spotify stats and your manually selected music tastes and preferences. It is thought as a beggining of an application that would let you show your music taste to the world, as well as find and interact with people with the same music taste as you.

Using the **[Official Spotify API](https://developer.spotify.com/documentation/web-api)**, alongside the **[LastFM API](https://www.last.fm/api)**, Musicphile lets you see your actual listening data (recently played and top tracks, artists and genres) and also lets you choose your favorite albums of all time, as well as your current favorite artist and song (which might defer from what your listening habits say). If this were to be a published app, these data points would allow, via a database search, for people to match with other users which share, for example, the same favorite song.

I came up with the idea for this app when I noticed that most of my friends don't have the same music taste as I do, and realize that I would love if an app existed that let you find people nearby to share festivals and concerts with, or maybe just chat about internal group lore or fan theories. 

## Project Overview
### How it works
The app is a Python, Flask, SQLite and Jinja mix that works alongside the aforementioned APIs. Right now it works as a single-user information hub, but it is thought as and prepared to be improved to a social network that revolves around music.

#### Login and Register
Any new user has to sign up to the app and create and account by choosing a name and password *(as in the CS50 Finance Project)*, when you log in for the first time, you have to also connect your account with the Spotify API, so that Musicphile can retrieve your listening information. When this is finished, you finally access the profile page. This pages look nearly identical, and store the information on a SQLite database. This database is explained further below.

#### Index
Index acts as the homepage of this app, and as a placeholder for future improvements it could improve. Right now it only houses the spotify api connection button and the log out button, but it could also house the search bar, relevant and trending profiles, music releases, etc.

#### Profile
This is the page where everything happens. in here, you can see your **recently played** songs, as well as your **top tracks, artists and genres** (genres are displayed with a cool percentage that lets you see how your music taste is divided), all of them retrieved with the Spotify API. Top tracks, artists and genres share 3 buttons in the top right part for the user to cycle between time periods to see how his music has looked like for the last 4 weeks, 6 months, or for the whole existence of his account (the Spotify one, not Musicphile's). 

In here you can also see a blank tile for a section called **top 5 albums**. This is the part where the user has to manually select their 5 favorite albums (*an option that spotify doesn't have :wink:*). Any music aficionado has strong opinions on the best albums they have listened to, and likes to share them with the world to make his magnificent taste known. **This is the place to do so**. The album information is retrieved from the LastFM API, so as to not use additional Spotify tokens. After you've selected 5 albums, you can reorder them any way you want, but you must remove one before choosing another, so you have to be selective with your preferences!

Finally (even though it was at the top of the page), you can find two placeholders to select your current favorite artist and song (it's all about favorites here). This is made because even though you might have a song you've listened to **a lot** during your lifetime, there might be a song that evokes strong emotions right now, be it by recent events, emotional state or moment in life. Both of these can be changed anytime.

This page also contains some Claude-generated JS to give the app a more clean-looking and user-friendly appearance and functionality. This is purely an aesthetic choice and the AI use 

#### Styles
The website features a clean, Spotify-like design all throughout. It uses similar colors and organized tiles resembling the feeling of their desktop and mobile apps. The album covers are fetched from the LastFM API.
The CSS for this project was a mix of my own work and the help of AI (Claude). I iterated over the colors, fonts and basic design of the elements (radius, shadows, glows, etc.) until I was satisfied with the results on a few elements and then prompted Claude to replicate the design for the rest of the webpage to avoid redundancy of work.


### Database Design
A total of 4 tables are involved in this app: `users`, `top_albums`, `top_artist` and `top_track`.

#### `users`
This table is the core of the project and stores every musicphile account. It contains:
- `id`: Auto-incrementing unique identifier for every account.
- `username`: Unique login name chosen when registering. 
- `hash`: Hashed password.
- `spotify_token`: Unique Spotify OAuth token, sotred in order to allow persistent sessions when logging in.

#### `top_albums`
Stores each user's manually curated Top 5 albums list. Any given user can have up to 5 rows on this table.
- `id`: Auto-incrementing unique identifier for every top 5.
- `user_id`: References `users.id` to connect each top 5 with its correct user.
- `position`: Ranking position for each album. These are stored contiguously and updated in every reorder or change.
- `title`: Album title from the LastFM API.
- `artist_name`: Artist name from the LastFM API.
- `cover_url`: URL to the album cover image fetched from the LastFM API. The link is stored to avoid multiple API calls.
- `mbid`: MusicBrainz id*

#### `top_artist`
Stores each user's single manually chosen favourite artist at the moment. Each user can only have one row in this table, enforced by a `UNIQUE` constraint on `user_id`.
- `id`: Auto-incrementing unique identifier for every top artist entry.
- `user_id`: References `users.id` to connect each pick with its correct user.
- `name`: Artist name from the LastFM API.
- `image_url`: URL to the artist image fetched from the LastFM API. The link is stored to avoid multiple API calls.
- `mbid`: MusicBrainz id*

#### `top_track`
Stores each user's single manually chosen favourite track at the moment. Each user can only have one row in this table, enforced by a `UNIQUE` constraint on `user_id`.
- `id`: Auto-incrementing unique identifier for every top track entry.
- `user_id`: References `users.id` to connect each pick with its correct user.
- `title`: Track title from the LastFM API.
- `artist`: Artist name from the LastFM API.
- `cover_url`: URL to the track cover image fetched from the LastFM API. The link is stored to avoid multiple API calls.
- `mbid`: MusicBrainz id*

*MusicBrainz is an open-source community project that strives to create a massive music database. The mbid on `top_albums`, `top_artist` and `top_track` exists in case a music taste comparison feature was added in the future (MBID is more reliable than title strings, especially if the app was expanded to support apple music or other similar services).

## Future Improvements
This app is currently single-user, and acts as a hub fore gathering listening data and storing preferences, but it has been thought of as a place to connect with people through music. For difficulty, time and monetary reasons, Musicphile isn't an online platform, but it could easily be made so, so **including a search feature** with filters, or a recommended section that tries to match you with people or community-created groups of similar music taste would be a wonderful addition.

Another feature that could be added would be a timestamp column for the `top_artist`, `top_track` and `top_albums` to **see how your music favorites evolve over time**.

Finally, I would also love if Musicphile had a **calendar of releases and concerts**, where you could go to if you wanted to see when your favorite artists are publishing new music or coming to your city.

## Acknowledgements - AI Use
As stated before, AI (and specifically Claude) has been used as a companion and teacher to help me over difficult funtions, API-specific syntax, JSON formatting and other fields in which I had little knowledge, as well as with the tedious work of stlying all of the many `divs` and `classes`. Claude also served as a debugger and trouble-shooter, in most of the many times the app didn't want to work. Nevertheless, the idea and bulk of the work is entirely my own, and the code is still of a level of difficulty which I can understand.

## How to run
### Requirements
- Python 3.10 or higher
- A [Spotify Developer](https://developer.spotify.com/dashboard) account with a registered app
- A [Last.fm API](https://www.last.fm/api/account/create) key

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/your-username/musicphile.git
cd musicphile
```
or download it.

**2. Create and activate a virtual environment**
```bash
python -m venv .venv
```
```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables**

Create a `.env` file in the root of the project with the following:
FLASK_SECRET_KEY=your_secret_key_here
CLIENT_ID=your_spotify_client_id
CLIENT_SECRET=your_spotify_client_secret
LASTFM_API_KEY=your_lastfm_api_key

Your Spotify `CLIENT_ID` and `CLIENT_SECRET` can be found in your app's settings on the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard). Make sure `http://127.0.0.1:5000/callback` is added as a Redirect URI in those same settings.

**5. Initialise the database**
```bash
python init_db.py
```

**6. Run the app**
```bash
flask run
```

The app will be available at `http://127.0.0.1:5000`.