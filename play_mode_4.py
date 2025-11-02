
from pico2d import *
import random

from background import *
from player import Player
from junior_barlog import JuniorBarlog
import game_world
import game_framework
import config
import game_data
from main_ui import Player_status
#import end_mode as next_mode
# Game object class here


def handle_events():

    global player_jump, barlog_event_time
    player_jump = player.get_jump()
    events = get_events()
    curr_time=get_time()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_i:
            pass
        elif event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:

            config.debug_flag = not config.debug_flag
        elif event.type == SDL_KEYDOWN and event.key == SDLK_COMMA:
            config.volume-=2
        elif event.type == SDL_KEYDOWN and event.key == SDLK_PERIOD:
            config.volume+=2
        else:
            if event.type in(SDL_KEYDOWN, SDL_KEYUP):
                player.handle_event(event) #boy에게 event 전달
    if curr_time - barlog_event_time >= 2.0:
        barlog.handle_events(player.get_player_location())
        barlog_event_time = get_time()
    game_data.php = player.hp
    game_data.mhp = player.max_hp
    game_data.pmp = player.mp
    game_data.mmp = player.max_mp

def init():
    global player, barlog, barlog_event_time
    player = Player(game_data.player_info[0], game_data.player_info[1], game_data.player_info[2], game_data.enhance)
    #player = Player(1000, 1000, 10000)

    game_world.add_object(player, 2)
    barlog_event_time = 0
    barlog = JuniorBarlog()
    game_world.add_object(barlog, 2)
    game_world.add_collision_pair("player:mob", player, barlog)
    background = CaveGround()
    game_world.add_object(background, 0)
    platforms = [CavePlatform(1020, 120), CavePlatform(870, 170), CavePlatform(720, 170), CavePlatform(570, 170),
                 CavePlatform(420, 170), CavePlatform(270, 170), CavePlatform(120, 120)]

    for platform in platforms:
        game_world.add_object(platform, 0)
    game_world.add_collision_pair("player:platform", player, None)
    for platform in platforms:
        game_world.add_collision_pair("player:platform", None, platform)
    game_world.add_collision_pair("skill:mob", barlog, None)
    ui=Player_status()
    game_world.add_object(ui, 4)



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