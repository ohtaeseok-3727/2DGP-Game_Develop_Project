from pico2d import *
import game_framework
import game_playmode


def init():
    global running
    running = True


def draw():
    clear_canvas()
    update_canvas()

def update():
    pass

def finish():
    pass

def handle_events():
    events = get_events() #이벤트를 받아서 아무것도 하지않는다.
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            game_framework.change_mode(game_playmode)
