from pico2d import *
import random


import game_world
import game_framework
import play_mode as next_mode
import config
import game_data
import network


def handle_events():
    pass
   

def init():
    pass

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def finish():
    game_world.clear()

def update():
    game_world.update()
    game_world.handle_collisions()

def pause():
    pass

def resume():
    pass