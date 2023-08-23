import random
import yaml

            
class QuickThemes:
    def __init__(self, leader=None, dj_queue=None):
        self.themes = self.theme_list('qt_themes.yml')
        self.used_themes = self.theme_list('used_themes.yml')
        self.user_theme_list = ['user_theme_test', 'user_theme_test_2', 'user_theme_test_3']
        self.next_theme = self.choose_theme()
        self.current_theme = self.choose_theme()
        self.leader = leader

    def submit_theme(self, theme):
        self.user_theme_list.append(theme)
        
    def choose_theme(self):
        """
        Selects a theme. If manual 
        """
        if self.user_theme_list:
            selected_theme = self.user_theme_list.pop()
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

