import numpy as np
from tcod.console import Console

from random import randint

import tile_types

class GameMap:
  def __init__(self, width: int, height: int):
    self.width = width
    self.height = height
    self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")

    self.visible = np.full((width, height), fill_value=False, order="F") # Tiles the player can currently see
    self.explored = np.full((width, height), fill_value=False, order="F") # Tiles the player has seen before
  
  def in_bounds(self, x: int, y: int) -> bool:
    # Return True if x and y are inside of the bounds of this map.
    return 0 <= x < self.width and 0 <= y < self.height
  
  def render(self, console: Console):
    console.rgb[0:self.width, 0:self.height] = np.select(
      condlist=[self.visible, self.explored],
      choicelist=[self.tiles["light"], self.tiles["dark"]],
      default=tile_types.SHROUD
    )