import websocket #pip install websocket-client
import json
import time
import os
from pprint import pprint
from features.quick_themes import QuickThemes
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
        
    def update_votes(self, data):
        self.votes = data['params']
        
    def new_message(self, data):
        print('new message')
        command = data['params']['payload']
        print(f"{self.users.get(data['params']['userId'])}: {command}")
        if data['params'].get('userName') == 'doop':
            if command in commands:
                response = commands[command](self, data)
                if isinstance(response, str):
                    self.send_message(response)
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
        print('trying to join')
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
                "image": "https://i.imgur.com/Ysm7Y6p.jpeg"
            }
        }
        self.ws.send(json.dumps(join_data))
        self.ws.send(json.dumps(bot_profile))
        

    def on_message(self, ws, message):
        print('on message')
        data = json.loads(message)
        if data.get('method') in self.event_handlers:
            response = self.event_handlers[data['method']](data)
            self.ws.send(json.dumps(response))
        else:
            print(data.get('method'))

    def run(self):
        #websocket.enableTrace(True)
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
