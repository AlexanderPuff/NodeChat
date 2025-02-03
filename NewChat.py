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
    name = os.path.basename(file)
    return name.split('.')[0]

def load_recent():
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
    return glob.glob(os.path.join(CHATS_PATH, '*.json'))

def _load_prompt_files():
    return glob.glob(os.path.join(PROMPTS_PATH, '*.txt'))


class ChatLoader(Screen):

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
        time = datetime.now()
        name = time.strftime("%Y-%m-%d_%H-%M-%S") + ".json"
        self.file = os.path.join(CHATS_PATH, name)

        with open(self.file, 'w') as f:
            json.dump({}, f, indent = 4)

    def load_file(self):
        with open(self.file, 'r') as f:
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



    def _gen_table(self, files):
        table = Table(show_header=False, show_lines=True)
        table.add_column('File', style="bold cyan")

        for i in range(0, len(files)):
            if i==self.index:
                table.add_row(_file_name(files[i]), style="on blue")
            else: table.add_row(_file_name(files[i]))

        return table

