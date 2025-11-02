from pico2d import *
from monster_state import *
import game_framework
from state_machine import time_out
import  config
import game_world
import game_data
import end_mode

import loadfile


TIME_PER_ACTION = [1.0, 1.0, 1.0, 1.5, 0.5]
ACTION_PER_TIME = [1.0/i for i in TIME_PER_ACTION]
FRAMES_PER_ACTION = [2, 5 , 4, 3, 3] # idle, walk, skill, die


class Idle:
    @staticmethod
    def enter(mob, e):
        mob.start_time = get_time()
        mob.frame=0
    @staticmethod
    def exit(mob, e):
        pass
    @staticmethod
    def do(mob):
        mob.frame = (mob.frame + FRAMES_PER_ACTION[0]*ACTION_PER_TIME[0] * game_framework.frame_time)%FRAMES_PER_ACTION[0]
        if get_time() - mob.start_time> 1:
            mob.state_machine.add_event(("TIME_OUT", (0, 0)))

    @staticmethod
    def draw(mob):
        if mob.direction == 'r':
            mob.idle_motion[int(mob.frame)].draw(mob.x, mob.y + 31, 150, 150)
        else:
            mob.idle_motion[int(mob.frame)].composite_draw(0, 'h', mob.x, mob.y + 31,)


class Trace():
    @staticmethod
    def enter(mob, e):

        mob.state_machine.add_event(e)
        mob.frame=0
        mob.start_time = get_time()

    @staticmethod
    def exit(mob, e):
        pass

    @staticmethod
    def do(mob):
        mob.frame = (mob.frame + FRAMES_PER_ACTION[1]*ACTION_PER_TIME[1] * game_framework.frame_time)%FRAMES_PER_ACTION[1]
        if get_time() - mob.start_time > 3:
            mob.state_machine.add_event(("TIME_OUT", (0, 0)))
        mob.x += mob.dx * mob.run_speed * game_framework.frame_time

    @staticmethod
    def draw(mob):
        if mob.direction == 'l':
            mob.move_motion[int(mob.frame)].composite_draw(0, 'h', mob.x, mob.y + 31)
        else:
            mob.move_motion[int(mob.frame)].draw(mob.x, mob.y + 31)

class Attack():
    @staticmethod
    def enter(mob, e):
        mob.frame=0
        mob.start_time = get_time()
        mob.attack=False
        mob.skill_sound.play()
    @staticmethod
    def exit(mob, e):
        mob.start_time=0

    @staticmethod
    def do(mob):
        mob.frame = (mob.frame + FRAMES_PER_ACTION[2] * ACTION_PER_TIME[2] * game_framework.frame_time) % \
                     FRAMES_PER_ACTION[2]
        if mob.frame > 3 and not mob.attack:
            mob_skill=mob_atatck(mob.x, mob.y, mob.direction)
            game_world.add_object(mob_skill, 3)
            game_world.add_collision_pair("player:mob", None, mob_skill)
            mob.attack=True
        if mob.frame >= FRAMES_PER_ACTION[2] -1 :
            mob.state_machine.add_event(("DONE", (0, 0)))

    @staticmethod
    def draw(mob):
        if mob.direction == 'l':
            mob.skill_motion[int(mob.frame)].composite_draw(0, 'h', mob.x, mob.y + 31)
        else:
            mob.skill_motion[int(mob.frame)].draw(mob.x, mob.y + 31)


