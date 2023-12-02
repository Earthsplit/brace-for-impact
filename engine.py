from __future__ import annotations
from typing import TYPE_CHECKING

from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov

from random import randint

from input_handlers import EventHandler

if TYPE_CHECKING:
  from entity import Entity
  from game_map import GameMap
  
class Engine:
  game_map: GameMap
  
  def __init__(self, player: Entity):
    self.event_handler: EventHandler = EventHandler(self)
    self.player = player
    
  def handle_enemy_turns(self):
    for entity in self.game_map.entities - {self.player}:
      print(f'The {entity.name} wonders when it will get to take a real turn.')

  def update_fov(self):
    # Recompute the visible area based on the players point of view.
    self.game_map.visible[:] = compute_fov(
      self.game_map.tiles["transparent"],
      (self.player.x, self.player.y),
      radius=8
    )
    # If a tile is "visible" it should be added to "explored".
    self.game_map.explored |= self.game_map.visible
  
  def render(self, console: Console, context: Context):
    self.game_map.render(console)

    context.present(console) # Render the console to the window and show it

    console.clear() # clear the console