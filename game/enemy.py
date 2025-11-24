from pico2d import *
from time import *

import game_data
import game_world
import game_framework
import config
from skill import *
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
    def enter(enemy):
        enemy.frame = 0
    def exit(self):
        pass
    @staticmethod
    def do(enemy):
        if enemy.enemy_heart:
            enemy.walk_motion[int(enemy.frame)].opacify(10000 * game_framework.frame_time % 2)
            enemy.jump_motion.opacify(10000 * game_framework.frame_time % 2)
        else:
            enemy.walk_motion[int(enemy.frame)].opacify(1)
            enemy.jump_motion.opacify(1)
        enemy.frame = (enemy.frame + FRAMES_PER_ACTION[0]*ACTION_PER_TIME[0] * game_framework.frame_time)%FRAMES_PER_ACTION[0]

    @staticmethod
    def draw(enemy):

        if enemy.direction == 'r':
            if not enemy.enemy_jump:
                enemy.walk_motion[int(enemy.frame)].composite_draw(0, 'h', enemy.enemy_x + 10, enemy.enemy_y)
            else:
                enemy.jump_motion.composite_draw(0, 'h', enemy.enemy_x - 25, enemy.enemy_y + 5)
        else:
            if not enemy.enemy_jump:
                enemy.walk_motion[int(enemy.frame)].draw(enemy.enemy_x - 25, enemy.enemy_y)
            else:
                enemy.jump_motion.draw(enemy.enemy_x + 15, enemy.enemy_y + 5)

    # 상태의 char[4]를 가져오기 위한 함수        # 신태양 11/06
    @staticmethod
    def get_name():
        return "Walk\0"

class Idle:
    @staticmethod
    def enter(enemy):
        enemy.frame = 0

    def exit(self):
        pass

    @staticmethod
    def do(enemy):
        if enemy.enemy_heart:
            enemy.idle_motion[int(enemy.frame)].opacify(10000 * game_framework.frame_time % 2)
            enemy.jump_motion.opacify(10000 * game_framework.frame_time % 2)
        else:
            enemy.idle_motion[int(enemy.frame)].opacify(1)
            enemy.jump_motion.opacify(1)
        enemy.frame = (enemy.frame + FRAMES_PER_ACTION[1]*ACTION_PER_TIME[1] * game_framework.frame_time)%FRAMES_PER_ACTION[1]

    @staticmethod
    def draw(enemy):
        if not enemy.enemy_jump:
            if enemy.direction == 'r':
                enemy.idle_motion[int(enemy.frame)].composite_draw(0, 'h', enemy.enemy_x + 10, enemy.enemy_y)
            else:
                enemy.idle_motion[int(enemy.frame)].draw(enemy.enemy_x - 20, enemy.enemy_y)
        else:
            if enemy.direction == 'r':
                enemy.jump_motion.composite_draw(0, 'h', enemy.enemy_x - 15, enemy.enemy_y + 5)
            else:
                enemy.jump_motion.draw(enemy.enemy_x + 15, enemy.enemy_y + 5)

    # 상태의 char[4]를 가져오기 위한 함수        # 신태양 11/06
    @staticmethod
    def get_name():
        return "Idle\0"

class Enemy:
    def __init__(self):
        self.enemy_jump = False
        self.enemy_heart = False

        self.enemy_x = 200
        self.enemy_y = 106+config.up
        self.temp_xy=[0, 0, 0, 0]
        self.walk_motion = [load_image(loadfile.resource_path("walk" + str(x) + ".png")) for x in range(4)]
        self.idle_motion = [load_image(loadfile.resource_path("idle" + str(x) + ".png")) for x in range(3)]
        self.jump_motion = load_image((loadfile.resource_path("jump.png")))

        self.skill_motion=0
        self.aura_blade_motion = [load_image(loadfile.resource_path("auraBlade" +str(i) +".png")) for i in range(5)]
        self.brandish_motion = [load_image(loadfile.resource_path("brandish" + str(i)+".png")) for i in range(7)]

        self.sound = load_music(loadfile.resource_path("Tombstone.mp3"))
        self.sound.set_volume(config.volume * 2)
        self.direction = 'r'
        self.frame = 0
        self.state = Idle

    def draw(self):
        self.state.draw()
        if config.debug_flag:
            draw_rectangle(*self.get_bb())
    def update(self, x, y, state):
        self.enemy_x = x
        self.enemy_y = y
        if(self.state != state):
            self.state.exit()
            self.state = state
            self.state.enter()
        
    def handle_event(self, event):
        pass
    def get_enemy_location(self):
        return self.enemy_x
    

