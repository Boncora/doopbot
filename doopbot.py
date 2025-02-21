import websocket #pip install websocket-client
import json
import time
import os
from pprint import pprint
from features.quick_themes import QuickThemes
from features import responses
from config.commands import commands
import re
import rel
from datetime import datetime
import sqlite3
import signal
import logging
import os

# """
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS spins (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     song_name TEXT NOT NULL,
#     started_at TEXT NOT NULL,
#     song_uri TEXT NMOT NULL,
#     artist_name TEXT NOT NULL,
#     star_count INTEGER NOT NULL,
#     dj_name TEXT NOT NULL,
#     date TEXT NOT NULL,
#     user_id TEXT NOT NULL,
#     starred_by TEXT NOT NULL,
#     duration INTEGER NOT NULL
# )
# """

class doopBot:
    def __init__(self):
        self.ws = None
        self.bot_name = 'doopbot'
        self.keep_running = True
        self.db_path = './features/pb_db/pb_rvrb_spins.db'
        self.channel_id = '6321dbf8740da59fefee3eae'
        self.rvrb_api_key = os.getenv('PB_RVRB_BOT_API_KEY')
        self.song_history = []
        self.messages = []
        self.event_handlers = {
            'keepAwake': self.stay_awake,
            'updateChannelDjs': self.update_dj_queue,
            'updateChannelUsers': self.update_users,
            'playChannelTrack': self.now_playing,
            'updateChannelHistory': self.update_song_history,
            'updateChannelMeter': self.update_votes,
            'pushChannelMessage': self.new_message,
        }
        self.dj_queue = []
        self.votes = {}
        self.users = {}
        self.qt = QuickThemes()
        self.strawpoll_id = None
        self.recording = False
        self.recording_theme = None
        self.recording_playlist = None
        self.logger = self.setup_logger()
        
    def update_votes(self, data):
        self.votes = data['params']['voting']
        
    def new_message(self, data):
        trigger_prefix = '+'
        message = data['params']['payload'].strip()
        if data['params']['userName'] != 'RVRB':
            self.logger.info(f"{data['params']['userName']}: {message}")
        if message.startswith(trigger_prefix):
            command = message[1:].lower().split()[0]
            if command in commands:
                response = commands[command](self, data)
                if isinstance(response, str):
                    self.send_message(response)
            else:
                # room_stuff = """{"jsonrpc":"2.0","method":"editChannel","params":{"channelId":"rock","slug":"rock","title":"🍺PIZZA & BEER🍕","genre":"Eclectic mix, tasty tunes.","visibility":"public","password":"","infoLink":"https://discord.gg/cQ5UH9R3CS","promoImageHref":"https://www.last.fm/user/JQBX-Pizza-Beer","promoImageUrl":"https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExN25xMHhyanhhcGFwcWgzdmZhY21hNWJ5Znl5NmkwcW1md2JkZGw2ZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/10RVT8mge0xQwU/giphy.gif","limitDjs":false,"maxDjs":4,"sameRoleCanKick":true,"noChangeVote":false,"banned":["6560248175be41759236df3a","6360306e2f9b8fe2ed76a748"],"listenersTitle":"Roadies","djsTitle":"The Last DJ","activeDjTitle":"is making some noise!","chatPrompt":"/ro","disableAutoReact":false,"writeBookmarkedToPlaylist":true,"writeBoofMarkToPlaylist":true,"writeThisIsPlaylist":true,"greeting":"🤘 Raise those horns 🤘 and raise a glass 🍺 and join us on discord https://discord.gg/KSr5bKyAYz","lastfm":{"username":"JQBX-Pizza-Beer","password":"JQBX-pb-2021!","api_key":"549b07635a42b6884fc6869d8dd60a81","api_secret":"6a909190e4453aea75e5ad3d0dc2d2fe"},"discord":{"serverId":"707223665158389820","channelId":"1090294627208282175","mode":"commands"}}}"""
                # self.ws.send(room_stuff)
                self.send_message("I am a black hole shitting into the void")
        self.messages.append(data['params'])
        if len(self.messages) > 100:
            self.messages.pop(0)

        
    def update_users(self, data):
        """
        I think I'll want to mostly use this to correlate IDs to display names..
        converted to a dict.
        """
        self.users = {user['_id']: user for user in data['params']['users']}

        
    def update_spin_db(self, data):
        artist_name = self.now_playing['track']['artists'][0]['name']
        song_name = self.now_playing['track']['name']
        started_at = datetime.now().isoformat()
        song_uri = self.now_playing['track']['uri']
        star_count = data['voteSummary']['star']
        # starred_by = ','.join([user_id for user_id in self.votes.keys() if self.votes[user_id]['star']])
        starred_by = ','.join([
            self.users[user_id]['userName'] if user_id in self.users else user_id
            for user_id in self.votes.keys()
            if self.votes[user_id]['star']
        ])
        try:
            dj_name = data['playedBy']['userName']
            dj_id = data['playedBy']['_id']
        except KeyError:
            dj_name = "Miss Groupie"
            dj_id = "123456789"
        duration = self.now_playing['track']['duration_ms']
        self.logger.info(f"Artist: {artist_name}---Track: {song_name}---Started at: {started_at}---URI: {song_uri}---Star Count{star_count}---DJ: {dj_name}---DJID: {dj_id}---Duration: {duration}---Starred by: {starred_by}")
        # Connect to the database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Insert the new row into the spins table
        cursor.execute("""
            INSERT INTO spins (song_name, started_at, song_uri, artist_name, star_count, dj_name, dj_id, starred_by, duration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (song_name, started_at, song_uri, artist_name, star_count, dj_name, dj_id, starred_by, duration))
        # Commit the transaction and close the connection
        conn.commit()
        conn.close()

        
        
    def update_song_history(self, data):
        self.update_spin_db(data['params'])
        self.song_history.append(data['params'])
        if len(self.song_history) > 100:
            self.song_history.pop(0)

    def update_dj_queue(self, data):
        self.dj_queue = data['params']['djs']
        self.qt.handle_qt_dj_queue(self)

    def now_playing(self, data):
        self.now_playing = data['params']
        if self.strawpoll_id:
            result = responses.poll_results(self)
            self.send_message(result)
        responses.artist_announcements(self)
        if self.recording:
            responses.auto_add(self)
        self.qt.handle_song_change(self)
        #songs_played =[f"{i['playedBy']['displayName']}---{i['track']['name']}---{i['track']['artists'][0]['name']}" for i in self.song_history]
        self.logger.info(f"#########{data['params']['track']['name']}--{data['params']['track']['artists'][0]['name']}#########")

    def on_error(self, ws, error):
        self.logger.info(f"Error occurred: {error}")
        if isinstance(error, websocket.WebSocketConnectionClosedException):
            self.logger.info("Connection lost. Attempting to reconnect...")
            time.sleep(5)  # Small delay before reconnecting
            self.run()  # Restart the connection

    

    def stay_awake(self, data=None):
        stay_awake_data = {
            'jsonrpc': '2.0',
            'method': 'stayAwake',
            'params': {
                'date': str(int(time.time() * 1000))
            }
        }
        return stay_awake_data

    # def send_upvote(self):
    #     send_message = {
    #         'jsonrpc': '2.0',
    #         'method': 'pushMessage',
    #         'params': {
    #             'payload': message
    #         }
    #     }
    #     self.ws.send(json.dumps(send_message))

    def send_message(self, message):
        send_message = {
            'jsonrpc': '2.0',
            'method': 'pushMessage',
            'params': {
                'payload': message
            }
        }
        self.ws.send(json.dumps(send_message))


    def on_open(self, data):
        self.logger.info('Joining the room.')
        # join the specified channel when the connection is established
        join_data = {
            'method': 'join',
            'params': {
                'channelId': self.channel_id
            }
        }
        bot_profile = {
            "method": "editUser",
            "params": {
                "displayName": "Han Tyumi",
                "image": "https://i.imgur.com/Ysm7Y6p.jpeg",
                # "image": "https://i.imgur.com/PcGKQOH.png", #halloween.
                "bio": """  +qt\n+qt-end\\n+qt-set-theme THEME NAME\n+qt-skip\n+vote
                            +vote --- creates a strawpoll using the last two songs played.
                            +vote things,separated,by,commas --- creates a strawpoll with the requested options
                            +vote # --- Creates a strawpoll based on the last # of played songs
                            +vote --- spams the strawpoll link 4 times
                            +vote cancel/stop --- Cancels the strawpoll, results will not be posted at the end of the song. Allows for a new strawpoll to be created.""",
            }
        }

        self.ws.send(json.dumps(bot_profile))
        self.ws.send(json.dumps(join_data))

    def on_close(self, ws, close_status_code, close_msg):
        self.logger.info(f"WebSocket closed: code={close_status_code}, message={close_msg}")
        self.logger.info("Attempting to reconnect in 5 seconds...")
        time.sleep(5)
        self.run()  # Restart the connection

    def on_message(self, ws, message):
        data = json.loads(message)
        # print(data.get('method'))
        # pprint(data)
        if data.get('method') in self.event_handlers:
            response = self.event_handlers[data['method']](data)
            self.ws.send(json.dumps(response))
        # else:
        #     print(data.get('method'))

    def setup_logger(self):
        logger = logging.getLogger('doopbot')
        logger.setLevel(logging.INFO)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_file = os.path.join(script_dir, 'doopbot.log')
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger
        

    def run(self):
        # Define a custom signal handler
        def signal_handler(sig, frame):
            self.logger.info("KeyboardInterrupt caught. Shutting down gracefully...")
            self.keep_running = False
            if self.ws:
                self.ws.close()
            # Exit the event loop if using rel
            rel.abort()

        # Register the signal handler for SIGINT (Ctrl+C)
        signal.signal(signal.SIGINT, signal_handler)

        while self.keep_running:
            try:
                self.ws = websocket.WebSocketApp(
                    f'wss://app.rvrb.one/ws-bot?apiKey={self.rvrb_api_key}',
                    on_error=self.on_error,
                    on_open=self.on_open,
                    on_message=self.on_message,
                    on_close=self.on_close  # if implemented
                )
                # Start the connection. Remove rel.signal if using your custom handler.
                self.ws.run_forever(ping_interval=30)
                # If using rel and you need dispatch, you can still call:
                # rel.dispatch()
            except Exception as e:
                self.logger.info(f"Unexpected exception: {e}")
            if self.keep_running:
                self.logger.info("Reconnecting in 5 seconds...")
                time.sleep(5)


    def stop(self):
        self.ws.close()

def main():
    bot = doopBot()
    bot.run()



if __name__ == "__main__":
    main()
