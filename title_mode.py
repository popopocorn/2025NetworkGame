from pico2d import *
import game_framework
import play_mode as next
import config
import loadfile

def init():
    global image, notice, title, sound
    sound = load_music(loadfile.resource_path("title.mp3"))
    image = load_image(loadfile.resource_path("back1.png"))
    notice = load_font(config.font, 30)
    title = load_font(config.font, 60)
    sound.set_volume(config.volume)
    sound.repeat_play()
def finish():
    global image, notice, title, sound
    del image
    del notice
    del title
    del sound

def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            else:
                game_framework.change_mode(next)



def update():
    pass

def draw():
    clear_canvas()
    image.draw(config.width/2, config.height/2)
    title.draw(config.width / 2 - 125, config.height / 2, "히어로그", (255, 255, 255))
    notice.draw(config.width/2-175, config.height/2 - 150, "Press Any Key To Start", (255, 255, 255))
    update_canvas()


def pause():
    pass
def resume():
    pass