class Skill:
    @staticmethod
    def enter(enemy):
        enemy.frame=0

        enemy.start_time = get_time()
        

    def exit(self):
        pass
    @staticmethod
    def do(enemy):
        if enemy.skill_motion == 1:
            if enemy.frame < FRAMES_PER_ACTION[1]+1:
                enemy.frame = (enemy.frame + FRAMES_PER_ACTION[enemy.skill_motion + 1] * ACTION_PER_TIME[enemy.skill_motion + 1] * game_framework.frame_time)
        if enemy.skill_motion == 2:
            if enemy.frame < FRAMES_PER_ACTION[2]+1:
                enemy.frame = (enemy.frame + FRAMES_PER_ACTION[enemy.skill_motion + 1] * ACTION_PER_TIME[enemy.skill_motion + 1] * game_framework.frame_time)

    @staticmethod
    def draw(enemy):
        if enemy.skill_motion == 1:
            if enemy.direction == 'r':
                enemy.aura_blade_motion[int(enemy.frame)].composite_draw(0, 'h', enemy.enemy_x + aura_blade_x[int(enemy.frame)], enemy.enemy_y + aura_blade_y[int(enemy.frame)])
            else:
                enemy.aura_blade_motion[int(enemy.frame)].draw(enemy.enemy_x - 20 - aura_blade_x[int(enemy.frame)], enemy.enemy_y + aura_blade_y[int(enemy.frame)])
        elif enemy.skill_motion == 2:
            if enemy.direction == 'r':
                enemy.brandish_motion[int(enemy.frame)].composite_draw(0, 'h', enemy.enemy_x + brandish_x[int(enemy.frame)], enemy.enemy_y+brandish_y[int(enemy.frame)])
            else:
                enemy.brandish_motion[int(enemy.frame)].draw(enemy.enemy_x + brandish_x[int(enemy.frame)], enemy.enemy_y+brandish_y[int(enemy.frame)])

    # 상태의 char[4]를 가져오기 위한 함수        # 신태양 11/06
    @staticmethod
    def get_name():
        return "Attk\0"

class Wait:
    @staticmethod
    def enter(enemy, e):

        enemy.frame = 0

    def exit(self):
        pass

    @staticmethod
    def do(enemy):
        if enemy.enemy_heart:
            enemy.idle_motion[int(enemy.frame)].opacify(10000 * game_framework.frame_time % 2)
            enemy.jump_motion.opacify(10000 * game_framework.frame_time % 2)
        else:
            enemy.idle_motion[int(enemy.frame)].opacify(1)
            enemy.jump_motion.opacify(1)
        enemy.frame = (enemy.frame + FRAMES_PER_ACTION[1] * ACTION_PER_TIME[1] * game_framework.frame_time) % \
                       FRAMES_PER_ACTION[1]

    @staticmethod
    def draw(enemy):
        if not enemy.enemy_jump:
            if enemy.direction == 'r':
                enemy.idle_motion[int(enemy.frame)].composite_draw(0, 'h', enemy.enemy_x + 10, enemy.enemy_y)
            else:
                enemy.idle_motion[int(enemy.frame)].draw(enemy.enemy_x - 20, enemy.enemy_y)
        else:
            if enemy.direction == 'r':
                enemy.jump_motion.composite_draw(0, 'h', enemy.enemy_x - 15, enemy.enemy_y + 5)
            else:
                enemy.jump_motion.draw(enemy.enemy_x + 15, enemy.enemy_y + 5)


