from typing import Set, Iterable, Any

from threading import Timer
from tcod.context import Context
from tcod.console import Console

from random import randint

from entity import Entity
from game_map import GameMap
from input_handlers import EventHandler
class Engine:
  def __init__(self, entities: Set[Entity], event_handler: EventHandler, game_map: GameMap, player: Entity):
    self.entities = entities
    self.event_handler = event_handler
    self.game_map = game_map
    self.player = player

  def handle_events(self, events):
    for event in events:
      action = self.event_handler.dispatch(event)

      if action is None:
        continue

      action.perform(self, self.player)
  
  def render(self, console: Console, context: Context):
    self.game_map.render(console)

    for entity in self.entities:
      console.print(entity.x, entity.y, entity.char, entity.color)

    context.present(console) # Render the console to the window and show it

    console.clear() # clear the console