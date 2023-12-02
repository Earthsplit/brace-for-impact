import tcod.event

from actions import Action, BumpAction, EscapeAction

class EventHandler(tcod.event.EventDispatch[Action]):
  def ev_quit(self, event):
    raise SystemExit()
  
  def ev_keydown(self, event):
    action = None

    key = event.sym

    if key == tcod.event.KeySym.w:
      action = BumpAction(dx=0, dy=-1)
    elif key == tcod.event.KeySym.s:
      action = BumpAction(dx=0, dy=1)
    elif key == tcod.event.KeySym.a:
      action = BumpAction(dx=-1, dy=0)
    elif key == tcod.event.KeySym.d:
      action = BumpAction(dx=1, dy=0)

    elif key == tcod.event.KeySym.ESCAPE:
      action = EscapeAction()
      
    # No valid key was pressed
    return action