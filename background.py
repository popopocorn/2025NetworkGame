from pico2d import *
import config
from random import randint
import loadfile


class Platform:
    def __init__(self,x=1050,y=120):

        self.platform = load_image(loadfile.resource_path("21.png"))
        self.platform = load_image(loadfile.resource_path("21.png"))

        self.platform = load_image(loadfile.resource_path("21.png"))
        self.platform = load_image(loadfile.resource_path("21.png"))

        self.platformxy = [x, y+config.up]
    def draw(self):
        self.platform.draw(self.platformxy[0], self.platformxy[1], 43, 50)
        self.platform.composite_draw(0, "h", self.platformxy[0]-43, self.platformxy[1], 43, 50)
        self.platform.composite_draw(0, "h", self.platformxy[0]-43-21.5, self.platformxy[1], 43, 50)
        if config.debug_flag:
            draw_rectangle(*self.get_bb())
    def update(self):
        pass
    def get_bb(self):
        return self.platformxy[0]-80, self.platformxy[1] - 20,self.platformxy[0]+15, self.platformxy[1] + 55
    def handle_collision(self, group, other):
        pass
    def not_collision(self, group, other):
        pass


class Background1:
    def __init__(self):
        self.floor = load_image(loadfile.resource_path("19.png"))
        self.back=load_image(loadfile.resource_path("back1.png"))
        self.sound=load_wav(loadfile.resource_path("bgm1.wav"))

        self.floor = load_image(loadfile.resource_path("19.png"))
        self.back=load_image(loadfile.resource_path("back1.png"))
        self.sound=load_wav(loadfile.resource_path("bgm1.wav"))

        self.floor = load_image(loadfile.resource_path("19.png"))
        self.back=load_image(loadfile.resource_path("back1.png"))
        self.sound=load_wav(loadfile.resource_path("bgm1.wav"))

        self.floor = load_image(loadfile.resource_path("19.png"))
        self.back=load_image(loadfile.resource_path("back1.png"))
        self.sound=load_wav(loadfile.resource_path("bgm1.wav"))

        self.sound.set_volume(config.volume)
        self.sound.repeat_play()
    def draw(self):
        self.back.draw(int(1600/1.5)/2,int( 900/1.5)/2+config.up)
        self.floor.draw(0, config.up)
        self.floor.draw(360, config.up)
        self.floor.draw(720, config.up)
        self.floor.draw(1080, config.up)
        self.floor.draw(1440, config.up)
        if config.debug_flag:
            draw_rectangle(*self.get_bb())
    def update(self):
        pass
    def get_bb(self):
        return 0, 0, config.width, config.up+76

class CavePlatform:
    def __init__(self,x=config.width/2,y=config.height/2):
        self.platform = [load_image(loadfile.resource_path("blue_cave_platform (" + str(i+1) + ").png")) for i in range(2)]
        self.platformxy = [x, y+config.up]
    def draw(self):
        self.platform[0].draw(self.platformxy[0], self.platformxy[1] + 10)
        self.platform[1].draw(self.platformxy[0] - 3, self.platformxy[1]-17)
        self.platform[0].draw(self.platformxy[0]-30, self.platformxy[1] + 10)
        self.platform[1].draw(self.platformxy[0] - 33, self.platformxy[1] - 17)
        self.platform[0].draw(self.platformxy[0] - 60, self.platformxy[1] + 10)
        self.platform[1].draw(self.platformxy[0] - 63, self.platformxy[1] - 17)
        if config.debug_flag:
            draw_rectangle(*self.get_bb())
    def update(self):
        pass
    def get_bb(self):
        return self.platformxy[0]-80, self.platformxy[1] - 20,self.platformxy[0]+15, self.platformxy[1] + 55
    def handle_collision(self, group, other):
        pass
    def not_collision(self, group, other):
        pass

