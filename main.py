import tcod

from input_handlers import EventHandler
from entity import Entity

from engine import Engine

def main():
  screen_width = 80
  screen_height = 50

  tileset = tcod.tileset.load_tilesheet(
    "data/Alloy_curses_12x12.png", columns=16, rows=16, charmap=tcod.tileset.CHARMAP_CP437
  )

  event_handler = EventHandler()

  player = Entity(int(screen_width / 2), int(screen_height / 2), "@", (255, 255, 255))
  npc = Entity(int(screen_width / 2 - 5), int(screen_height / 2), "@", (255, 100, 0))
  entities = { npc, player }

  engine = Engine(entities, event_handler, player)

  with tcod.context.new_terminal(screen_width, screen_height, tileset=tileset, title="brace for impact") as context:
    root_console = tcod.console.Console(screen_width, screen_height, order="F")
    while True:  # Main loop
      engine.render(console=root_console, context=context)

      engine.handle_events(tcod.event.wait())

if __name__ == "__main__":
  main()