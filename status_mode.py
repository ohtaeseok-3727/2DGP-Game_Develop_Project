from pico2d import *
import game_framework
import game_playmode
from Attack import Attack
from weapon import weapon
import game_world


class UpgradeButton:
    def __init__(self, x, y, width, height, rank, text):
        pass

    def is_clicked(self, mx, my):
        pass
    def draw(self):
        pass




def init():
    pass

def finish():
    pass

def update():
    game_world.update()
    pass


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE or event.key == SDLK_f:
                game_framework.pop_mode()
        elif event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            mx, my = event.x, get_canvas_height() - event.y


def pause():
    pass


def resume():
    pass