class CaveGround:
    def __init__(self):
        self.back=load_image(loadfile.resource_path("barlog_back.png"))
        self.ground_up=[load_image(loadfile.resource_path("blue_cave_base_up (1).png")), load_image(loadfile.resource_path("blue_cave_base_up (2).png"))]
        self.ground_down = [load_image(loadfile.resource_path("blue_cave_base_down (" + str(i+1) + ").png")) for i in range(3)]
        self.ground_bottom = [load_image(loadfile.resource_path("blue_cave_base_bottom (" + str(i + 1) + ").png")) for i in range(2)]
        self.up_idx=[randint(0, 1)for _ in range(13)]
        self.down_idx = [randint(0, 2) for _ in range(13)]
        self.bottom_idx = [randint(0, 1) for _ in range(13)]
        self.sound = load_wav(loadfile.resource_path("bgm4.wav"))
        self.sound.set_volume(config.volume)
        self.sound.repeat_play()

    def draw(self):
        self.back.draw(config.width/2, config.height/2)
        for i in range(13):
            self.ground_up[self.up_idx[i]].draw(i*90, config.up+65, 90, 24)
            self.ground_down[self.down_idx[i]].draw(i*90, config.up + 23, 90, 60)
            self.ground_bottom[self.bottom_idx[i]].draw(i*90, config.up - 25, 90, 35)


        if config.debug_flag:
            draw_rectangle(*self.get_bb())
    def update(self):
        pass
    def get_bb(self):
        return 0, 0, config.width, config.up+76

class BlockPlatform:
    def __init__(self,x=config.width/2,y=config.height/2):
        self.platform = [load_image(loadfile.resource_path("block_platform (" + str(i+1) + ").png")) for i in range(2)]
        self.platformxy = [x, y + config.up]
    def draw(self):
        self.platform[0].draw(self.platformxy[0] - 50, self.platformxy[1] + 10)
        self.platform[1].draw(self.platformxy[0] - 50, self.platformxy[1] - 10)
        self.platform[0].draw(self.platformxy[0] - 10, self.platformxy[1] + 10)
        self.platform[1].draw(self.platformxy[0] - 10, self.platformxy[1] - 10)

        if config.debug_flag:
            draw_rectangle(*self.get_bb())
    def update(self):
        pass
    def get_bb(self):
        return self.platformxy[0]-80, self.platformxy[1] - 20,self.platformxy[0]+15, self.platformxy[1] + 55
    def handle_collision(self, group, other):
        pass
    def not_collision(self, group, other):
        pass

class BlockGround:
    def __init__(self):
        self.back=load_image(loadfile.resource_path("timer_back.png"))
        self.ground_up=[load_image(loadfile.resource_path("blue_block_base_up (" + str(i+1) + ").png")) for i in range(3)]
        self.ground_down = [load_image(loadfile.resource_path("blue_block_base (" + str(i+1) + ").png")) for i in range(6)]
        self.ground_bottom = [load_image(loadfile.resource_path("blue_block_base_bottom (" + str(i + 1) + ").png")) for i in range(3)]
        self.up_idx=[randint(0, 2)for _ in range(13)]
        self.down_idx = [randint(0, 5) for _ in range(13)]
        self.bottom_idx = [randint(0, 2) for _ in range(13)]
        self.sound = load_wav(loadfile.resource_path("bgm3.wav"))
        self.sound.set_volume(config.volume)
        self.sound.repeat_play()
    def draw(self):
        self.back.draw(config.width / 2, config.height / 2)
        for i in range(13):
            self.ground_up[self.up_idx[i]].draw(i*90, config.up+65, 90, 24)
            self.ground_down[self.down_idx[i]].draw(i*90, config.up + 23, 90, 60)
            self.ground_bottom[self.bottom_idx[i]].draw(i*90, config.up - 25, 90, 35)


        if config.debug_flag:
            draw_rectangle(*self.get_bb())
    def update(self):
        pass
    def get_bb(self):
        return 0, 0, config.width, config.up+76


if __name__ == "__main__":
    open_canvas(config.width, config.height)
    bg=CaveGround()
    pl=BlockPlatform()

    bg.draw()
    pl.draw()
    update_canvas()
    input()