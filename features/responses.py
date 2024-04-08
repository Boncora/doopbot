# from .quick_themes import QuickThemes
from . import strawpoll
from . import spotify_bot
import re
import yaml

#from ..config import commands

def display_help(bot, data):
    help_message = [
        'qt --- Starts Quick ⚡ Themes.. Displays current/on-deck themes if QT is already in progress',
        'qt-end --- Stops Quick ⚡ Themes',
        'qt-skip --- Moves the on-deck theme into the current theme. Reassigns leader to the next DJ',
        'qt-set-theme THEME NAME --- Assigns a user specified theme to the on-deck theme.',
        'qt-playlist --- Displays the current/ondeck theme playlists',
        'vote --- Creates a strawpoll link. By default it uses the last 2 songs played as options. Spams the URL 4 times if a poll is active. Results post after current song finishes',
        'vote #--- Creates a strawpoll link. Last # songs are the options',
        'vote option a, option b, option c --- Creates a strawpoll link. Separate options with commas',
        'vote cancel/stop/end --- Ends the current strawpoll in case we need to create a new one.',
        'addto THEME --- Adds the current playing track to one of our room playlists',
        'get-playlist THEME NAME --- Gets the URL to a given room theme playlist'
        'auto-addto THEME NAME --- Starts automatically adding tracks to a playlist until stop-recording or stop-addto is ran.'
    ]
    bot.send_message('<br>'.join(help_message))

def qt(bot, data):
    if bot.qt.leader and bot.qt.active == False:
        # Someone initiated QT so the leader and themes are set but it hasn't started yet
        return f"🍕Quick Themes will start on {bot.users[bot.qt.leader]['displayName']}'s spin!🍺<hr>🍕The first theme is {bot.qt.current_theme}🍺<hr>🍕On deck is {bot.qt.next_theme}🍺"
    if bot.qt.active:
        # QT is in progress. Just tell them what the current and next theme is.
        return f"🍕Current theme is {bot.qt.current_theme}🍺<hr>🍕On deck is {bot.qt.next_theme} (starts on {bot.users[bot.qt.leader]['displayName']}'s next spin)🍺"
    else:
        if data['params']['userId'] not in bot.dj_queue:
            return f"You need to be in the queue to start Quick Themes!"
        else:
            bot.qt.leader = data['params']['userId']
            bot.qt.caboose = bot.dj_queue[-1]
            bot.qt.leader_queue_position = bot.dj_queue.index(bot.qt.leader) # If the leader steps down.. I'll need a way to auto-assign a new leader. By tracking the index I can assign the next user in the queue to the leader spot.
            bot.qt.current_theme = bot.qt.choose_theme()
            bot.qt.next_theme = bot.qt.choose_theme()
            bot.qt.next_theme_playlist = spotify_bot.get_theme_playlist(bot.qt.next_theme)['link']
            bot.qt.current_theme_playlist = spotify_bot.get_theme_playlist(bot.qt.current_theme)['link']
            return f"🍕Quick Themes will start on {bot.users[bot.qt.leader]['displayName']}'s spin!🍺<hr>🍕The first theme is {bot.qt.current_theme}🍺<hr>🍕On-deck is {bot.qt.next_theme}🍺"

def qt_playlist(bot, data):
    return f"🍕{bot.qt.current_theme}--{bot.qt.current_theme_playlist}🍺<br>🍕{bot.qt.next_theme}--{bot.qt.next_theme_playlist}🍺"


def find_and_add_to_playlist(bot, data):
    message = data['params']['payload'].strip()
    theme = message.replace('+addto', '').strip()
    playlist = spotify_bot.get_theme_playlist(theme)
    bot.send_message(f"Adding {bot.now_playing['track']['name']} to {theme.upper()} playlist.<hr>{playlist['link']}")
    spotify_bot.add_to_playlist(playlist['uri'], bot.now_playing['track']['uri'])

def get_playlist(bot, data):
    message = data['params']['payload'].strip()
    theme = message.replace('+get-playlist', '').strip()
    with open(r'config/qt_playlists.yml') as file:
        theme_playlists = yaml.load(file, Loader=yaml.FullLoader)
    if theme_playlists.get(theme.lower()):
        bot.send_message(f"Here's the room playlist for 🍕{theme.upper()}🍺<hr>{theme_playlists[theme.lower()]['link']}")
    else:
        bot.send_message(f"We don't have a playlist for 🍕{theme.upper()}🍺 yet")
    
