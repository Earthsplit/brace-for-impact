import numpy as np
from tcod.console import Console

from random import randint

import tile_types

class GameMap:
  def __init__(self, width: int, height: int):
    self.width = width
    self.height = height
    self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")
  
  def in_bounds(self, x: int, y: int) -> bool:
    # Return True if x and y are inside of the bounds of this map.
    return 0 <= x < self.width and 0 <= y < self.height
  
  def render(self, console: Console):
    console.rgb[0:self.width, 0:self.height] = self.tiles["dark"]