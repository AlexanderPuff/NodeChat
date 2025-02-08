from datetime import datetime
import os
import glob
import json
import readchar
from Screen import Screen
import MainScreen

from rich.table import Table

from conversationTree import *

CHATS_PATH = "./userInfo/chats"
PROMPTS_PATH = "./userInfo/prompts"

def _file_name(file: str):
    """Given a file name remove its ending."""
    name = os.path.basename(file)
    return name.split('.')[0]

def load_recent():
    """Load the most recent saved chat, or start a new one if no chat files exist.
    
    Returns:
    - The current message node from last session, needed to exactly reconstruct its state.
    - A list containing all messages in the current branch, starting at the root.
    - The file that was loaded (None if there wasn't any)."""
    files = _load_chat_files()
    if not files:
        with open(PROMPTS_PATH + "/standardAssistant.txt", "r", encoding="utf-8") as file:
                prompt = file.read()
        root = Msg_Node(None, "system", prompt, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0)
        msgs = [root.to_msg()]
        return root, msgs, None
    file = max(files, key = os.path.getmtime)
    cur, messages = load_file(file)
    return cur, messages, file

def load_file(file: str):
    """Loads a given chat file.

    Args:
    file: Path to the file that will be read.
    
    Returns:
    - The current message from when the chat was last saved.
    - A list holding all messages in the current conversation branch, starting at the root.
    """
    with open(file, 'r') as f:
        data = json.load(f)
    messages = []
    root, cur = deserialize(data['messages'], data['cur_id'])
    if not cur:
        return root, [root.to_msg()]
    cur_it = cur
    while cur_it:
        messages.append(cur_it.to_msg())
        cur_it=cur_it.prev
    messages.reverse()
    return cur, messages

def _load_chat_files():
    """Returns a list of paths for all saved chat files."""
    return glob.glob(os.path.join(CHATS_PATH, '*.json'))

def _load_prompt_files():
    """Returns a list of paths for all saved system prompt files."""
    return glob.glob(os.path.join(PROMPTS_PATH, '*.txt'))


class ChatLoader(Screen):
    """This screen implements loading and starting new chats."""

    def __init__(self, scr:"Screen"):
        self.files = _load_chat_files()
        self.mode = 'Load' if self.files else 'New'
        self.files = self.files if self.files else _load_prompt_files()
        self.index = 0
        super().__init__(scr)

    
    def _update_renderables(self):
        if self.mode == 'Load':
            table = self._gen_table(_load_chat_files())
            self.renderables = [table, Rule(style='bold white')]
            self.renderables.append(Markdown("Select chat to load, or press 'n' to start new chat."))
        
        elif self.mode == 'New':
            table = self._gen_table(_load_prompt_files())
            self.renderables = [table, Rule(style='bold white')]
            self.renderables.append(Markdown('Select system prompt for new chat.'))
    
    def handle_input(self, key):
        if key == readchar.key.UP:
            self.index=max(0, self.index-1)

        elif key == readchar.key.DOWN:
            self.index = min(len(self.files), self.index+1)
        elif key == readchar.key.ENTER:
            return self._sel_file()
        elif key == 'n' and self.mode == 'Load':
            self.mode = 'New'
            self.index = 0
        elif key == readchar.key.ESC and self.mode=='New':
            self.mode = 'Load'
            self.index = 0
        
        self._update_renderables()
        self._render()
        return self

    def _sel_file(self):
        """Lets users select a file; Either a chat or a prompt.

        Returns:
        A Main Screen, ready to go for chatting."""
        if self.mode == 'Load':
            self.file = self.files[self.index]
            self.cur, self.messages = load_file(self.file)
            return MainScreen.MainScreen(self)
        elif self.mode == 'New':
            with open(self.files[self.index], "r", encoding="utf-8") as file:
                prompt = file.read()
            root = Msg_Node(None, "system", prompt, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0)
            self.messages = [root.to_msg()]
            self.cur = root
            self.file = None
            return MainScreen.MainScreen(self)



    def create_empty_json(self):
        """Creates an empty .json file in the chats directory, with the current time as its name."""
        time = datetime.now()
        name = time.strftime("%Y-%m-%d_%H-%M-%S") + ".json"
        self.file = os.path.join(CHATS_PATH, name)

        with open(self.file, 'w') as f:
            json.dump({}, f, indent = 4)


    def _gen_table(self, files):
        """Returns a table showing a list of files and marking the one currently selected by the user."""
        table = Table(show_header=False, show_lines=True)
        table.add_column('File', style="bold cyan")

        for i in range(0, len(files)):
            if i==self.index:
                table.add_row(_file_name(files[i]), style="on blue")
            else: table.add_row(_file_name(files[i]))

        return table

