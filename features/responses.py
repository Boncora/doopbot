from .quick_themes import QuickThemes

def abc(bot, data):
    return('hello. my name is han tyumi')
    
def hey(bot, data):
    return f'DATA DATADATADATADATA{data}'
    
def qtstart(bot, data):
    if bot.qt.active:
        return "Quick Themes is already running!"
    else:
        if data['params']['userId'] not in bot.dj_queue:
            return f"You need to be in the queue to start Quick Themes!"
        else:
            bot.qt.leader = data['params']['userId']
            bot.qt.caboose = bot.dj_queue[-1]
            bot.qt.leader_queue_position = bot.dj_queue.index(bot.qt.leader) # If the leader steps down.. I'll need a way to auto-assign a new leader. By tracking the index I can assign the next user in the queue to the leader spot.
            bot.qt.current_theme = bot.qt.choose_theme()
            bot.qt.next_theme = bot.qt.choose_theme()
            username = bot.users[bot.qt.leader]['displayName']
            return f"🍕Quick Themes has begun!🍺<hr>🍕The theme is {bot.qt.current_theme} (starting with {username}'s spin)🍺<hr>🍕On deck is {bot.qt.next_theme}🍺"










