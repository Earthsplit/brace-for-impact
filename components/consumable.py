from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import actions
import color
import components.inventory
from components.base_component import BaseComponent
from exceptions import Impossible

if TYPE_CHECKING:
  from entity import Actor, Item
  
class Consumable(BaseComponent):
  parent: Item
  
  def get_action(self, consumer: Actor) -> Optional[actions.Action]:
    # try to return the action fro this item
    return actions.ItemAction(consumer, self.parent)
  
  def activate(self, action: actions.ItemAction):
    """Invoke this items ability.
    `action` is the context for this activation."""
    raise NotImplementedError()
  
  def consume(self):
    # remove the consumed item from inventory
    entity = self.parent
    inventory = entity.parent
    if isinstance(inventory, components.inventory.Inventory):
      inventory.items.remove(entity)

class HealingConsumable(Consumable):
  def __init__(self, amount: int):
    self.amout = amount
    
  def activate(self, action: actions.ItemAction):
    consumer = action.entity
    amount_recovered = consumer.fighter.heal(self.amout)
    
    if amount_recovered > 0:
      self.engine.message_log.add_message(
        f"You consume the {self.parent.name}, and recover {amount_recovered} HP!",
        color.health_recovered,
      )
      self.consume()
    else:
      raise Impossible("Your health is already full.")