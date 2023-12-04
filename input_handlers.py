from __future__ import annotations

from typing import Optional
from typing import Optional, TYPE_CHECKING

import tcod.event

from actions import Action, BumpAction, EscapeAction, WaitAction

if TYPE_CHECKING:
  from engine import Engine

MOVE_KEYS = {
  # Arrow keys.
  tcod.event.KeySym.w: (0, -1),
  tcod.event.KeySym.s: (0, 1),
  tcod.event.KeySym.a: (-1, 0),
  tcod.event.KeySym.d: (1, 0),
  tcod.event.KeySym.HOME: (-1, -1),
  tcod.event.KeySym.END: (-1, 1),
  tcod.event.KeySym.PAGEUP: (1, -1),
  tcod.event.KeySym.PAGEDOWN: (1, 1),
  # Numpad keys.
  tcod.event.KeySym.KP_1: (-1, 1),
  tcod.event.KeySym.KP_2: (0, 1),
  tcod.event.KeySym.KP_3: (1, 1),
  tcod.event.KeySym.KP_4: (-1, 0),
  tcod.event.KeySym.KP_6: (1, 0),
  tcod.event.KeySym.KP_7: (-1, -1),
  tcod.event.KeySym.KP_8: (0, -1),
  tcod.event.KeySym.KP_9: (1, -1),
  # Vi keys.
  tcod.event.KeySym.h: (-1, 0),
  tcod.event.KeySym.j: (0, 1),
  tcod.event.KeySym.k: (0, -1),
  tcod.event.KeySym.l: (1, 0),
  tcod.event.KeySym.y: (-1, -1),
  tcod.event.KeySym.u: (1, -1),
  tcod.event.KeySym.b: (-1, 1),
  tcod.event.KeySym.n: (1, 1),
}

WAIT_KEYS = {
  tcod.event.KeySym.PERIOD,
  tcod.event.KeySym.KP_5,
  tcod.event.KeySym.CLEAR,
}



class EventHandler(tcod.event.EventDispatch[Action]):
  def __init__ (self, engine: Engine):
    self.engine = engine
    
  def handle_events(self) -> None:
    raise NotImplementedError()

  def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
    raise SystemExit()
  
class MainGameEventHandler(EventHandler):    
  def handle_events(self):
    for event in tcod.event.wait():
      action = self.dispatch(event)
      
      if action is None:
        continue
      
      action.perform()
      
      self.engine.handle_enemy_turns()
      self.engine.update_fov() # Update the FOV before the players next action.
  
  def ev_keydown(self, event):
    action = None

    key = event.sym
    
    player = self.engine.player

    if key in MOVE_KEYS:
      dx, dy = MOVE_KEYS[key]
      action = BumpAction(player, dx, dy)
    elif key in WAIT_KEYS:
      action = WaitAction(player)
      
    # No valid key was pressed
    return action
  
class GameOverEventHandler(EventHandler):
  def handle_events(self):
    for event in tcod.event.wait():
      action = self.dispatch(event)
      
      if action is None:
        continue
      
      action.perform()
      
  def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
    action: Optional[Action] = None
    
    key = event.sym
    
    if key == tcod.event.KeySym.ESCAPE:
      action = EscapeAction(self.engine.player)
    
    # No valid key was pressed  
    return action