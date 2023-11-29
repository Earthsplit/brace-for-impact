import tcod

from input_handlers import EventHandler
from entity import Entity

from engine import Engine

from random import randint
from procgen import generate_dungeon

def main():
  screen_width = 80
  screen_height = 50

  map_width = 80
  map_height = 45

  room_max_size = 10
  room_min_size = 6
  max_rooms = 30 

  tileset = tcod.tileset.load_tilesheet(
    "data/Alloy_curses_12x12.png", columns=16, rows=16, charmap=tcod.tileset.CHARMAP_CP437
  )

  event_handler = EventHandler()

  player = Entity(int(screen_width / 2), int(screen_height / 2), "@", (255, 255, 255))
  crab = Entity(int(randint(0, 80)), int(randint(0, 45)), "c", (177, 255, 38))

  entities = { crab, player }

  game_map = generate_dungeon(max_rooms, room_min_size, room_max_size, map_width, map_height, player)

  engine = Engine(entities=entities, event_handler=event_handler, game_map=game_map, player=player)

  with tcod.context.new_terminal(screen_width, screen_height, tileset=tileset, title="brace for impact") as context:
    root_console = tcod.console.Console(screen_width, screen_height, order="F")
    while True:  # Main loop
      engine.render(console=root_console, context=context)

      engine.handle_events(tcod.event.wait())

if __name__ == "__main__":
  main()