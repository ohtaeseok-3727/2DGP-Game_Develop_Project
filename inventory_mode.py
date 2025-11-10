from pico2d import *
import game_framework
import game_playmode
from Attack import Attack
from weapon import weapon
import game_world
from worldmap import WorldMap


class Back:
    image = None
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.image = load_image(f'resource/UI/inventory.png')

    def is_clicked(self, mx, my):
        return (self.x - self.width // 2 < mx < self.x + self.width // 2 and
                self.y - self.height // 2 < my < self.y + self.height // 2)

    def draw(self):
        self.image.draw(self.x, self.y, self.width, self.height)




def init():
    global char, back_ui
    char = game_playmode.char
    back_ui = Back(WorldMap.width/2, WorldMap.height/2, 846, 528)
    pass

def finish():
    pass

def update():
    game_world.update()
    pass


def draw():
    clear_canvas()
    game_world.render()
    back_ui.draw()
    game_world.render_cursor()
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
