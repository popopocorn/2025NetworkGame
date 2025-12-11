from pico2d import *
import random


import game_world
import game_framework
import play_mode as next_mode
import logo_mode
import config
import game_data
import network
import main_ui
import threading

match_timer=0
def handle_events():
    pass
   

def init():   
    if 0 == network.connect():
        recv_thread = threading.Thread(target=network.start_game, daemon=True)
        recv_thread.start()
        ui = main_ui.matchUI()
        game_world.add_object(ui, 4)
    else :
        game_framework.change_mode(logo_mode)
    pass

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def finish():
    game_world.clear()

def update():
    global match_timer

    game_world.update()
    game_world.handle_collisions()

    if network.game_start:

        # 프레임 시간 누적
        match_timer += game_framework.frame_time  

        # 3초 경과 시 씬 전환
        if match_timer >= 3.0:
            game_framework.change_mode(next_mode)
        

def pause():
    pass

def resume():
    pass

def send_info():
    pass