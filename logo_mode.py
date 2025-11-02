from pico2d import *
import game_framework
import title_mode as next
import config
import loadfile

TIME_PER_ACTION = 2
ACTION_PER_TIME = 1.0/TIME_PER_ACTION
FRAMES_PER_ACTION = 55


def init():
    global image
    global running
    global logo_start_time
    global logo_frame, sound
    sound = load_music(loadfile.resource_path("logo.mp3"))
    sound.set_volume(config.volume)
    sound.play()
    image=[load_image(loadfile.resource_path("Wizet (" + str(i+1) + ").png")) for i in range(55)]
    running=True
    logo_start_time=get_time()
    logo_frame=0

def finish():
    global image
    del image

def update():
    global running
    global logo_start_time, logo_frame
    logo_frame = (logo_frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % \
                   FRAMES_PER_ACTION
    if get_time()-logo_start_time>= 2:
        logo_start_time=get_time()
        game_framework.change_mode(next)
def draw():
    global image, logo_frame
    clear_canvas()
    image[int(logo_frame)].draw((1600/1.5)/2, (900/1.2)/2)
    image[0].clip_draw(0, 0, 100, 100, 0, 350, 100, 800)
    image[0].clip_draw(0, 0, 100, 100, (1600/1.5), 350, 100, 800)
    update_canvas()

def handle_events():
    events=get_events()

def pause():
    pass
def resume():
    pass