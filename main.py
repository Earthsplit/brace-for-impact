import tcod
import copy
import traceback

import entity_factories
import color
from engine import Engine
from procgen import generate_dungeon

def main():
  screen_width = 80
  screen_height = 50

  map_width = 80
  map_height = 43

  room_max_size = 10
  room_min_size = 6
  max_rooms = 30 
  
  max_monsters_per_room = 2
  max_items_per_room = 2

  tileset = tcod.tileset.load_tilesheet(
    "data/Alloy_curses_12x12.png", columns=16, rows=16, charmap=tcod.tileset.CHARMAP_CP437
  )

  player = copy.deepcopy(entity_factories.player)
  engine = Engine(player)

  engine.game_map = generate_dungeon(
    max_rooms,
    room_min_size,
    room_max_size,
    map_width,
    map_height,
    max_monsters_per_room,
    max_items_per_room, 
    engine
  )
  
  engine.update_fov()
  
  engine.message_log.add_message('Hello and welcome, adventurer, to yet another dungeon!', color.welcome_text)

  with tcod.context.new_terminal(screen_width, screen_height, tileset=tileset, title="brace for impact") as context:
    root_console = tcod.console.Console(screen_width, screen_height, order="F")
    while True:  # Main loop
      root_console.clear()
      engine.event_handler.on_render(console=root_console)
      context.present(root_console)
      
      try:
        for event in tcod.event.wait():
          context.convert_event(event)
          engine.event_handler.handle_events(event)
      except Exception: # handle exceptions in game
        traceback.print_exc() # print error to stderr
        # then print the error to the message log
        engine.message_log.add_message(traceback.format_exc(), color.error)

if __name__ == "__main__":
  main()