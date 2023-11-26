class Action:
  pass

# subclasses of Action
class EscapeAction(Action):
  pass

class MovementAction(Action):
  def __init__(self, dx: int, dy: int):
    super().__init__() # calling the constructor of the Action class

    self.dx = dx
    self.dy = dy