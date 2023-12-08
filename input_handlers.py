from __future__ import annotations

from typing import Optional
from typing import Optional, TYPE_CHECKING
import tcod

from tcod import libtcodpy
import tcod.event

import actions
from actions import Action, BumpAction, WaitAction, PickupAction
import color
from entity import Item
import exceptions

if TYPE_CHECKING:
  from engine import Engine
  from entity import Item

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
    
  def handle_events(self, event: tcod.event.Event):
    self.handle_action(self.dispatch(event))
  
  def handle_action(self, action: tcod.event.Event):
    """Handle actions returned from event methods.
    Returns True if the action will advance a turn."""
    
    if action is None:
      return False 
    
    try:
      action.perform()
    except exceptions.Impossible as exc:
      self.engine.message_log.add_message(exc.args[0], color.impossible)
      return False # Skip enemy turn on exceptions.

    self.engine.handle_enemy_turns()
    
    self.engine.update_fov()
    return True
    
  def ev_mousemotion(self, event: tcod.event.MouseMotion):
    if self.engine.game_map.in_bounds(event.tile.x, event.tile.y):
      self.engine.mouse_location = event.tile.x, event.tile.y

  def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
    raise SystemExit()
  
  def on_render(self, console: tcod.Console):
    self.engine.render(console)
    
class AskUserEventHandler(EventHandler):
  """Handles user input for actions which require special input."""
  def handle_action(self, action: Optional[Action]) -> bool:
    """Return to the main event handler when a valid action was performed."""
    if super().handle_action(action):
      self.engine.event_handler = MainGameEventHandler(self.engine)
      return True
    return False

  def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
    """By default any key exits this input handler."""
    if event.sym in {  # Ignore modifier keys.
      tcod.event.KeySym.LSHIFT,
      tcod.event.KeySym.RSHIFT,
      tcod.event.KeySym.LCTRL,
      tcod.event.KeySym.RCTRL,
      tcod.event.KeySym.LALT,
      tcod.event.KeySym.RALT,
    }:
      return None
    return self.on_exit()

  def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[Action]:
      """By default any mouse click exits this input handler."""
      return self.on_exit()

  def on_exit(self) -> Optional[Action]:
      """Called when the user is trying to exit or cancel an action.

      By default this returns to the main event handler.
      """
      self.engine.event_handler = MainGameEventHandler(self.engine)
      return None
  
class MainGameEventHandler(EventHandler):    
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
    elif key == tcod.event.KeySym.g:
      action = PickupAction(player)
    elif key == tcod.event.KeySym.i:
      self.engine.event_handler = InventoryActivateHandler(self.engine)
    elif key == tcod.event.KeySym.o:
      self.engine.event_handler = InventoryDropHandler(self.engine)
      
    # No valid key was pressed
    return action
  
class InventoryEventHandler(AskUserEventHandler):
  """This handler lets the user select an item.
  What happens then depends on the subclass."""
  
  TITLE = '<missing title>'
  
  def on_render(self, console: tcod.console.Console):
    """Render an inventory menu, which displays the items in the inventory, and the letter to select them.
    Will move to a different position based on where the player is located, so the player can always see where
    they are.
    """
    super().on_render(console)
    number_of_items_in_inventory = len(self.engine.player.inventory.items)
    
    height = number_of_items_in_inventory + 2
    
    if height <= 3:
      height = 3
      
    if self.engine.player.x <= 30:
      x = 40
    else:
      x = 0
    
    y = 0
    
    width = len(self.TITLE) + 4
    
    console.draw_frame(x=x, y=y, width=width, height=height, title=self.TITLE, clear=True, fg=(255, 255, 255), bg=(0, 0, 0))
    
    if number_of_items_in_inventory > 0:
      for i, item in enumerate(self.engine.player.inventory.items):
        item_key = chr(ord('a') + i)
        console.print(x + 1, y + i + 1, f"({item_key}) {item.name}")
    else:
      console.print(x + 1, y + 1, '(Empty)')
  
  def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
    player = self.engine.player
    key = event.sym
    index = key - tcod.event.KeySym.a
    
    if 0 <= index <= 26:
      try:
        selected_item = player.inventory.items[index]
      except IndexError:
        self.engine.message_log.add_message('Invalid entry', color.invalid)
        return None
      return self.on_item_selected(selected_item)
    return super().ev_keydown(event)
  
  def on_item_selected(self, item: Item) -> Optional[Action]:
    # Called when the user selects a valid item.
    raise NotImplementedError()
  
class InventoryActivateHandler(InventoryEventHandler):
  TITLE = 'Select an item to use'
  
  def on_item_selected(self, item: Item) -> Optional[Action]:
    return item.consumable.get_action(self.engine.player)  
  
class InventoryDropHandler(InventoryEventHandler):
  # handle dropping an inventory item
  
  TITLE = 'Select an item to drop'
  
  def on_item_selected(self, item: Item) -> Optional[Action]:
    # drop this item
    return actions.DropItem(self.engine.player, item)
  
class GameOverEventHandler(EventHandler):
  def ev_keydow(self, event: tcod.event.KeyDown):
    if event.sym == tcod.event.KeySym.ESCAPE:
      raise SystemExit()

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