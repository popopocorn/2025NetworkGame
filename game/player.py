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
    def exit(self):
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


class Idle:
    @staticmethod
    def enter(player, e):
        player.frame = 0

    def exit(self):
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


class Player:
    def __init__(self, hp=1000, mp=250, ad=100, enhance_list=[]):
        self.run_speed = ((5 * 1000) / 3600) * 10 / 0.3
        self.max_hp = 1000
        self.hp=hp
        self.max_mp=250
        self.mp = mp
        self.ad=ad
        self.enhance_list = enhance_list

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
        self.ground=106+config.up
        self.temp_xy=[0, 0, 0, 0]
        self.walk_motion = [load_image(loadfile.resource_path("walk" + str(x) + ".png")) for x in range(4)]
        self.idle_motion = [load_image(loadfile.resource_path("idle" + str(x) + ".png")) for x in range(3)]
        self.jump_motion = load_image((loadfile.resource_path("jump.png")))

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
                Walk: {right_down: Idle, left_down: Idle, right_up: Idle, left_up: Idle, skill_down: Skill},
                Idle: {right_down: Walk, left_down: Walk, skill_down: Skill},
                Skill: {time_out: Wait},
                Wait: {right_down: Walk, left_down: Walk, skill_down: Skill},
            }
        )
        self.init_enhance()
    def draw(self):
        self.state_machine.draw()
        # self.font.draw(self.player_x - 50, self.player_y + 50, "mp: " + str(int(self.mp)), (255, 255, 255))
        # self.font.draw(self.player_x - 50, self.player_y + 70, "hp: " + str(int(self.hp)), (255, 255, 255))
        if config.debug_flag:
            draw_rectangle(*self.get_bb())
    def update(self):
        if self.hp<=0:
            self.sound.play()
            game_framework.change_mode(end_mode)
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
        if self.hp < self.max_hp:
            self.hp += 1 * game_framework.frame_time
        elif self.hp > self.max_hp:
            self.hp=self.max_hp
        if get_time()-self.heart_time> self.non_hit_time:
            self.player_heart=False

    def handle_event(self, event):
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
    def init_enhance(self):
        for e in self.enhance_list:
            match e:
                case "공격력 증가":
                    self.ad *= (120/100)

                case "마나 증가":
                    self.max_mp=450
                    self.mp+=100

                case "체력 증가":
                    self.max_hp=1500
                    self.hp+=150

                case "마나 회복속도 증가":
                    self.mpup=3

                case "무적 프레임 증가":
                    self.non_hit_time=1.5


class Skill:
    @staticmethod
    def enter(player, e):
        player.frame=0

        player.start_time = get_time()
        if e[1].key==SDLK_q and player.mp >= 50:
            player.skill_motion = 1
            skill=Aura_blade(player.player_x, player.player_y, player.direction, player.ad)
            game_world.add_object(skill, 3)
            player.mp-=skill.mp

        elif e[1].key==SDLK_w:
            player.skill_motion = 2
            skill=Brandish(player.player_x, player.player_y, player.direction, player.ad)
            game_world.add_object(skill, 3)
            game_world.add_collision_pair("skill:mob", None, skill)
        else:
            player.state_machine.add_event(('TIME_OUT', 0))
    def exit(self):
        pass
    @staticmethod
    def do(player):
        if player.skill_motion == 1:
            if player.frame < FRAMES_PER_ACTION[1]+1:
                player.frame = (player.frame + FRAMES_PER_ACTION[player.skill_motion + 1] * ACTION_PER_TIME[player.skill_motion + 1] * game_framework.frame_time)
            if get_time() - player.start_time >= TIME_PER_ACTION[player.skill_motion+1]:
                player.state_machine.add_event(('TIME_OUT', 0))
        if player.skill_motion == 2:
            if player.frame < FRAMES_PER_ACTION[2]+1:
                player.frame = (player.frame + FRAMES_PER_ACTION[player.skill_motion + 1] * ACTION_PER_TIME[player.skill_motion + 1] * game_framework.frame_time)
            if get_time() - player.start_time >= TIME_PER_ACTION[player.skill_motion+1]:
                player.state_machine.add_event(('TIME_OUT', 0))
    @staticmethod
    def draw(player):
        if player.skill_motion == 1:
            if player.direction == 'r':
                player.aura_blade_motion[int(player.frame)].composite_draw(0, 'h', player.player_x + aura_blade_x[int(player.frame)], player.player_y + aura_blade_y[int(player.frame)])
            else:
                player.aura_blade_motion[int(player.frame)].draw(player.player_x - 20 - aura_blade_x[int(player.frame)], player.player_y + aura_blade_y[int(player.frame)])
        elif player.skill_motion == 2:
            if player.direction == 'r':
                player.brandish_motion[int(player.frame)].composite_draw(0, 'h', player.player_x + brandish_x[int(player.frame)], player.player_y+brandish_y[int(player.frame)])
            else:
                player.brandish_motion[int(player.frame)].draw(player.player_x + brandish_x[int(player.frame)], player.player_y+brandish_y[int(player.frame)])

class Wait:
    @staticmethod
    def enter(player, e):

        player.frame = 0

    def exit(self):
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


