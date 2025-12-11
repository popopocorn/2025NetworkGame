from unittest.mock import sentinel

from pico2d import *
import config
import game_data
import loadfile
import network

class Player_status:
    def __init__(self):
        self.status_base=load_image(loadfile.resource_path("status_bar.png"))
        self.hp_bar=load_image(loadfile.resource_path("hp.png"))
        self.mp_bar=load_image(loadfile.resource_path("mp.png"))
        self.alpha=load_image(loadfile.resource_path("gauge.png"))
        self.hper = 100
        self.mper = 100
        self.font=load_font(config.font, 25)
        self.font2 = load_font(config.font, 15)


    def draw(self):
        self.status_base.draw(config.width/2 - 100, 60, 570 * 1.5, 71 * 1.5)
        self.hp_bar.clip_draw_to_origin(0, 0, int(108 * (self.hper / 100)), 18, config.width / 2 - 200, 25)
        self.alpha.clip_draw_to_origin(0, 0, 108, 18, config.width / 2 - 200, 25)
        self.mp_bar.clip_draw_to_origin(0, 0, int(108 * (self.mper / 100)), 18, config.width / 2 - 50, 25)
        self.alpha.clip_draw_to_origin(0, 0, 108, 18, config.width / 2 - 50, 25)
        self.font.draw(75, 40, "60", (255, 255, 255))
        self.font.draw(150,40, "Zl존 히어로", (255, 255, 255))

        self.font2.draw( config.width / 2 - 200, 50, "hp: " + str(int(game_data.php)), (255, 255, 255))
        self.font2.draw( config.width / 2 - 50, 50, "mp: " + str(int(game_data.pmp)), (255, 255, 255))
    def update(self):
        self.hper = (game_data.php/game_data.mhp)*100
        self.mper = (game_data.pmp / game_data.mmp) * 100

    def handle_events(self, player_info):
        pass
    def get_bb(self):
        return 0, 0, 0, 0
    def handle_collision(self, group, other):
        pass

class matchUI:
    def __init__(self):
        self.font=load_font(config.font, 25)
        self.image = load_image(loadfile.resource_path("back1.png"))
        self.sentence = "매칭 대기중..."
    def draw(self):
        self.image.draw(config.width/2, config.height/2)
        self.font.draw(config.width/2 - 100 , config.height/2, self.sentence, (255, 255, 255))
    def setText(self, text):
        self.sentence = text
    def update(self):
        pass

    def handle_events(self, player_info):
        pass
    def get_bb(self):
        return 0, 0, 0, 0
    def handle_collision(self, group, other):
        pass

class scoreUI:
    def __init__(self):
        self.font=load_font(config.font, 25)
        self.image = load_image(loadfile.resource_path("back1.png"))
        scores = network.game_score

        self.scores =[f"내 점수:         {scores[0]}",
        f"플레이어 1 점수:  {scores[1]}",
        f"플레이어 2 점수:  {scores[2]}"]

    def draw(self):
        self.image.draw(config.width/2, config.height/2)
        for i in range(3):
            self.font.draw(config.width/2- 100 , config.height/2 - i*100, self.scores[i], (255, 255, 255))

    def setText(self, text):
        self.sentence = text
    def update(self):
        pass

    def handle_events(self, player_info):
        pass
    def get_bb(self):
        return 0, 0, 0, 0
    def handle_collision(self, group, other):
        pass




class RemainingTimeUI:
    def __init__(self):
        self.font=load_font(config.font, 25)
        self.sentence = str()
    def draw(self):
        color = (255, 255, 255)
        if game_data.remaining_time < 11.0:
            color = (255, 0, 0)


        self.font.draw(config.width / 2 + config.width / 8, 30, self.sentence, color)

    def update(self):
        self.sentence = str()
        min = int(game_data.remaining_time) // 60
        sec = int(game_data.remaining_time) % 60
        if min >= 10:
            self.sentence += str(min)
        else:
            self.sentence += '0'
            self.sentence += str(min)
        self.sentence += ':'
        if sec >= 10:
            self.sentence += str(sec)
        else:
            self.sentence += '0'
            self.sentence += str(sec)


    def handle_events(self, player_info):
        pass
    def get_bb(self):
        return 0, 0, 0, 0
    def handle_collision(self, group, other):
        pass