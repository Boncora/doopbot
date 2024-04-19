from features.responses import *

commands = {
    'help': display_help,
    'qt': qt,
    'qt-end': qt_end,
    'qt-skip': qt_skip,
    'qt-set-theme': qt_set_theme,
    'qt-playlist': qt_playlist,
    'vote': create_strawpoll,
    'addto': find_and_add_to_playlist,
    'get-playlist': get_playlist,
    'auto-addto': start_recording,
    'stop-addto': stop_recording,
    'stop-recording': stop_recording,
    'qt-queue': queue_manual_qt_theme
}