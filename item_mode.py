from pico2d import *
import game_framework
import game_world
import play_mode as next
import game_data
from item_select import Items

is_selected = False

def init():
    global items
    items = Items()
    game_world.add_object(items, 3)


def finish():
    game_world.remove_object(items)

def handle_events():
    global is_selected, items
    events = get_events()

    for event in events:
        if event.type == SDL_KEYDOWN:
            match event.key:
                case pico2d.SDLK_1:
                    is_selected = True
                    game_data.enhance.append(game_data.cards[items.item1])
                    game_data.cards.pop(items.item1)

                    game_framework.pop_mode()
                case pico2d.SDLK_2:
                    is_selected = True
                    game_data.enhance.append(game_data.cards[items.item2])
                    game_data.cards.pop(items.item2)

                    game_framework.pop_mode()


def update():
    pass

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def pause():
    pass
def resume():
    pass