from pico2d import *
from time import *

import game_data
import game_world
import game_framework
import config
from skill import *
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
    def enter(enemy):
        enemy.frame = 0
    def exit(self):
        pass
    @staticmethod
    def do(enemy):
        if enemy.enemy_heart:
            enemy.walk_motion[int(enemy.frame)].opacify(10000 * game_framework.frame_time % 2)
            enemy.jump_motion.opacify(10000 * game_framework.frame_time % 2)
        else:
            enemy.walk_motion[int(enemy.frame)].opacify(1)
            enemy.jump_motion.opacify(1)
        enemy.frame = (enemy.frame + FRAMES_PER_ACTION[0]*ACTION_PER_TIME[0] * game_framework.frame_time)%FRAMES_PER_ACTION[0]

    @staticmethod
    def draw(enemy):

        if enemy.direction == 'r':
            if not enemy.enemy_jump:
                enemy.walk_motion[int(enemy.frame)].composite_draw(0, 'h', enemy.enemy_x + 10, enemy.enemy_y)
            else:
                enemy.jump_motion.composite_draw(0, 'h', enemy.enemy_x - 25, enemy.enemy_y + 5)
        else:
            if not enemy.enemy_jump:
                enemy.walk_motion[int(enemy.frame)].draw(enemy.enemy_x - 25, enemy.enemy_y)
            else:
                enemy.jump_motion.draw(enemy.enemy_x + 15, enemy.enemy_y + 5)

    # 상태의 char[4]를 가져오기 위한 함수        # 신태양 11/06
    @staticmethod
    def get_name():
        return "Walk\0"

class Idle:
    @staticmethod
    def enter(enemy):
        enemy.frame = 0

    def exit(self):
        pass

    @staticmethod
    def do(enemy):
        if enemy.enemy_heart:
            enemy.idle_motion[int(enemy.frame)].opacify(10000 * game_framework.frame_time % 2)
            enemy.jump_motion.opacify(10000 * game_framework.frame_time % 2)
        else:
            enemy.idle_motion[int(enemy.frame)].opacify(1)
            enemy.jump_motion.opacify(1)
        enemy.frame = (enemy.frame + FRAMES_PER_ACTION[1]*ACTION_PER_TIME[1] * game_framework.frame_time)%FRAMES_PER_ACTION[1]

    @staticmethod
    def draw(enemy):
        if not enemy.enemy_jump:
            if enemy.direction == 'r':
                enemy.idle_motion[int(enemy.frame)].composite_draw(0, 'h', enemy.enemy_x + 10, enemy.enemy_y)
            else:
                enemy.idle_motion[int(enemy.frame)].draw(enemy.enemy_x - 20, enemy.enemy_y)
        else:
            if enemy.direction == 'r':
                enemy.jump_motion.composite_draw(0, 'h', enemy.enemy_x - 15, enemy.enemy_y + 5)
            else:
                enemy.jump_motion.draw(enemy.enemy_x + 15, enemy.enemy_y + 5)

    # 상태의 char[4]를 가져오기 위한 함수        # 신태양 11/06
    @staticmethod
    def get_name():
        return "Idle\0"

class Enemy:
    def __init__(self, x=200):
        self.enemy_jump = False
        self.enemy_heart = False

        self.enemy_dx = 0
        self.enemy_dy = 0
        self.enemy_x = x
        self.enemy_y = 106+config.up
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
        self.state = Idle

    def draw(self):
        # self.font.draw(self.enemy_x - 50, self.enemy_y + 50, "mp: " + str(int(self.mp)), (255, 255, 255))
        # self.font.draw(self.enemy_x - 50, self.enemy_y + 70, "hp: " + str(int(self.hp)), (255, 255, 255))
        if config.debug_flag:
            draw_rectangle(*self.get_bb())

        self.state.draw(self)
    def update(self):
        self.state.do(self)

    def update_info(self, info):
        self.enemy_x = info.x
        self.enemy_y = info.y
        if self.state.get_name() != info.state:
            self.state.exit()
            if info.state == Idle.get_name():
                self.state=Idle
            elif info.state == Walk.get_name():
                self.state=Walk
            elif info.state == Skill.get_name():
                self.state=Skill
            elif info.state == Wait.get_name():
                self.state=Wait
        

    def handle_event(self, event):
        pass
    def get_enemy_location(self):
        return self.enemy_x
    def get_bb(self):
        return self.enemy_x - 20, self.enemy_y - 35, self.enemy_x + 10, self.enemy_y + 30
    
    