def qt_end(bot, data):
    if bot.qt.leader:
        bot.qt.leader = None
        bot.qt.active = False
        bot.qt.current_theme = None
        bot.qt.next_theme = None
        return "🍕Quick ⚡ Themes has ended🍺<hr>Thanks for hanging out with us!"
    else:
        return "🍕Quick ⚡ Themes was not running🍺"


def qt_skip(bot, data):
    if bot.qt.leader:
        bot.qt.current_theme = bot.qt.next_theme
        bot.qt.next_theme = bot.qt.choose_theme()
        bot.qt.next_theme_playlist = spotify_bot.get_theme_playlist(bot.qt.next_theme)['link']
        bot.qt.current_theme_playlist = spotify_bot.get_theme_playlist(bot.qt.current_theme)['link']
        if len(bot.dj_queue) > 2:
            bot.qt.leader = bot.dj_queue[1]
            bot.qt.active = False
            return f"🍺Skipping theme<hr>🍕The theme is now {bot.qt.current_theme} (starting on {bot.users[bot.qt.leader]['displayName']}'s next spin)🍺<hr>🍕The new on-deck theme is {bot.qt.next_theme}"

def qt_set_theme(bot, data):
    message = data['params']['payload'].strip()
    requested_theme = message.replace('+qt-set-theme', '').strip()
    if requested_theme:
        bot.qt.next_theme = requested_theme.upper()
        return f"🍕On-deck theme set to {bot.qt.next_theme}🍺"
    else:
        bot.qt.next_theme = bot.qt.choose_theme()
        return f"🍕On-deck randomly selected and changed to {bot.qt.next_theme}🍺"
    
    
def create_strawpoll(bot, data):
    message = data['params']['payload'].strip()
    if message == '+vote cancel' or message == '+vote stop' or message == '+vote end':
        bot.strawpoll_id = None
        return "strawpoll cancelled"
    if bot.strawpoll_id:
        return f"https://strawpoll.com/{bot.strawpoll_id}<br>"*4
    if message == '+vote':
        if len(bot.song_history) >= 2:
            options = [f"{song['track']['name']} -- {song['track']['artists'][-1]['name']} -- played by {song['playedBy']['displayName']}" for song in bot.song_history[-2:]]
        else:
            return "I don't remember what songs were played. Please provide me a comma-separated list of options to use!"
    elif ',' in message:
        options = message[6:].split(',')
    elif re.search('\d+', message):
        amount_of_options = int(re.search('\d+', message).group())
        if amount_of_options >= len(bot.song_history):
            options = [f"{song['track']['name']}" for song in bot.song_history[-amount_of_options:]]
        else:
            return f"Sorry. I've only tracked the last {len(bot.song_history)} songs"
    poll = strawpoll.create_poll(options)
    if "Error" not in poll:
        bot.strawpoll_id = poll
        return f"https://strawpoll.com/{bot.strawpoll_id}"
    else:
        return "Error creating strawpoll link"


def poll_results(bot):
    results = strawpoll.get_results(bot.strawpoll_id)
    bot.strawpoll_id = None
    #highest_vote = max([option['vote_count'] for option in results['poll_options']])
    #winners = [option['value'] for option in results['poll_options'] if option['vote_count'] == highest_vote]
    result_message = [f"{option['value']}--{option['vote_count']}" for option in results['poll_options']]
    return '<br>'.join(result_message)

def artist_announcements(bot):
    gizzard_artists = ['bootleg gizzard', 'king gizzard & the lizard wizard']
    now_playing_artists = [artist['name'].lower() for artist in bot.now_playing['track']['artists']]
    for artist in now_playing_artists:
        if artist in gizzard_artists:
            bot.send_message('!kglw')
            break

def auto_add(bot):
    spotify_bot.add_to_playlist(bot.recording_playlist['uri'], bot.now_playing['track']['uri'])

def start_recording(bot, data):
    message = data['params']['payload'].strip()
    theme = message.replace('+auto-addto', '').strip()
    if not bot.recording:
        bot.recording = True
        bot.recording_theme = theme.upper()
        bot.recording_playlist = spotify_bot.get_theme_playlist(theme)
        bot.send_message(f"Automatically adding songs to the 🍕{bot.recording_theme.upper()}🍺 playlist. Send +stop-addto or +stop-recording to stop.<hr> {bot.recording_playlist['link']}")
    else:
        bot.send_message(f"Automatic playlist recording is running. The theme is 🍕{bot.recording_theme.upper()}🍺")
        
def stop_recording(bot, data):
    if bot.recording:
        bot.recording = False
        bot.send_message(f"Stopped recording for {bot.recording_theme.upper()}")
        bot.recording_theme = None
        bot.recording_playlist = None
