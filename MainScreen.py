from openai import OpenAI, OpenAIError

from rich.rule import Rule

import readchar

from datetime import datetime

from NewChat import load_recent
from SaveScreen import SaveScreen
import UserSettings

from conversationTree import *
from Screen import Screen, _clear_terminal, _get_input
import sys

RENDERED_MSGS = 5

class MainScreen(Screen):
    """The main screen, where conversations with LLMs take place."""

    def __init__(self, scr: "Screen" = None):
        if not scr:
            self.cur, self.messages, self.file = load_recent()
            self.settings = UserSettings.load_settings()
            self._connect()
        super().__init__(scr)
    
    def _update_renderables(self, ctrl: bool = True):
        num_msgs = RENDERED_MSGS
        cur_it = self.cur
        renderables = []
        while num_msgs and cur_it:
            if cur_it.role != "system":
                renderables.append(cur_it.render())
            cur_it = cur_it.prev
            num_msgs -= 1
        renderables.reverse()
        renderables.append(Rule(style="bold white"))
        if ctrl:
            with open("ctrl.md", "r", encoding="utf-8") as file:
                renderables.append(Markdown(file.read()))
            renderables.append(Rule(style="bold white"))
        self.renderables = renderables

    def _generate(self):
        """Stream in a response via the chosen API. This does multiple things:
        - Send a request to the API.
        - Print tokens as the stream in.
        - If there is an error: Print that instead.
        - Convert the streamed content to a message node placed in the conversation tree, and properly render markdown once finished."""
        try:
            stream = self.client.chat.completions.create(
                model=self.settings['Model'],
                messages = self.messages,
                stream = True,
                temperature = self.settings['Temperature'],
                frequency_penalty = self.settings['FrequencyPenalty'],
                presence_penalty = self.settings['PresencePenalty']
            )

            buffer = ""

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    sys.stdout.write(content)
                    sys.stdout.flush()
                    buffer += content
        
        except OpenAIError as e:
            buffer = str(e)

        gen_msg = Msg_Node(self.cur, "assistant", buffer, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), len(self.messages))
        self.cur = gen_msg
        self.messages.append(gen_msg.to_msg())


    def handle_input(self, key):

        if key == 'q':
            return SaveScreen(self, cont=False)

        elif key == 'c':
            return SaveScreen(self)

        elif key == 'e':
            self._edit()
        
        elif key == 's':
            return UserSettings.SettingsScreen(self)
            

        elif key == readchar.key.UP:
            if self.cur.prev:
                self.cur = self.cur.prev
                self.messages.pop()
                self._update_renderables()
                self._render()

        elif key == readchar.key.DOWN:
            if self.cur.next:
                self.cur=self.cur.next[0]
                self.messages.append(self.cur.to_msg())
                self._update_renderables()
                self._render()

        elif key == readchar.key.RIGHT:
            if self.cur.prev:
                sib = self.cur.prev.next
                id = self.cur.index-1
                if id+1 < len(sib):
                    self.cur = sib[id+1]
                    self.messages.pop()
                    self.messages.append(self.cur.to_msg())
                    self._update_renderables()
                    self._render()
                else:
                    self.cur = self.cur.prev
                    self.messages.pop()
                    _clear_terminal()
                    self._generate()
                    self._update_renderables()
                    self._render()


        elif key == readchar.key.LEFT:
            if self.cur.prev:
                sib = self.cur.prev.next
                id = self.cur.index-1
                self.cur = sib[max(0, id-1)]
                self.messages.pop()
                self.messages.append(self.cur.to_msg())
                self._update_renderables()
                self._render()

        elif key == readchar.key.ENTER:
            self._type_msg()
        
        return self

    def _edit(self):
        """Lets users edit the current message. If they press escape, restore the previous state. If the edited message was one of theirs, also generate a response."""
        if self.cur.prev:
            prev_text = self.cur.content
            input = _get_input(default=prev_text)
            if input == None:
                self._render()
                return
            edited=Msg_Node(self.cur.prev, self.cur.role, input, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.cur.depth)
            self.cur=edited
            self.messages.pop()
            self.messages.append(self.cur.to_msg())
            if self.cur.role=="user":
                self._generate()
                self._update_renderables()
                self._render()
            else:
                self.render_cur()
    
    def _type_msg(self):
        """Lets users type a new message, stores it in the conversation tree, and generates a response."""
        input = _get_input()
        if input == None:
            self._render()
            return
        usr_msg = Msg_Node(self.cur, "user", input, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), len(self.messages))
        self.cur = usr_msg
        self.messages.append(usr_msg.to_msg())
        self._generate()
        self._update_renderables()
        self._render()


