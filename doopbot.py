import websocket #pip install websocket-client
import json
import time
import os
from pprint import pprint
from features.quick_themes import QuickThemes
from features import responses
from config.commands import commands
import re

class doopBot:
    def __init__(self):
        self.ws = None
        self.bot_name = 'doopbot'
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
        self.users = {}
        self.qt = QuickThemes()
        self.strawpoll_id = None
        
    def update_votes(self, data):
        self.votes = data['params']
        
    def new_message(self, data):
        trigger_prefix = '+'
        message = data['params']['payload'].strip()
        print(f"{self.users[data['params']['userId']]['displayName']}: {message}")
        if message.startswith(trigger_prefix):
            command = message[1:].lower().split()[0]
            if command in commands:
                response = commands[command](self, data)
                if isinstance(response, str):
                    self.send_message(response)
            else:
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

    def update_song_history(self, data):
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
        # self.qt.handle_now_playing(self)
        self.qt.handle_song_change(self)
        songs_played =[f"{i['playedBy']['displayName']}---{i['track']['name']}---{i['track']['artists'][0]['name']}" for i in self.song_history]


    def on_error(self, ws, data):
        pass
    

    def stay_awake(self, data=None):
        stay_awake_data = {
            'jsonrpc': '2.0',
            'method': 'stayAwake',
            'params': {
                'date': str(int(time.time() * 1000))
            }
        }
        return stay_awake_data
    
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
        print('Joining the room.')
        # join the specified channel when the connection is established
        join_data = {
            'method': 'join',
            'params': {
                'channelId': self.channel_id
            },
            'id': 1
        }
        bot_profile = {
            "method": "editUser",
            "params": {
                "image": "https://i.imgur.com/Ysm7Y6p.jpeg",
                "bio": """  +qt\n+qt-end\\n+qt-set-theme THEME NAME\n+qt-skip\n+vote
                            +vote --- creates a strawpoll using the last two songs played.
                            +vote things,separated,by,commas --- creates a strawpoll with the requested options
                            +vote # --- Creates a strawpoll based on the last # of played songs
                            +vote --- spams the strawpoll link 4 times
                            +vote cancel/stop --- Cancels the strawpoll, results will not be posted at the end of the song. Allows for a new strawpoll to be created.""",
            }
        }
        self.ws.send(json.dumps(join_data))
        self.ws.send(json.dumps(bot_profile))
        



    def on_message(self, ws, message):
        data = json.loads(message)
        if data.get('method') in self.event_handlers:
            response = self.event_handlers[data['method']](data)
            self.ws.send(json.dumps(response))
        else:
            print(data.get('method'))

    def run(self):
        # websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(f'wss://app.rvrb.one/ws-bot?apiKey={self.rvrb_api_key}',
                                on_error=self.on_error,
                                on_open=self.on_open,
                                on_message=self.on_message,)
        self.ws.run_forever(ping_interval=30)

def main():
    bot = doopBot()
    bot.run()

if __name__ == "__main__":
    main()
