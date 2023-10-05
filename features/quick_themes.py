import random
import yaml


class QuickThemes:
    def __init__(self):
        self.active = False
        self.themes = self.theme_list('qt_themes.yml')
        self.used_themes = self.theme_list('used_themes.yml')
        self.user_theme_list = self.theme_list('manual_themes.yml')
        self.leader = None
        self.current_theme = None
        self.next_theme = None

    def submit_theme(self, theme):
        self.user_theme_list.append(theme)

    def submit_theme(self, theme):
        self.user_theme_list.append(theme)

    def choose_theme(self):
        """
        Selects a theme. If any themes were submitted in the chat, prioritize those first. 
        """
        if self.user_theme_list:
            selected_theme = self.user_theme_list.pop()
            with open('config/manual_themes.yml', 'w') as f:
                yaml.dump(self.user_theme_list, f)
            return selected_theme
        if not self.themes:
            #rotate all used themes back into the list.
            self.themes = self.used_themes
            self.used_themes = []
        random_theme = random.choice(self.themes)
        index = self.themes.index(random_theme)
        print(len(self.themes))
        selected_theme = self.themes.pop(index)
        print(len(self.themes))
        with open('config/qt_themes.yml', 'w') as f:
            yaml.dump(self.themes, f)
        with open('config/used_themes.yml', 'w') as f:
            yaml.dump(self.used_themes, f)
        self.used_themes.append(selected_theme)
        return selected_theme
    
    def theme_list(self, filename):
        with open(f'config/{filename}', 'r') as yaml_file:
            theme_list = yaml.load(yaml_file, Loader=yaml.FullLoader)
        if theme_list == None:
            theme_list = []
        return theme_list

    def handle_qt_dj_queue(self, bot):
        if bot.dj_queue[0] == bot.qt.leader:
            if not bot.qt.active:
                # The leader triggers QT with the qtstart command, but it doesn't begin until their first spin
                # I want the current/on-deck themes pulled before it begins so users can get ready.
                bot.qt.active = True
            else:
                # The game is in progress. Cycle themes each time the leader spins.
                bot.qt.current_theme = bot.qt.next_theme
                bot.qt.next_theme = bot.qt.choose_theme()
                bot.send_message(f'New theme is {bot.qt.current_theme}. On deck is {bot.qt.next_theme}')
        if bot.qt.leader not in bot.dj_queue:
            # Reassign the leader if the user steps down for any reason.
            bot.qt.leader = bot.dj_queue[bot.qt.leader_queue_position+1]
        bot.qt.leader_queue_position = bot.dj_queue.index(bot.qt.leader)
                
            


