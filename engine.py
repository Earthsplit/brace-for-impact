from tcod.context import Context
from tcod.console import Console

from actions import EscapeAction, MovementAction
from entity import Entity
from input_handlers import EventHandler

class Engine:
  def __init__(self, entities, event_handler, player):
    self.entities = entities
    self.event_handler = event_handler
    self.player = player

  def handle_events(self, events):
    for event in events:
      action = self.event_handler.dispatch(event)

      if action is None:
        continue
          
      if isinstance(action, MovementAction):
        self.player.move(dx=action.dx, dy=action.dy)

      elif isinstance(action, EscapeAction):
        raise SystemExit()
  
  def render(self, console, context):
    for entity in self.entities:
      console.print(entity.x, entity.y, entity.char, entity.color)

    context.present(console) # Render the console to the window and show it

    console.clear() # clear the console