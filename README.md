# Musicphile

#### Video Demo: 
#### Description:
Musicphile is a hub that recollects both your Spotify stats and your manually selected music tastes and preferences. It is thought as a beggining of an application that would let you show your music taste to the world, as well as find and interact with people with the same music taste as you.

Using the [Official Spotify API](https://developer.spotify.com/documentation/web-api), alongside the [LastFM API](https://www.last.fm/api), Musicphile lets you see your actual listening data (recently played and top tracks, artists and genres) and also lets you choose your favorite albums of all time, as well as your current favorite artist and song (which might defer from what your listening habits say). If this were to be a published app, these data points would allow, via a database search, for people to match with other users which share, for example, the same favorite song.

I came up with the idea for this app when I noticed that most of my friends don't have the same music taste as I do, and realize that I would love if an app existed that let you find people nearby to share festivals and concerts with, or maybe just chat about internal group lore or fan theories. 

## Project Overview
### How it works

### Login (or Signup)
Any new user has to sign up to the app and create and account by choosing a name and password *(as in the CS50 Finance Project)*, when you log in for the first time, you have to also connect your account with the Spotify API, so that Musicphile can retrieve your listening information. When this is finished, you finally access the profile page. This pages look nearly identical, and store the information on a SQLite database. This database is explained further below.

### Profile
This is the page where everything happens. in here, you can see your **recently played** songs, as well as your **top tracks, artists and genres** (genres are displayed with a cool percentage that lets you see how your music taste is divided), all of them retrieved with the Spotify API. Top tracks, artists and genres share 3 buttons in the top right part for the user to cycle between time periods to see how his music has looked like for the last 4 weeks, 6 months, or for the whole existence of his account (the Spotify one, not Musicphile's). 

In here you can also see a blank tile for a section called **top 5 albums**. This is the part where the user has to manually select their 5 favorite albums (*an option that spotify doesn't have :wink:*). Any music aficionado has strong opinions on the best albums they have listened to, and likes to share them with the world to make his magnificent taste known. **This is the place to do so**. The album information is retrieved from the LastFM API, so as to not use additional Spotify tokens. After you've selected 5 albums, you can reorder them any way you want, but you must remove one before choosing another, so you have to be selective with your preferences!

Finally (even though it was at the top of the page), you can find two placeholders to select your current favorite artist and song (it's all about favorites here). This is made because even though you might have a song you've listened to **a lot** during your lifetime, there might be a song that evokes strong emotions right now, be it by recent events, emotional state or moment in life. Both of these can be changed anytime.