import readchar
from MainScreen import MainScreen
from UserSettings import SettingsScreen, load_settings

def main():
    settings = load_settings()
    if not settings or settings["ApiKey"] == "enter-key-here":
        cur_screen = SettingsScreen()
    else:
        cur_screen = MainScreen()
    while cur_screen:
        key = readchar.readkey()
        cur_screen = cur_screen.handle_input(key)


if __name__ == "__main__":
    main()