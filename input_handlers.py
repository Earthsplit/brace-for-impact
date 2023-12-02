from __future__ import annotations

from typing import Optional
from typing import Optional, TYPE_CHECKING

import tcod.event

from actions import Action, BumpAction, EscapeAction

if TYPE_CHECKING:
  from engine import Engine

class EventHandler(tcod.event.EventDispatch[Action]):
  def __init__ (self, engine: Engine):
    self.engine = engine
    
  def handle_events(self):
    for event in tcod.event.wait():
      action = self.dispatch(event)
      
      if action is None:
        continue
      
      action.perform()
      
      self.engine.handle_enemy_turns()
      self.engine.update_fov() # Update the FOV before the players next action.
  
  def ev_quit(self, event):
    raise SystemExit()
  
  def ev_keydown(self, event):
    action = None

    key = event.sym
    
    player = self.engine.player

    if key == tcod.event.KeySym.w:
      action = BumpAction(player, dx=0, dy=-1)
    elif key == tcod.event.KeySym.s:
      action = BumpAction(player, dx=0, dy=1)
    elif key == tcod.event.KeySym.a:
      action = BumpAction(player, dx=-1, dy=0)
    elif key == tcod.event.KeySym.d:
      action = BumpAction(player, dx=1, dy=0)

    elif key == tcod.event.KeySym.ESCAPE:
      action = EscapeAction(player)
      
    # No valid key was pressed
    return action