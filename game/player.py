from pico2d import *
from time import *

import game_data
from state_machine import *
import game_world
import game_framework
import config
from skill import *
import end_mode
import loadfile
import network

TIME_PER_ACTION = [0.5, 1.0, 0.68, 0.5]
ACTION_PER_TIME = [1.0/i for i in TIME_PER_ACTION]
FRAMES_PER_ACTION = [4, 3, 5, 7] # walk, idle, aura, brandish

aura_blade_y = [0, 0, -12, 15, 15]
aura_blade_x = [0, -30, -30, -0, 0]

brandish_x = [-30,-30, -10, -10, -30, 0, 0]
brandish_y = [0, 0, 20, 20, 20, 10, 5]


class Walk:
    @staticmethod
    def enter(player, e):

        if right_down(e) or left_up(e):
            player.direction = 'r'
            player.player_dx = 5
            player.frame = 0
        elif left_down(e) or right_up(e):
            player.direction = 'l'
            player.player_dx = -5
            player.frame = 0

    @staticmethod
    def exit(player):
        pass
    @staticmethod
    def do(player):
        if player.player_heart:
            player.walk_motion[int(player.frame)].opacify(10000 * game_framework.frame_time % 2)
            player.jump_motion.opacify(10000 * game_framework.frame_time % 2)
        else:
            player.walk_motion[int(player.frame)].opacify(1)
            player.jump_motion.opacify(1)
        if (player.direction == 'r' and player.player_x < config.width - 20) or (player.direction == 'l' and player.player_x > 20):
            player.player_x += player.player_dx * player.run_speed * game_framework.frame_time
        player.frame = (player.frame + FRAMES_PER_ACTION[0]*ACTION_PER_TIME[0] * game_framework.frame_time)%FRAMES_PER_ACTION[0]

        if player.hp <= 0:
            player.state_machine.add_event(('DEAD', 0))
    @staticmethod
    def draw(player):

        if player.direction == 'r':
            if not player.player_jump:
                player.walk_motion[int(player.frame)].composite_draw(0, 'h', player.player_x + 10, player.player_y)
            else:
                player.jump_motion.composite_draw(0, 'h', player.player_x - 25, player.player_y + 5)
        else:
            if not player.player_jump:
                player.walk_motion[int(player.frame)].draw(player.player_x - 25, player.player_y)
            else:
                player.jump_motion.draw(player.player_x + 15, player.player_y + 5)

    # 상태의 char[4]를 가져오기 위한 함수        # 신태양 11/06
    @staticmethod
    def get_name():
        return "Walk\0"

class Idle:
    @staticmethod
    def enter(player, e):
        player.frame = 0

    @staticmethod
    def exit(player):
        pass

    @staticmethod
    def do(player):
        if player.player_heart:
            player.idle_motion[int(player.frame)].opacify(10000 * game_framework.frame_time % 2)
            player.jump_motion.opacify(10000 * game_framework.frame_time % 2)
        else:
            player.idle_motion[int(player.frame)].opacify(1)
            player.jump_motion.opacify(1)
        player.frame = (player.frame + FRAMES_PER_ACTION[1]*ACTION_PER_TIME[1] * game_framework.frame_time)%FRAMES_PER_ACTION[1]

        if player.hp <= 0:
            player.state_machine.add_event(('DEAD', 0))

    @staticmethod
    def draw(player):
        if not player.player_jump:
            if player.direction == 'r':
                player.idle_motion[int(player.frame)].composite_draw(0, 'h', player.player_x + 10, player.player_y)
            else:
                player.idle_motion[int(player.frame)].draw(player.player_x - 20, player.player_y)
        else:
            if player.direction == 'r':
                player.jump_motion.composite_draw(0, 'h', player.player_x - 15, player.player_y + 5)
            else:
                player.jump_motion.draw(player.player_x + 15, player.player_y + 5)

    # 상태의 char[4]를 가져오기 위한 함수        # 신태양 11/06
    @staticmethod
    def get_name():
        return "Idle\0"



class Brds:
    @staticmethod
    def enter(player, e):
        player.frame=0
        player.start_time = get_time()
        skill=Brandish(player.player_x, player.player_y, player.direction, player.ad)
        game_world.add_object(skill, 3)
        # 스킬 상태에 도입하면 send_buffer의 skill_info를 채운다.         # 신태양 11/06
        # 그럼 위에 add_object는 지워야 할 듯
        network.send_buffer.skill_info.update(2, player)

    @staticmethod
    def exit(player):
        pass
    @staticmethod
    def do(player):
        player.frame = (player.frame + FRAMES_PER_ACTION[3]*ACTION_PER_TIME[3] * game_framework.frame_time)%FRAMES_PER_ACTION[3]
        if get_time() - player.start_time >= TIME_PER_ACTION[3]:
            player.state_machine.add_event(('TIME_OUT', 0))

        if player.hp <= 0:
            player.state_machine.add_event(('DEAD', 0))

    @staticmethod
    def draw(player):
        if player.direction == 'r':
            player.brandish_motion[int(player.frame)].composite_draw(0, 'h', player.player_x + brandish_x[int(player.frame)], player.player_y+brandish_y[int(player.frame)])
        else:
            player.brandish_motion[int(player.frame)].draw(player.player_x + brandish_x[int(player.frame)], player.player_y+brandish_y[int(player.frame)])
    # 상태의 char[4]를 가져오기 위한 함수        # 신태양 11/06
    @staticmethod
    def get_name():
        return "Brds\0"
    
