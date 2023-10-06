from .quick_themes import QuickThemes


# def qtstart(bot, data):
#     if bot.qt.active:
#         return "Quick Themes is already running!"
#     else:
#         if data['params']['userId'] not in bot.dj_queue:
#             return f"You need to be in the queue to start Quick Themes!"
#         else:
#             bot.qt.leader = data['params']['userId']
#             bot.qt.caboose = bot.dj_queue[-1]
#             bot.qt.leader_queue_position = bot.dj_queue.index(bot.qt.leader) # If the leader steps down.. I'll need a way to auto-assign a new leader. By tracking the index I can assign the next user in the queue to the leader spot.
#             bot.qt.current_theme = bot.qt.choose_theme()
#             bot.qt.next_theme = bot.qt.choose_theme()
#             username = bot.users[bot.qt.leader]['displayName']
#             return f"🍕Quick Themes has begun!🍺<hr>🍕The theme is {bot.qt.current_theme} (starting with {username}'s spin)🍺<hr>🍕On deck is {bot.qt.next_theme}🍺"

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
            return f"🍕Quick Themes will start on {bot.users[bot.qt.leader]['displayName']}'s spin!🍺<hr>🍕The first theme is {bot.qt.current_theme}🍺<hr>🍕On-deck is {bot.qt.next_theme}🍺"

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
    
    
    
            
