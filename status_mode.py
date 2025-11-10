from pico2d import *
import game_framework
import game_playmode
from Attack import Attack
from weapon import weapon
import game_world
from worldmap import WorldMap


class State_UI:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = load_image(f'resource/character/CharacterUI_Base.png')
        pass

    def is_clicked(self, mx, my):
        pass
    def draw(self):
        self.image.draw(self.x, self.y, self.width, self.height)
        pass




def init():
    global char, state_ui
    char = game_playmode.char
    state_ui = State_UI(WorldMap.width/8, WorldMap.height/2, 320, 446)
    pass

def finish():
    pass

def update():
    game_world.update()
    pass


def draw():
    clear_canvas()
    game_world.render()
    state_ui.draw()
    game_world.render_cursor()
    update_canvas()


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE or event.key == SDLK_c:
                game_framework.pop_mode()
            else:
                char.handle_event(event, game_world.camera)
        elif event.type == SDL_KEYUP:
            char.handle_event(event, game_world.camera)
        elif event.type == SDL_MOUSEBUTTONDOWN or event.type == SDL_MOUSEBUTTONUP:
            char.handle_event(event, game_world.camera)


def pause():
    pass


def resume():
    pass
