from pico2d import *
import game_framework
import game_world
import game_data
import config
import title_mode
import loadfile


def init():
    global font
    font = load_font(config.font, 20)



def finish():
    pass

def handle_events():
    events = get_events()

    for event in events:
        if event.type == SDL_KEYDOWN:
            match event.key:
                case pico2d.SDLK_1:
                    game_data.player_info = game_data.init_player_info
                    game_data.cards = game_data.init_cards
                    game_data.enhance = game_data.init_enhance
                    game_data.clear = False
                    game_framework.change_mode(title_mode)
                case pico2d.SDLK_2:
                    game_framework.quit()


def update():
    pass

def draw():

    if game_data.clear:
        font.draw(config.width/2-100, config.height/2 + 50, "승리를 축하합니다", (255, 255, 255))
        font.draw(config.width / 2 - 100, config.height / 2,"다시하기: 1 종료: 2", (255, 255, 255))
    else:
        font.draw(config.width / 2 - 100, config.height / 2 + 50, "사망하였습니다.", (255, 255, 255))
        font.draw(config.width / 2 - 100, config.height / 2, "다시하기: 1 종료: 2", (255, 255, 255))
    update_canvas()

def pause():
    pass
def resume():
    pass