class Aura:
    @staticmethod
    def enter(player, e):
        player.frame=0

        player.start_time = get_time()
        if player.mp >= 50:
            skill=Aura_blade(player.player_x, player.player_y, player.direction, player.ad)
            game_world.add_object(skill, 3)
            player.mp-=skill.mp

            # 스킬 상태에 도입하면 send_buffer의 skill_info를 채운다.         # 신태양 11/06
            network.send_buffer.skill_info.update(1, player)
        else:
            player.state_machine.add_event(('TIME_OUT', 0))

    @staticmethod
    def exit(player):
        pass

    @staticmethod
    def do(player):
        
        player.frame = (player.frame + FRAMES_PER_ACTION[2]*ACTION_PER_TIME[2] * game_framework.frame_time)%FRAMES_PER_ACTION[2]
        if get_time() - player.start_time >= TIME_PER_ACTION[2]:
            player.state_machine.add_event(('TIME_OUT', 0))

        if player.hp <= 0:
            player.state_machine.add_event(('DEAD', 0))

    @staticmethod
    def draw(player):
        if player.direction == 'r':
            player.aura_blade_motion[int(player.frame)].composite_draw(0, 'h', player.player_x + aura_blade_x[int(player.frame)], player.player_y + aura_blade_y[int(player.frame)])
        else:
            player.aura_blade_motion[int(player.frame)].draw(player.player_x - 20 - aura_blade_x[int(player.frame)], player.player_y + aura_blade_y[int(player.frame)])

    # 상태의 char[4]를 가져오기 위한 함수        # 신태양 11/06
    @staticmethod
    def get_name():
        return "Aura\0"


class Wait:
    @staticmethod
    def enter(player, e):

        player.frame = 0

    @staticmethod
    def exit(player):
        pass

    @staticmethod
    def do(player):
        if player.player_heart:
            player.idle_motion[int(player.frame)].opacify(10000 * game_framework.frame_time % 2)
            player.jump_motion.opacify(10000 * game_framework.frame_time % 2)
        else:
            player.idle_motion[int(player.frame)].opacify(1)
            player.jump_motion.opacify(1)
        player.frame = (player.frame + FRAMES_PER_ACTION[1] * ACTION_PER_TIME[1] * game_framework.frame_time) % \
                       FRAMES_PER_ACTION[1]

        if player.hp <= 0:
            player.state_machine.add_event(('DEAD', 0))

    @staticmethod
    def draw(player):
        if not player.player_jump:
            if player.direction == 'r':
                player.idle_motion[int(player.frame)].composite_draw(0, 'h', player.player_x + 10, player.player_y)
            else:
                player.idle_motion[int(player.frame)].draw(player.player_x - 20, player.player_y)
        else:
            if player.direction == 'r':
                player.jump_motion.composite_draw(0, 'h', player.player_x - 15, player.player_y + 5)
            else:
                player.jump_motion.draw(player.player_x + 15, player.player_y + 5)

    # 상태의 char[4]를 가져오기 위한 함수        # 신태양 11/06
    @staticmethod
    def get_name():
        return "Wait\0"

class Dead:
    @staticmethod
    def enter(player, e):
        player.frame = 0
    def exit(player):
        player.player_x = randint(20, config.width-20)
        player.player_y = randint(200, config.height-20)

    @staticmethod
    def do(player):
        if player.hp != 0:
            player.state_machine.add_event(('TIME_OUT', 0))

    @staticmethod
    def draw(player):
        player.tomb_stone.draw(player.player_x + 15, player.player_y + 5)
                

    # 상태의 char[4]를 가져오기 위한 함수        # 신태양 11/06
    @staticmethod
    def get_name():
        return "Dead\0"

