from pico2d import *
import random

from background import *
from main_ui import Player_status
from player import Player
import game_world
import game_framework
import play_mode_2 as next_mode
import config
import game_data
import main_ui
import network
import enemy

# Game object class here


def handle_events():

    global player_jump
    player_jump = player.get_jump()
    events = get_events()
    curr_time=get_time()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:

            config.debug_flag = not config.debug_flag
        elif event.type == SDL_KEYDOWN and event.key == SDLK_COMMA:
            config.volume-=2
        elif event.type == SDL_KEYDOWN and event.key == SDLK_PERIOD:
            config.volume+=2
        else:
            if event.type in(SDL_KEYDOWN, SDL_KEYUP):
                player.handle_event(event) #boy에게 event 전달
    game_data.php = player.hp
    game_data.mhp = player.max_hp
    game_data.pmp = player.mp
    game_data.mmp = player.max_mp

def init():
    global player
    player = Player()
    game_world.add_object(player, 2)
    background = Background1()
    game_world.add_object(background, 0)
    platforms = [Platform( 1020,120 ), Platform(870, 170),  Platform(720, 170),  Platform(570, 170),
                 Platform(420, 170), Platform(270, 170), Platform(120, 120)]
    for platform in platforms:
        game_world.add_object(platform, 0)
    game_world.add_collision_pair("player:platform", player, None)
    for platform in platforms:
        game_world.add_collision_pair("player:platform", None, platform)
    ui=Player_status()
    game_world.add_object(ui, 4)
    e = enemy.Enemy()
    game_world.add_object(e, 1)

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def finish():
    game_world.clear()
    game_data.player_info=[player.hp, player.mp, player.ad]

def update():
    game_world.update()
    game_world.handle_collisions()
    update_info()


def send_info():        # 신태양 11/06
    network.send_info()


def pause():
    pass
def resume():
    pass

def update_info():
    global player
    network.recv_buf_lock.acquire()
    buf = network.recv_buffer.update_info[:]
    network.recv_buffer.update_info.clear()
    network.recv_buf_lock.release()
    for a in buf:
        player.hp =  a.my_char_hp
        a.time_remaining
        for j in range(2):
            a.other_chars[j]
        for i in range(4):
            a.skills[i]
        
    