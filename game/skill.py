from pico2d import *
import game_framework
import game_world
from random import randint
import config
import loadfile

TIME_PER_ACTION = [0.68, 0.5, 0.78]
ACTION_PER_TIME = [1.0/i for i in TIME_PER_ACTION]
FRAMES_PER_ACTION = [15, 6, 11] # aura_blade, aura, brandish

aura_blade_y = [0, 0, -12, 15, 15]
aura_blade_x = [0, -30, -30, -0, 0]
brandish_x = [-20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20]
brandish_y = [-20, -5, 3, 0, -1, -18, -22, -30, -30, -35, -50]




class Aura_blade:
    def __init__(self, x, y, direction, ad):
        self.image =[load_image(loadfile.resource_path("aura_blade_effect (" + str(i+1)+").png")) for i in range(FRAMES_PER_ACTION[0])]
        self.frame=0
        self.x=x
        self.y=y
        self.type=0
        self.mp=50
        self.shoot=False
        self.ad=ad
        if direction == 'r':
            self.direction = 1
        else:
            self.direction = -1
    def draw(self):
        if self.direction == 1:
            self.image[int(self.frame)].draw(self.x - 50, self.y)
        else:
            self.image[int(self.frame)].composite_draw(0, 'h', self.x + 50, self.y)
    def update(self):
        if self.frame<FRAMES_PER_ACTION[self.type]-1:
            self.frame = (self.frame + FRAMES_PER_ACTION[self.type] * ACTION_PER_TIME[self.type] * game_framework.frame_time)
        else:
            game_world.remove_object(self)
        if self.frame > 7 and not self.shoot:
            aura =Aura(self.x, self.y, self.direction, self.ad)
            game_world.add_object(aura, 3)
            game_world.add_collision_pair("skill:mob", None, aura)
            self.shoot=True



class Aura:
    def __init__(self, x, y, direction, ad):
        self.image =[load_image(loadfile.resource_path("aura_shoot (" + str(i+1)+").png")) for i in range(FRAMES_PER_ACTION[1])]
        self.frame=0
        self.x=x
        self.y=y
        self.type = 1
        self.direction = direction
        self.speed=10
        self.damage=(1.8 * ad)+randint(-10, 10)
        self.is_hit=False
    def draw(self):
        if self.direction == -1:
            self.image[int(self.frame)].draw(self.x - 50, self.y, 480*0.6, 350*0.6)

        else:
            self.image[int(self.frame)].composite_draw(0, 'h', self.x + 50, self.y, 480*0.6, 350*0.6)

        if config.debug_flag:
            draw_rectangle(*self.get_bb())

    def update(self):
        self.frame = (self.frame + FRAMES_PER_ACTION[self.type] * ACTION_PER_TIME[
            self.type] * game_framework.frame_time) %FRAMES_PER_ACTION[self.type]
        self.x += self.direction * self.speed * 100 * game_framework.frame_time
        if self.x > 1500 or self.x < 0:
            game_world.remove_object(self)
    def get_bb(self):
        # fill here
        if self.direction == 1:
            return self.x +50, self.y -50, self.x+150, self.y+50
        else:
            return self.x - 150, self.y - 50, self.x - 50, self.y + 50
        pass
    def handle_collision(self, group, other):
        if group == "skill:mob":
            self.is_hit = True


class Brandish:
    def __init__(self, x, y, direction, ad):
        self.frame = 1
        self.x = x
        self.y = y
        self.type = 2
        self.image = [load_image(loadfile.resource_path("brandish_effect" + str(i) + ".png")) for i in range(FRAMES_PER_ACTION[self.type])]
        if direction == 'r':
            self.direction = 1
        else:
            self.direction = -1
        self.damage = (0.6 * ad) + randint(-4, 4)
        self.is_hit = False
        self.start_time=get_time()
    def draw(self):
        if self.direction == -1:
            self.image[int(self.frame)].draw(self.x  + brandish_x[int(self.frame)], self.y + brandish_y[int(self.frame)] + 30, 480 * 0.6, 350 * 0.6)

        else:
            self.image[int(self.frame)].composite_draw(0, 'h', self.x , self.y + brandish_y[int(self.frame)] + 30, 480 * 0.6, 350 * 0.6)

        if config.debug_flag:
            draw_rectangle(*self.get_bb())

    def update(self):
        if self.frame < FRAMES_PER_ACTION[self.type] - 1:
            self.frame = (self.frame + FRAMES_PER_ACTION[self.type] * ACTION_PER_TIME[
                self.type] * game_framework.frame_time)
        else:
            game_world.remove_object(self)
    def get_bb(self):
        # fill here
        if self.direction == 1:
            return self.x, self.y - 70, self.x + 120, self.y + 100
        else:
            return self.x - 130, self.y - 70, self.x , self.y + 90
        pass

    def handle_collision(self, group, other):
        if group == "skill:mob":
            self.is_hit = True

