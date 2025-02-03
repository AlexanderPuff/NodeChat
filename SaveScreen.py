import json
import os

import readchar
from NewChat import CHATS_PATH, ChatLoader
from Screen import Screen, _clear_terminal, _get_input
from datetime import datetime

class SaveScreen(Screen):
    def __init__(self, scr: "Screen", cont: bool = True):
        super().__init__(scr)
        self.continue_after = cont
    
    def _update_renderables(self):
        self.renderables = ["Do you want to save the previous chat? \[y/n]"]
    
    def handle_input(self, key):
        if key == 'y' or key == readchar.key.ENTER:
            return self.save()
        elif key == 'n':
            return ChatLoader(self) if self.continue_after else None
        
    def save(self):
        root = self.cur
        root2 = root
        while root:
            root2 = root
            root = root.prev
        chat = root2.serialize(self.cur)
        
        if self.file:
            with open(self.file, 'w') as f:
                json.dump(chat, f, indent=4)
            return ChatLoader(self) if self.continue_after else None
        else:
            _clear_terminal()
            time = datetime.now()
            name = time.strftime("%Y-%m-%d_%H-%M-%S")
            input = _get_input(prompt_text="Name for chat file: ", default= name)
            if input:
                path = os.path.join(CHATS_PATH, (input + '.json'))
                with open(path, 'w') as f:
                    json.dump(chat, f, indent=4)
                return ChatLoader(self) if self.continue_after else None
            else:
                self._update_renderables()
                self._render()
                return self
