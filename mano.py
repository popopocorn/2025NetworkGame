from pico2d import *
from monster_state import *
import game_framework
from state_machine import time_out
import config
import game_world
import item_mode
import play_mode_2 as next_mod
import loadfile

TIME_PER_ACTION = [1.0, 1.0, 1.0, 1.5]
ACTION_PER_TIME = [1.0/i for i in TIME_PER_ACTION]
FRAMES_PER_ACTION = [8, 6 ,10, 9] # idle, walk, skill

mano_motion_y = [0, 0, 0, 1.5, 1.5, 27, 27, 34.5, 39, 37.5]

class Idle:
    @staticmethod
    def enter(mano, e):
        mano.start_time = get_time()
        mano.frame=0
    @staticmethod
    def exit(mano, e):
        pass
    @staticmethod
    def do(mano):
        mano.frame = (mano.frame + FRAMES_PER_ACTION[0]*ACTION_PER_TIME[0] * game_framework.frame_time)%FRAMES_PER_ACTION[0]
        if get_time() - mano.start_time> 1:
            mano.state_machine.add_event(("TIME_OUT", (0, 0)))

    @staticmethod
    def draw(mano):
        if mano.direction == 'r':
            mano.idle_motion[int(mano.frame)].draw(mano.x, mano.y + 31, 150, 150)
        else:
            mano.idle_motion[int(mano.frame)].composite_draw(0, 'h', mano.x, mano.y + 31, 150, 150)


class Trace():
    @staticmethod
    def enter(mano, e):

        mano.state_machine.add_event(e)
        mano.frame=0
        mano.start_time = get_time()

    @staticmethod
    def exit(mano, e):
        pass

    @staticmethod
    def do(mano):
        mano.frame = (mano.frame + FRAMES_PER_ACTION[1]*ACTION_PER_TIME[1] * game_framework.frame_time)%FRAMES_PER_ACTION[1]
        if get_time() - mano.start_time > 3:
            mano.state_machine.add_event(("TIME_OUT", (0, 0)))
        mano.x += mano.dx * mano.run_speed * game_framework.frame_time

    @staticmethod
    def draw(mano):
        if mano.direction == 'l':
            mano.move_motion[int(mano.frame)].composite_draw(0, 'h', mano.x, mano.y + 31, 150, 150)
        else:
            mano.move_motion[int(mano.frame)].draw(mano.x, mano.y + 31, 150, 150)

class Attack():
    @staticmethod
    def enter(mano, e):
        mano.frame=0
        mano.start_time = get_time()
        mano.attack=False
        mano.skill_sound.play()
    @staticmethod
    def exit(mano, e):
        mano.start_time=0

    @staticmethod
    def do(mano):
        mano.frame = (mano.frame + FRAMES_PER_ACTION[2] * ACTION_PER_TIME[2] * game_framework.frame_time) % \
                     FRAMES_PER_ACTION[2]
        if mano.frame >5 and not mano.attack:
            mano_skill=mano_atatck(mano.x, mano.y)
            game_world.add_object(mano_skill, 3)
            game_world.add_collision_pair("player:mob", None, mano_skill)
            mano.attack=True
        if mano.frame >= FRAMES_PER_ACTION[2] -1 :
            mano.state_machine.add_event(("DONE", (0, 0)))

    @staticmethod
    def draw(mano):
        if mano.direction == 'l':
            mano.skill_motion[int(mano.frame)].composite_draw(0, 'h', mano.x, mano.y + 31 + mano_motion_y[int(mano.frame)], mano.skill_motion[int(mano.frame)].w *1.5, mano.skill_motion[int(mano.frame)].h *1.5)
        else:
            mano.skill_motion[int(mano.frame)].draw(mano.x, mano.y + 31+ mano_motion_y[int(mano.frame)], mano.skill_motion[int(mano.frame)].w *1.5, mano.skill_motion[int(mano.frame)].h *1.5)


class Mano:
    def __init__(self):
        self.font=load_font(config.font, 30)

        self.x=600
        self.y=115+config.up
        self.run_speed = ((5 * 1000) / 3600) * 10 / 0.3
        self.hp = 2000
        self.damage=150

        self.is_mush = False
        self.attack=False
        self.delay=0

        self.idle_motion =[load_image(loadfile.resource_path("mano_idle"+str(i)+".png")) for i in range(8)]
        self.move_motion = [load_image(loadfile.resource_path("mano_move" + str(i) + ".png")) for i in range(6)]
        self.skill_motion=[load_image(loadfile.resource_path("mano_skill"+str(i)+".png")) for i in range(10)]
        self.die_motion = [load_image(loadfile.resource_path("mano_die (" + str(i + 1) + ").png")) for i in range(9)]
        self.skill_sound=load_music(loadfile.resource_path("mano_skill.mp3"))
        self.skill_sound.set_volume(config.volume)
        self.hit_sound=load_music(loadfile.resource_path("mano_hit.mp3"))
        self.hit_sound.set_volume(config.volume)
        self.die_sound=load_music(loadfile.resource_path("mano_die.mp3"))
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
            self.font.draw(self.x - 50, self.y + 120, str(self.hp), (255, 255, 255))
    def handle_collision(self, group, other):
        if group =="skill:mob":
            if not other.is_hit:
                self.hp -= other.damage
                self.hit_sound.play()



class mano_atatck:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_hit = False
        self.start_time=get_time()
        self.damage = 170
        self.is_mush = False
    def draw(self):
        if config.debug_flag:
            draw_rectangle(*self.get_bb())

    def update(self):
        if get_time() - self.start_time>0.1:
            game_world.remove_object(self)
    def get_bb(self):
        # fill here
        return self.x -150, self.y -150, self.x +150, self.y+100

    def handle_collision(self, group, other):
        if group == "player.mob":
            self.is_hit = True


class Die:
    @staticmethod
    def enter(mano, e):
        mano.start_time = get_time()
        mano.frame=0
        mano.die_sound.play()
    @staticmethod
    def exit(mano, e):
        game_world.remove_object(mano)
        game_framework.push_mode(item_mode)
        #game_framework.change_mode(next_mod)
    @staticmethod
    def do(mano):
        mano.frame = (mano.frame + FRAMES_PER_ACTION[3]*ACTION_PER_TIME[3] * game_framework.frame_time)%FRAMES_PER_ACTION[3]
        if mano.frame >= FRAMES_PER_ACTION[3] -1 :
            mano.state_machine.add_event(("TIME_OUT", (0, 0)))

    @staticmethod
    def draw(mano):
        if mano.direction == 'r':
            mano.die_motion[int(mano.frame)].draw(mano.x, mano.y + 31, 150, 150)
        else:
            mano.die_motion[int(mano.frame)].composite_draw(0, 'h', mano.x, mano.y + 31, 150, 150)
