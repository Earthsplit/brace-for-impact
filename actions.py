from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
  from engine import Engine
  from entity import Actor, Entity
  
class Action:
  def __init__(self, entity: Actor):
    super().__init__()
    self.entity = entity
    
  @property
  def engine(self) -> Engine:
    #Return the engine this action belongs to.
    return self.entity.gamemap.engine
  
  """Perform this action with the objects needed to determine its scope.

  `self.engine` is the scope this action is being performed in.

  `self.entity` is the object performing the action.

  This method must be overridden by Action subclasses.
  """
  def perform(self):
    raise NotImplementedError()

# subclasses of Action
class EscapeAction(Action):
  def perform(self):
    raise SystemExit()
  
class ActionWithDirection(Action):
  def __init__(self, entity: Actor, dx: int, dy: int):
    super().__init__(entity)
    
    self.dx = dx
    self.dy = dy
  
  @property
  def dest_xy(self) -> Tuple[int, int]:
    return self.entity.x + self.dx, self.entity.y + self.dy
  
  @property
  def blocking_entity(self) -> Optional[Entity]:
    return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)
  
  @property
  def target_actor(self) -> Optional[Actor]:
    # Return the actor at this actions destination
    return self.engine.game_map.get_actor_at_location(*self.dest_xy)
  
  def perform(self):
    raise NotImplementedError()
    
class MeleeAction(ActionWithDirection):
  def perform(self):
    target = self.target_actor
    if not target:
      return
    
    damage = self.entity.fighter.power - target.fighter.defense
    
    attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"
    if damage > 0:
      print(f"{attack_desc} for {damage} hit points.")
      target.fighter.hp -= damage
    else:
      print(f"{attack_desc} but does no damage.")
    
class BumpAction(ActionWithDirection):
  def perform(self):
    
    if self.target_actor:
      return MeleeAction(self.entity, self.dx, self.dy).perform()
    else:
      return MovementAction(self.entity, self.dx, self.dy).perform()

class MovementAction(ActionWithDirection):
  def perform(self):
    dest_x, dest_y = self.dest_xy

    if not self.engine.game_map.in_bounds(dest_x, dest_y):
      return
    if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
      return
    if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
      return # Destination is blocked by an entity.
    
    self.entity.move(self.dx, self.dy)
    
class WaitAction(Action):
  def perform(self):
    pass