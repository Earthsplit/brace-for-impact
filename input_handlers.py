from __future__ import annotations

from typing import Optional
from typing import Optional, TYPE_CHECKING
import tcod

from tcod import libtcodpy
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

CURSOR_Y_KEYS = {
  tcod.event.KeySym.UP: -1,
  tcod.event.KeySym.DOWN: 1,
  tcod.event.KeySym.PAGEUP: -10,
  tcod.event.KeySym.PAGEDOWN: 10,
}

class EventHandler(tcod.event.EventDispatch[Action]):
  def __init__ (self, engine: Engine):
    self.engine = engine
    
  def handle_events(self, context: tcod.context.Context):
    for event in tcod.event.wait():
      context.convert_event(event)
      self.dispatch(event)
    
  def ev_mousemotion(self, event: tcod.event.MouseMotion):
    if self.engine.game_map.in_bounds(event.tile.x, event.tile.y):
      self.engine.mouse_location = event.tile.x, event.tile.y

  def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
    raise SystemExit()
  
  def on_render(self, console: tcod.Console):
    self.engine.render(console)
  
class MainGameEventHandler(EventHandler):    
  def handle_events(self, context: tcod.context.Context):
    for event in tcod.event.wait():
      context.convert_event(event)
      
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
    elif key == tcod.event.KeySym.q:
      self.engine.event_handler = HistoryViewer(self.engine)
      
    # No valid key was pressed
    return action
  
class GameOverEventHandler(EventHandler):
  def handle_events(self, context: tcod.context.Context):
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

class HistoryViewer(EventHandler):
  # Print the history on a larger window which can be navigated.

  def __init__(self, engine: Engine):
    super().__init__(engine)
    self.log_length = len(engine.message_log.messages)
    self.cursor = self.log_length - 1

  def on_render(self, console: tcod.Console) -> None:
    super().on_render(console)  # Draw the main state as the background.

    log_console = tcod.console.Console(console.width - 6, console.height - 6)

    # Draw a frame with a custom banner title.
    log_console.draw_frame(0, 0, log_console.width, log_console.height)
    log_console.print_box(
      0, 0, log_console.width, 1, "┤Message history├", alignment=libtcodpy.CENTER
    )

    # Render the message log using the cursor parameter.
    self.engine.message_log.render_messages(
      log_console,
      1,
      1,
      log_console.width - 2,
      log_console.height - 2,
      self.engine.message_log.messages[: self.cursor + 1],
    )
    log_console.blit(console, 3, 3)

  def ev_keydown(self, event: tcod.event.KeyDown) -> None:
    # Fancy conditional movement to make it feel right.
    if event.sym in CURSOR_Y_KEYS:
      adjust = CURSOR_Y_KEYS[event.sym]
      if adjust < 0 and self.cursor == 0:
        # Only move from the top to the bottom when you're on the edge.
        self.cursor = self.log_length - 1
      elif adjust > 0 and self.cursor == self.log_length - 1:
        # Same with bottom to top movement.
        self.cursor = 0
      else:
        # Otherwise move while staying clamped to the bounds of the history log.
        self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
    elif event.sym == tcod.event.KeySym.HOME:
      self.cursor = 0  # Move directly to the top message.
    elif event.sym == tcod.event.KeySym.END:
      self.cursor = self.log_length - 1  # Move directly to the last message.
    else:  # Any other key moves back to the main game state.
      self.engine.event_handler = MainGameEventHandler(self.engine)