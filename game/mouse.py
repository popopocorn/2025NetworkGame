from pico2d import *
from config import *
class mouse:
    def __init__(self):
        self.image = [[], []]
        self.mouse_state=0
        self.x=width/2
        self.y=height/2
    def draw(self):

        if debug_flag:
            draw_rectangle(*self.get_bb())
    def update(self):
        pass
    def get_bb(self):
        pass
    def handle_collision(self, group, other):
        pass
    def not_collision(self, group, other):
        pass