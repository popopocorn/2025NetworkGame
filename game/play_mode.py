from pico2d import *
import random

from background import *
from game_data import remaining_time
from main_ui import Player_status, RemainingTimeUI
from player import Player
import game_world
import game_framework
import config
import game_data
import main_ui
import network
import enemy
from skill import *
import threading
import score_mode as next_mode

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
    recv_thread = threading.Thread(target=network.client_recv_thread, daemon=True)
    recv_thread.start()
    global player
    player = Player()
    game_world.add_object(player, 2)
    background = Background1()
    game_world.add_object(background, 0)
    # 기준 플랫폼 (아래층)
    base_x_positions = [1020, 870, 720, 570, 420, 270, 120]
    base_y = 120

    platforms = []

    layers = 4              # 총 층 수
    y_gap = 80              # 층 간 y 차이 (조금씩만 높이기)
    shift_amount = 50       # 층마다 좌우 시프트량

    for i in range(layers):
        y = base_y + (layers - 1 - i) * y_gap    # 위층부터 생성

        # 층마다 좌 → 우 → 좌 → 우로 엇갈리게 시프트
        if i % 2 == 0:
            shift = shift_amount
        else:
            shift = -shift_amount

        for x in base_x_positions:
            platforms.append(Platform(x + shift, y))


    for platform in platforms:
        game_world.add_object(platform, 0)
    game_world.add_collision_pair("player:platform", player, None)
    for platform in platforms:
        game_world.add_collision_pair("player:platform", None, platform)
    ui=Player_status()
    game_world.add_object(ui, 4)
    timeui = RemainingTimeUI()
    game_world.add_object(timeui, 4)
    e = enemy.Enemy(100)
    game_world.add_object(e, 1)
    e1 = enemy.Enemy()
    game_world.add_object(e1, 1)

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
    if network.game_start == False:
        game_framework.change_mode(next_mode)


def send_info():        # 신태양 11/06
    network.send_info()


def pause():
    pass

def resume():
    pass

def update_info():
    global player
    local_recv_buffer = []

    with network.recv_buf_lock:
        local_recv_buffer, network.global_recv_buffer = network.global_recv_buffer, local_recv_buffer

    for a in local_recv_buffer:
        for i in range(4):
            match a.skills[i].skill_id:
                case 1:
                    skill = Aura_blade(a.skills[i].x, a.skills[i].y, a.skills[i].skill_direction, a.skills[i].skill_ad)
                    game_world.add_object(skill, 3)
                case 2:
                    skill = Brandish(a.skills[i].x, a.skills[i].y, a.skills[i].skill_direction, a.skills[i].skill_ad)
                    game_world.add_object(skill, 3)
                case _:
                    pass

    if len(local_recv_buffer):
        player.hp = local_recv_buffer[-1].my_char_hp
        player.player_heart = local_recv_buffer[-1].heart

        if local_recv_buffer[-1].time_remaining > 0:
            game_data.remaining_time = local_recv_buffer[-1].time_remaining
        else:
            game_data.remaining_time = 0
            
            

        for j in range(2):
            game_world.world[1][j].update_info(local_recv_buffer[-1].other_chars[j])
    
    