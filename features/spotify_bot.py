import os
import spotipy
import spotipy.util as util
import yaml
from pprint import pprint

def login():
    '''
    logs in to spotify. currently only works for my own account.
    '''
    #print('attempting to build playlist')
    SPOTIFY_ID = os.environ.get('SPOTIFY_BOT_APP_ID2')
    SPOTIFY_SECRET = os.environ.get('SPOTIFY_BOT_APP_KEY2')
    SPOTIFY_USERNAME = os.environ.get('SPOTIFY_USERNAME2')
    scope = 'playlist-modify-private, user-read-recently-played, playlist-modify-public, playlist-read-private, user-follow-read, user-read-private'
    token = util.prompt_for_user_token(username=SPOTIFY_USERNAME, scope=scope, client_id=SPOTIFY_ID,
                                       client_secret=SPOTIFY_SECRET, redirect_uri="http://localhost:8080/callback")
    #spotipy will create a .cache-username file.
    #If you need to do the spotify redirect thing again to use a new user, delete that file beforehand.
    sp = spotipy.Spotify(auth=token, requests_timeout=10, retries=10)
    print(SPOTIFY_ID)
    print(SPOTIFY_SECRET)
    print(SPOTIFY_USERNAME)
    return sp

# def doopbot_spotify_login():
#     '''
#     logs in to spotify. currently only works for my own account.
#     '''
#     print('attempting to login')
#     SPOTIFY_ID = os.environ.get('SPOTIFY_BOT_APP_ID2')
#     SPOTIFY_SECRET = os.environ.get('SPOTIFY_BOT_APP_KEY2')
#     SPOTIFY_USERNAME = os.environ.get('SPOTIFY_USERNAME2')
#     scope = 'playlist-modify-private, user-read-recently-played, playlist-modify-public, playlist-read-private, user-follow-read, user-read-private'
#     token = util.prompt_for_user_token(username=SPOTIFY_USERNAME, scope=scope, client_id=SPOTIFY_ID,
#                                        client_secret=SPOTIFY_SECRET, redirect_uri="https://localhost:8080/callback")
#     #spotipy will create a .cache-username file.
#     #If you need to do the spotify redirect thing again to use a new user, delete that file beforehand.
#     sp = spotipy.Spotify(auth=token)
#     return sp


def write_playlists_config(theme_playlists):
    with open(r'../config/qt_playlists.yml', 'w') as file:
        documents = yaml.dump(theme_playlists, file)

def get_theme_playlist(theme):
    '''
    returns a dictionary of themes and their corresponding playlist. Adds new playlists if new themes are discovered.
    '''
    with open(r'config/qt_playlists.yml') as file:
        theme_playlists = yaml.load(file, Loader=yaml.FullLoader)
    if not theme_playlists.get(theme.lower().strip()):
        print(f'Adding {theme.lower()} theme playlist')
        sp = login()
        print('trying to get playlist')
        playlist = sp.user_playlist_create('9lmdbr25slw401t2mmq86y2sd', theme.lower().strip(), public=True, collaborative=False, description='')
        theme_playlists[theme.lower().strip()] = {'uri': playlist['uri'], 'link': playlist['external_urls']['spotify']}
        with open(r'config/qt_playlists.yml', 'w') as file:
            documents = yaml.dump(theme_playlists, file)
    return theme_playlists[theme.lower().strip()]

def add_to_playlist(playlist_uri, track_uri):
    '''
    
    '''
    sp = login()
    try:
        sp.user_playlist_add_tracks('9lmdbr25slw401t2mmq86y2sd', playlist_uri, [track_uri], position=0)
    except Exception as e:
        print(e)


def quick_themes_add(room_details):
    ''' Adds the track to the correct theme playlist'''
    sp = login()
    sp = doopbot_spotify_login() #doopbots account has the mass of theme playlists..
    theme = room_details['theme'].lower().strip()
    playlist = room_details['qt_playlists'].get(theme)
    track = room_details['nextTrack']['uri']
    if playlist != None:
        sp.user_playlist_add_tracks('9lmdbr25slw401t2mmq86y2sd', playlist['uri'], [track], position=0)
    else:
        print('cannot find that playlist')
