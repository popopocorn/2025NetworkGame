
from pico2d import *
import random

from background import *
from player import Player
import game_world
import game_framework
from timer import Timer
import play_mode_4 as next_mode
import game_data
import item_mode
from main_ui import Player_status

def handle_events():

    global player_jump, timer_event_time
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
    if curr_time - timer_event_time >= 2.0:
        timer.handle_events(player.get_player_location())
        timer_event_time = get_time()
    game_data.php = player.hp
    game_data.mhp = player.max_hp
    game_data.pmp = player.mp
    game_data.mmp = player.max_mp

def init():
    global player, timer, timer_event_time
    timer_event_time = 0
    player = Player(game_data.player_info[0], game_data.player_info[1], game_data.player_info[2], game_data.enhance)
    #player = Player()
    game_world.add_object(player, 2)
    timer = Timer()
    game_world.add_object(timer, 2)
    game_world.add_collision_pair("player:mob", player, timer)
    background = BlockGround()
    game_world.add_object(background, 0)
    platforms = [BlockPlatform(1020, 120), BlockPlatform(870, 170), BlockPlatform(720, 170), BlockPlatform(570, 170),
                 BlockPlatform(420, 170), BlockPlatform(270, 170), BlockPlatform(120, 120)]
    for platform in platforms:
        game_world.add_object(platform, 0)
    game_world.add_collision_pair("player:platform", player, None)
    for platform in platforms:
        game_world.add_collision_pair("player:platform", None, platform)
    game_world.add_collision_pair("skill:mob", timer, None)
    ui=Player_status()
    game_world.add_object(ui, 4)


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def finish():
    game_world.clear()
    game_data.player_info = [player.hp, player.mp, player.ad]

def update():
    game_world.update()
    game_world.handle_collisions()
    if item_mode.is_selected:
        game_framework.change_mode(next_mode)
        item_mode.is_selected = False

def pause():
    pass
def resume():
    pass