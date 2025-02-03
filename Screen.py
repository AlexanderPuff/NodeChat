import os
from openai import OpenAI
from prompt_toolkit import prompt
from rich.console import Console
from prompt_toolkit.key_binding import KeyBindings

def _clear_terminal():
    """Reset and clear the current terminal."""
    os.system('cls' if os.name == 'nt' else 'printf "\033[2J\033[3J\033[H"')

bindings = KeyBindings()
@bindings.add('enter')
def _(event):
    event.current_buffer.validate_and_handle()

@bindings.add('escape')
def _(event):
    event.current_buffer.reset()
    event.app.exit(result = None)


def _get_input(prompt_text: str = "> ", default: str = ""):
    """Get user input, a custom prompt and prefill can be provided. Note: this uses custom key binds.
    
    Args:
        prompt_text: Text to display in front of user input, for example a question
        default: Optional default value for prefill

    Returns:
        User input as a string, or None if they pressed escape.
    
    Example:
        >>> response = _get_input(prompt_text = "Enter name: ", default = "Name")
        Enter name: Name_
    """
    user_input = prompt(prompt_text, key_bindings=bindings, default=default)
    return user_input

class Screen():
    def __init__(self, scr: "Screen" = None):
        if scr:
            self.cur = scr.cur
            self.messages = scr.messages
            self.settings = scr.settings
            self.console = scr.console
            self.file = scr.file
            self.client = scr.client
        else:
            self.console = Console()
        self._update_renderables()
        self._render()
            

    def _update_renderables(self):
        self.renderables=[]
    
    def handle_input(self, key):
        return self
    
    def _render(self):
        _clear_terminal()
        for renderable in self.renderables:
            self.console.print(renderable)
    
    def _connect(self):
        """Connect to an OpenAI-compatible API; 
        """
        if hasattr(self, "client"):
            new_key = str(self.client.api_key) != self.settings['ApiKey']
            new_url = str(self.client.base_url) != self.settings['URL']
            if new_key or new_url:
                self.client.close()
                self.client = OpenAI(api_key=self.settings['ApiKey'], base_url=self.settings['URL'])
        else: self.client = OpenAI(api_key=self.settings['ApiKey'], base_url=self.settings['URL'])
