from pico2d import *
import random


import game_world
import game_framework
import play_mode as next_mode
import config
import game_data
import network
import main_ui
import title_mode

def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.change_mode(title_mode)

   

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