class Skill:
    @staticmethod
    def enter(enemy):
        enemy.frame=0

        enemy.start_time = get_time()
        

    def exit(self):
        pass
    @staticmethod
    def do(enemy):
        if enemy.skill_motion == 1:
            if enemy.frame < FRAMES_PER_ACTION[1]+1:
                enemy.frame = (enemy.frame + FRAMES_PER_ACTION[enemy.skill_motion + 1] * ACTION_PER_TIME[enemy.skill_motion + 1] * game_framework.frame_time)
        if enemy.skill_motion == 2:
            if enemy.frame < FRAMES_PER_ACTION[2]+1:
                enemy.frame = (enemy.frame + FRAMES_PER_ACTION[enemy.skill_motion + 1] * ACTION_PER_TIME[enemy.skill_motion + 1] * game_framework.frame_time)

    @staticmethod
    def draw(enemy):
        if enemy.skill_motion == 1:
            if enemy.direction == 'r':
                enemy.aura_blade_motion[int(enemy.frame)].composite_draw(0, 'h', enemy.enemy_x + aura_blade_x[int(enemy.frame)], enemy.enemy_y + aura_blade_y[int(enemy.frame)])
            else:
                enemy.aura_blade_motion[int(enemy.frame)].draw(enemy.enemy_x - 20 - aura_blade_x[int(enemy.frame)], enemy.enemy_y + aura_blade_y[int(enemy.frame)])
        elif enemy.skill_motion == 2:
            if enemy.direction == 'r':
                enemy.brandish_motion[int(enemy.frame)].composite_draw(0, 'h', enemy.enemy_x + brandish_x[int(enemy.frame)], enemy.enemy_y+brandish_y[int(enemy.frame)])
            else:
                enemy.brandish_motion[int(enemy.frame)].draw(enemy.enemy_x + brandish_x[int(enemy.frame)], enemy.enemy_y+brandish_y[int(enemy.frame)])

    # 상태의 char[4]를 가져오기 위한 함수        # 신태양 11/06
    @staticmethod
    def get_name():
        return "Attk\0"

class Wait:
    @staticmethod
    def enter(enemy, e):

        enemy.frame = 0

    def exit(self):
        pass

    @staticmethod
    def do(enemy):
        if enemy.enemy_heart:
            enemy.idle_motion[int(enemy.frame)].opacify(10000 * game_framework.frame_time % 2)
            enemy.jump_motion.opacify(10000 * game_framework.frame_time % 2)
        else:
            enemy.idle_motion[int(enemy.frame)].opacify(1)
            enemy.jump_motion.opacify(1)
        enemy.frame = (enemy.frame + FRAMES_PER_ACTION[1] * ACTION_PER_TIME[1] * game_framework.frame_time) % \
                       FRAMES_PER_ACTION[1]

    @staticmethod
    def draw(enemy):
        if not enemy.enemy_jump:
            if enemy.direction == 'r':
                enemy.idle_motion[int(enemy.frame)].composite_draw(0, 'h', enemy.enemy_x + 10, enemy.enemy_y)
            else:
                enemy.idle_motion[int(enemy.frame)].draw(enemy.enemy_x - 20, enemy.enemy_y)
        else:
            if enemy.direction == 'r':
                enemy.jump_motion.composite_draw(0, 'h', enemy.enemy_x - 15, enemy.enemy_y + 5)
            else:
                enemy.jump_motion.draw(enemy.enemy_x + 15, enemy.enemy_y + 5)

    @staticmethod
    def get_name():
        return "Wait\0"