class JuniorBarlog:
    def __init__(self):
        self.font = load_font(config.font, 30)

        self.x=600
        self.y=115+config.up
        self.run_speed = ((10 * 1000) / 3600) * 10 / 0.3
        self.hp = 5000
        self.damage=270

        self.is_mush = False
        self.attack=False

        self.delay=0

        self.idle_motion =[load_image(loadfile.resource_path("barlog_idle (" + str(i+1) + ").png")) for i in range(FRAMES_PER_ACTION[0])]
        self.move_motion = [load_image(loadfile.resource_path("barlog_move (" + str(i+1) + ").png")) for i in range(FRAMES_PER_ACTION[1])]
        self.skill_motion=[load_image(loadfile.resource_path("barlog_skill2 (" + str(i+1) + ").png")) for i in range(FRAMES_PER_ACTION[2])]
        self.die_motion=[load_image(loadfile.resource_path("barlog_die (" + str(i+1) + ").png")) for i in range(FRAMES_PER_ACTION[4])]
        self.skill_sound = load_music(loadfile.resource_path("barlog_skill.mp3"))
        self.skill_sound.set_volume(config.volume)
        self.hit_sound = load_music(loadfile.resource_path("barlog_hit.mp3"))
        self.hit_sound.set_volume(config.volume)
        self.die_sound = load_music(loadfile.resource_path("barlog_die.mp3"))
        self.die_sound.set_volume(config.volume)

        self.direction = 'r'
        self.dx=0
        self.frame = 0
        self.state_machine = StateMachine(self)
        self.state_machine.start(Idle)
        self.state_machine.set_transitions(
            {
                Trace: {can_attack: Attack, die: Die},
                Attack: {Done: Trace, die: Die},
                Idle: {time_out: Trace, die: Die},
                Die: {time_out: Die},
            }
        )
    def update(self):
        self.state_machine.update()
        if self.hp <= 0:
            self.state_machine.add_event(('DIE', (0, 0)))
    def handle_events(self, player_location):
        if player_location < self.x:
            self.direction='r'
            self.dx= -1
        else:
            self.direction='l'
            self.dx=1

        self.state_machine.add_event(('INPUT', (player_location, self.x)))

    def get_bb(self):
        return self.x -70, self.y - 50, self.x+60, self.y+55
    def draw(self):

        self.state_machine.draw()
        if config.debug_flag:
            draw_rectangle(*self.get_bb())
            self.font.draw(self.x - 50, self.y + 120, str(int(self.hp)), (255, 255, 255))

    def handle_collision(self, group, other):
        if group =="skill:mob":
            if not other.is_hit:
                self.hp -= other.damage
                self.hit_sound.play()

class mob_atatck:
    def __init__(self, x, y, dir):
        self.x = x
        self.y = y
        self.is_mush=False
        self.is_hit = False
        self.start_time=get_time()
        self.damage = 500
        self.skill_effect=[load_image(loadfile.resource_path("fire_ball (" + str(i+1) + ").png")) for i in range(3)]
        self.direction = dir
        if dir == 'l':
            self.dx = 1
        else:
            self.dx = -1
        self.frame = 0
        self.run_speed = ((30 * 1000) / 3600) * 10 / 0.3

    def draw(self):
        if self.direction == "r":
            self.skill_effect[int(self.frame)].draw(self.x, self.y)
        else:
            self.skill_effect[int(self.frame)].composite_draw(0, 'h', self.x, self.y)
        if config.debug_flag:
            draw_rectangle(*self.get_bb())

    def update(self):
        self.frame = (self.frame + FRAMES_PER_ACTION[4] * ACTION_PER_TIME[4] * game_framework.frame_time) % \
                    FRAMES_PER_ACTION[4]
        self.x += self.dx * self.run_speed * game_framework.frame_time
        if self.x < 0 or self.x>config.width:
            game_world.remove_object(self)
    def get_bb(self):
        # fill here
        if self.direction == 'l':
            return self.x + 10, self.y -10, self.x +30, self.y+10
        else:
            return self.x - 20, self.y - 10, self.x, self.y + 10

    def handle_collision(self, group, other):
        if group == "player.mob":
            self.is_hit = True

class Die:
    @staticmethod
    def enter(mob, e):
        mob.start_time = get_time()
        mob.frame=0
        mob.die_sound.play()
    @staticmethod
    def exit(mob, e):
        game_world.remove_object(mob)
        #game_framework.change_mode(next_mod)
        game_data.clear = True
        game_framework.change_mode(end_mode)

    @staticmethod
    def do(mob):
        mob.frame = (mob.frame + FRAMES_PER_ACTION[3]*ACTION_PER_TIME[3] * game_framework.frame_time)%FRAMES_PER_ACTION[3]
        if mob.frame >= FRAMES_PER_ACTION[3] -1 :
            mob.state_machine.add_event(("TIME_OUT", (0, 0)))

    @staticmethod
    def draw(mob):
        if mob.direction == 'r':
            mob.die_motion[int(mob.frame)].draw(mob.x, mob.y + 31)
        else:
            mob.die_motion[int(mob.frame)].composite_draw(0, 'h', mob.x, mob.y + 31)

