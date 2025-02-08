import readchar

from rich.table import Table
from rich.rule import Rule
from rich.markdown import Markdown

from pathlib import Path
import json
import os

import MainScreen
from NewChat import load_recent
from Screen import Screen, _get_input


def get_config_dir():
    """Returns the usual location for config files, depending on the OS. Additionally makes an empty directory there for this app if it doesn't exist yet."""
    if os.name == 'nt':  # Windows
        base_dir = os.getenv('APPDATA')
    else:  # Linux/Mac
        base_dir = os.path.expanduser('~/.config')
    
    config_dir = Path(base_dir) / 'llmFrontend'
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def save_settings(settings: dict):
    """Store settings in a .json file inside this app's config directory.

    Args:
    settings: A dictionary holding user settings as key-value pairs."""
    config_file = get_config_dir() / 'settings.json'
    with open(config_file, 'w') as f:
        json.dump(settings, f)

def load_settings():
    """Load this app's settings file.
    
    Returns:
    User settings as a dictionary, or an empty dictionary if the file doesn't exist."""
    config_file = get_config_dir() / 'settings.json'
    if config_file.exists():
        with open(config_file) as f:
            return json.load(f)
    return {}  # Default settings

def delete_settings():
    """Delete this app's settings file."""
    config_file = get_config_dir() / 'settings.json'
    if config_file.exists():
        os.remove(config_file)


class SettingsScreen(Screen):
    """A screen for adjusting user settings."""

    default = {
            "URL": "https://api.deepseek.com",
            "ApiKey": "enter-key-here",
            "Model": "deepseek-chat",
            "Temperature": 1,
            "FrequencyPenalty": 0.2,
            "PresencePenalty": 0.2,
            }
    
    def __init__(self, scr:"Screen" = None):
        if not scr:
            self.cur, self.messages, self.file = load_recent()
            settings = load_settings()
            self.settings = settings if settings else self.default
        self.index = 0
        super().__init__(scr)
        self.settings_keys= list(self.settings.keys())

    
    def _update_renderables(self):
        table = Table(title="Settings", show_header=False, show_lines=True)
        table.add_column("Key", style="bold cyan")
        table.add_column("Value", style="bold green")

        for i, (key, value) in enumerate(self.settings.items()):
            # Highlight the selected row
            if i == self.index:
                table.add_row(key, str(value), style="on blue")
            else:
                table.add_row(key, str(value))

        self.renderables = [table, Rule(style="bold white")]
        self.renderables.append(Markdown("Arrow Keys: Navigate | Enter: Edit | 's': Save & Return | 'r': Reset."))
        self.renderables.append(Rule(style = "bold white"))

    def handle_input(self, key):
        if key == readchar.key.UP:
            self.index=max(0, self.index-1)
            self._update_renderables()
            self._render()
        elif key == readchar.key.DOWN:
            self.index=min(len(self.settings_keys)-1, self.index+1)
            self._update_renderables()
            self._render()
        elif key == readchar.key.ENTER:
            self._update_setting()
            self._update_renderables()
            self._render()
        elif key == 's':
            save_settings(self.settings)
            self._update_renderables()
            self._render()
            self._connect()
            return MainScreen.MainScreen(self)
        elif key == 'r':
            delete_settings()
            self.settings = self.default
            self._update_renderables()
            self._render()
        return self

    def _update_setting(self):
        """After a user selects a setting to change, this parses their input and if valid updates the settings dictionary. Important: this does not yet permanently store the change on disk."""
        key = self.settings_keys[self.index]
        cur_val = self.settings[key]
        new_val = _get_input(prompt_text=f"Enter new value for {key}: ", default= str(cur_val))
        if not new_val:
            return
        if key in ["Temperature", "FrequencyPenalty", "PresencePenalty"]:
            try:
                new_val = float(new_val)
            except ValueError:
                return
        self.settings[key] = new_val
