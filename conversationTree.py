from rich.markdown import Markdown
from rich.text import Text
from rich.console import Group
from rich.rule import Rule
import uuid

def deserialize(data, cur_id):
    cur = None
    node = Msg_Node(
        prev = None,
        role=data['role'],
        content=data['content'],
        time=data['time'],
        depth=data['depth'],
        id = data['id'],
        index = data['index']
    )
    if node.id == cur_id: cur = node

    for nxt in data['next']: 
        child, new_cur= deserialize(nxt, cur_id)
        node.add_child(child)
        if new_cur: cur = new_cur

    return node, cur


class Msg_Node:

    def __init__(self, prev, role, content, time, depth, id = None, index = None):
        self.prev = prev
        if prev:
            prev.next.append(self)
            self.index = len(prev.next)
        else: self.index=1
        if index: self.index = index
        self.next = []
        self.role = role
        self.content = content
        self.time = time
        self.depth = depth
        if id:
            self.id = id
        else:
            self.id=str(uuid.uuid4())

    def get_counts(self):
        if self.prev:
            return len(self.prev.next), self.index
        else: return 1,1
    
    def to_msg(self):
        return {"role": self.role, "content": self.content}
    
    def add_child(self, child):
        self.next.append(child)
        child.prev = self

    def render(self):
        total, this = self.get_counts()

        header = f"{self.time} | {self.depth} | {this}/{total}"

        if self.role == "assistant":
            header_style = "bold red"
        elif self.role == "user":
            header_style = "bold green"
        else:
            header_style = "bold blue"
        styled_header= Text(header, style = header_style, justify="center")
        return Group(Rule(styled_header, style = header_style), Markdown(self.content))
    
    def serialize(self, cur):
        serialized = {
            'cur_id': cur.id,
            'messages': self.serialize_rec()
        }
        return serialized
    
    def serialize_rec(self):
        serialized = {
            'index': self.index,
            'role': self.role,
            'content': self.content,
            'time': self.time,
            'depth': self.depth,
            'id': self.id,
            'next': [child.serialize_rec() for child in self.next],
        }
        return serialized
