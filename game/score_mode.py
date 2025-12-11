from pico2d import *
import random


import game_world
import game_framework
import play_mode as next_mode
import config
import game_data
import network
import main_ui


def handle_events():
    pass
   

def init():
    global ui
    ui = main_ui.scoreUI()
    game_world.add_object(ui, 4)
    network.closesocket()

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def finish():
    game_world.clear()

def update():
    game_world.update()
    game_world.handle_collisions()

def send_info():
    pass

def pause():
    pass

def resume():
    pass