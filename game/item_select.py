from pico2d import *
import random
import game_data
import config


from pico2d import load_image

class Items:
    def __init__(self):

        self.font = load_font(config.font, 20)
        self.item1 = random.randint(0, len(game_data.cards)-1)
        self.item2 = random.randint(0, len(game_data.cards)-1)
        while self.item1 == self.item2:
            self.item2 = random.randint(0, len(game_data.cards)-1)

    def draw(self):
        self.font.draw(config.width/2 - 100, config.height/2, "1." + str(game_data.cards[self.item1]), (255, 255, 255))
        self.font.draw(config.width/2 + 100, config.height/2, "2." + str(game_data.cards[self.item2]), (255, 255, 255))

    def update(self):

        pass