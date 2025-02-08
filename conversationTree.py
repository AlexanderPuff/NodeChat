from rich.markdown import Markdown
from rich.text import Text
from rich.console import Group
from rich.rule import Rule
import uuid

def deserialize(data: dict, cur_id: str):
    """Recursively converts a dicitonary into a doubly-linked tree of conversation nodes.

    Args:
    data: A recursive dict holding the chat to be loaded.
    cur_id: The unique ID of the message which will become the current one.

    Returns:
    - The root of the tree.
    - The message node corresponding to the current message, or None if the message with cur_id is not (yet) found.
    """
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
    """A node in the doubly linked conversation tree."""

    def __init__(self, prev: "Msg_Node", role: str, content: str, time:str, depth:int, id = None, index = None):
        """Constructs a new message node.
        
        Args:
        - prev: The parent of this node in the tree.
        - role: The author of this message (System, User, or Assistant).
        - content: The actual message text.
        - time: The time the message was sent.
        - depth: The distance to the root.
        - id: The unique ID of this message. If left blank, a new one is generated.
        - index: The position in the list of children of this node's parent. If left blank and a parent is provided, calculate this automatically."""
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
        """Returns both the amount of children self's parent has as well as self's position among them. If there is no parent, return 1, 1."""
        if self.prev:
            return len(self.prev.next), self.index
        else: return 1,1
    
    def to_msg(self):
        """Returns a dictionary containing self's role and content."""
        return {"role": self.role, "content": self.content}
    
    def add_child(self, child):
        """Appends a child to this node."""
        self.next.append(child)
        child.prev = self

    def render(self):
        """Returns a nicely formatted renderable of this node. This renderable contains basic info (time, depth, index) of this node, colorring indicating the role, and the message itself as markdown."""
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
    
    def serialize(self, cur:str):
        """For saving to .json files.

        Args:
        cur: The unique ID of the message that will be treated as current.
        
        Returns:
        A dictionary holding the current ID and the conversation tree with this as root (recursively)."""
        serialized = {
            'cur_id': cur.id,
            'messages': self.serialize_rec()
        }
        return serialized
    
    def serialize_rec(self):
        """The recursive part of the serialize procedure."""
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
