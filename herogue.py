from pico2d import *
import logo_mode as start_mode
import game_framework



open_canvas(int(1600/1.5),int(900/1.2))
game_framework.run(start_mode)
close_canvas()
