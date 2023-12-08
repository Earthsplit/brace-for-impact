from typing import Iterable, List, Reversible, Tuple
import textwrap

import tcod

import color

class Message:
  def __init__(self, text: str, fg: Tuple[int, int, int]):
    self.plain_text = text
    self.fg = fg
    self.count = 1
    
  @property
  def full_text(self) -> str:
    if self.count > 1:
      return f'{self.plain_text} (x{self.count})' # Repeats the same text
    return self.plain_text
  
class MessageLog:
  def __init__(self):
    self.messages: List[Message] = []
    
  def add_message(
    self, text: str, fg: Tuple[int, int, int] = color.white, *, stack: bool = True
  ):
    """Add a message to this log.
    `text` is the message text, `fg` is the text color.
    If `stack` is True then the message can stack with a previous message
    of the same text.
    """
    
    if stack and self.messages and text == self.messages[-1].plain_text:
      self.messages[-1].count += 1
    else:
      self.messages.append(Message(text, fg))
    
  def render(self, console: tcod.console.Console, x: int, y: int, width: int, height: int):
    self.render_messages(console, x, y, width, height, self.messages)
  
  @staticmethod
  def wrap(string: str, width: int) -> Iterable[str]:
    # Return a wrapped text msg
    for line in string.splitlines(): # handle new lines in messages
      yield from textwrap.wrap(
        line, width, expand_tabs=True
      )
  
  @classmethod
  def render_messages(
    cls,
    console: tcod.console.Console,
    x: int,
    y: int,
    width: int,
    height: int,
    messages: Reversible[Message]
  ):
    """Render the messages provided.
    The `messages` are rendered starting at the last message and working
    backwards.
    """
    y_offset = height - 1
    
    for message in reversed(messages):
      for line in reversed(cls.wrap(message.full_text, width)):
        console.print(x=x, y=y+y_offset, string=line, fg=message.fg)
        y_offset -= 1
        if y_offset < 0:
          return # No more space to print messages.