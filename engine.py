from typing import Set, Iterable, Any

from threading import Timer
from tcod.context import Context
from tcod.console import Console

from random import randint

from entity import Entity
from game_map import GameMap
from input_handlers import EventHandler
class Engine:
  def __init__(self, entities: Set[Entity], event_handler: EventHandler, game_map: GameMap, player: Entity, crab: Entity):
    self.entities = entities
    self.event_handler = event_handler
    self.game_map = game_map
    self.player = player
    self.crab = crab
    self.crab_moving_timer = Timer(2.0, self.move_crab)  # Set initial timer for 2 seconds
    self.crab_moving_timer.start()

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

    self.crabMovingTime = 10

    context.present(console) # Render the console to the window and show it

    console.clear() # clear the console

  def move_crab(self):
    # Move the crab entity (example: move right)
    self.crab.x += 1
    self.crab_moving_timer = Timer(1.0, self.move_crab)  # Set timer for the next movement
    self.crab_moving_timer.start()