class Player:
    def __init__(self):
        self.run_speed = ((5 * 1000) / 3600) * 10 / 0.3
        self.max_hp = 1000
        self.hp=game_data.player_info[0]
        self.max_mp=250
        self.mp = game_data.player_info[1]
        self.ad=game_data.player_info[2]


        self.mpup = 1
        self.jump_speed = ((5 * 1000) / 3600) * 10 / 0.3
        self.non_hit_time_now = get_time()
        self.non_hit_time = 1

        self.gravity = 3
        self.player_jump = False
        self.player_heart = False
        self.heart_time = get_time()

        self.player_dx = 0
        self.player_dy = 0
        self.player_x = 200
        self.player_y = 106+config.up
        self.player_x = randint(20, config.width-20)
        self.player_y = randint(200, config.height-20)
        self.ground=106+config.up
        self.temp_xy=[0, 0, 0, 0]
        self.walk_motion = [load_image(loadfile.resource_path("walk" + str(x) + ".png")) for x in range(4)]
        self.idle_motion = [load_image(loadfile.resource_path("idle" + str(x) + ".png")) for x in range(3)]
        self.jump_motion = load_image(loadfile.resource_path("jump.png"))
        self.tomb_stone = load_image(loadfile.resource_path("Tombstone.png"))

        self.skill_motion=0
        self.aura_blade_motion = [load_image(loadfile.resource_path("auraBlade" +str(i) +".png")) for i in range(5)]
        self.brandish_motion = [load_image(loadfile.resource_path("brandish" + str(i)+".png")) for i in range(7)]

        self.sound = load_music(loadfile.resource_path("Tombstone.mp3"))
        self.sound.set_volume(config.volume * 2)


        self.font =load_font(config.font, 16)
        self.event=None
        self.direction = 'r'
        self.frame = 0
        self.state_machine=StateMachine(self)
        self.state_machine.start(Idle)
        self.state_machine.set_transitions(
            {
                Walk: {right_down: Idle, left_down: Idle, right_up: Idle, left_up: Idle, q_down: Aura,  w_down: Brds, is_dead: Dead},
                Idle: {right_down: Walk, left_down: Walk, q_down: Aura,  w_down: Brds, is_dead: Dead},
                Aura: {time_out: Wait, is_dead: Dead},
                Brds: {time_out: Wait, is_dead: Dead},
                Wait: {right_down: Walk, left_down: Walk, q_down: Aura,  w_down: Brds, is_dead: Dead},
                Dead: {time_out : Idle}
            }
        )
    def draw(self):
        self.state_machine.draw()
        # self.font.draw(self.player_x - 50, self.player_y + 50, "mp: " + str(int(self.mp)), (255, 255, 255))
        # self.font.draw(self.player_x - 50, self.player_y + 70, "hp: " + str(int(self.hp)), (255, 255, 255))
        if config.debug_flag:
            draw_rectangle(*self.get_bb())
    def update(self):
        if self.hp<=0:
            self.state_machine.add_event(('DEAD', 0))

        if(self.player_x +10 <self.temp_xy[0] or self.player_x -20 > self.temp_xy[2]) or\
            self.event.type == SDL_KEYDOWN and self.event.key == SDLK_DOWN :
            self.ground=106+config.up
        if self.player_y>self.ground:
            self.player_jump=True
        self.state_machine.update()
        if self.player_jump:
            self.update_jump(self.ground)
        if self.mp < self.max_mp:
            self.mp += self.mpup * 3 * game_framework.frame_time
        elif self.mp > self.max_mp:
            self.mp=self.max_mp
        if get_time()-self.heart_time> self.non_hit_time:
            self.player_heart=False

        # 매 프레임마다 send_buffer의 char_info를 갱신한다.         # 신태양 11/06
        network.send_buffer.char_info.update(self)

    def handle_event(self, event):
        if self.hp <= 0 :
            return

        if event.type == SDL_KEYDOWN and event.key == SDLK_LALT and not self.player_jump:
            self.player_jump=True
            self.player_dy=25
        self.state_machine.add_event(('INPUT', event))
        self.event=event
    def get_player_location(self):
        return self.player_x

    def update_jump(self, y):
        if self.player_jump:
            # 점프 속도를 시간 프레임에 따라 계산
            self.player_y += self.player_dy * self.jump_speed * game_framework.frame_time
            self.player_dy -= self.gravity* self.jump_speed * game_framework.frame_time  # 중력 적용

            # 바닥에 도달했을 때
            if self.player_y <= y:
                self.player_y = y
                self.player_jump = False
                self.player_dy = 0  # 점프 속도 초기화
    def get_jump(self):
        return self.player_jump
    def get_bb(self):
        return self.player_x - 20, self.player_y - 35, self.player_x + 10, self.player_y + 30
        pass

    def handle_collision(self, group, other):
        self.temp_xy = other.get_bb()
        if group=="player:platform":
            if self.player_y>=self.temp_xy[3]:
                self.ground=self.temp_xy[3]
            else:
                self.ground=106+config.up
        if group=="player:mob":
            if get_time() - self.non_hit_time_now > self.non_hit_time:
                if other.is_mush:
                    if self.player_jump:
                        pass
                    else:
                        self.hp -= other.damage
                        self.non_hit_time_now = get_time()
                        self.player_heart=True
                        self.heart_time=get_time()
                else:
                    self.hp-=other.damage
                    self.non_hit_time_now=get_time()
                    self.player_heart = True
                    self.heart_time = get_time()
