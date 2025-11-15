from pico2d import *
import game_framework
import game_playmode
from Attack import Attack
from weapon import weapon
import game_world
from worldmap import WorldMap

class itmeslot:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.item = None
        self.hovered = False

    def set_item(self, item):
        self.item = item


    def is_clicked(self, mx, my):
        return (self.x - self.width // 2 < mx < self.x + self.width // 2 and
                self.y - self.height // 2 < my < self.y + self.height // 2)

    def is_hovered(self, mx, my):
        half = self.size//2
        return (self.x - half < mx < self.x + half and
                self.y - half < my < self.y + half)

    def draw(self):
        color = (255, 255, 100) if self.hovered else (200, 200, 200)
        draw_rectangle(self.x - self.size // 2, self.y - self.size // 2,
                       self.x + self.size // 2, self.y + self.size // 2, color)
        if self.item and self.item.image:
            self.item.image.draw(self.x, self.y, self.size - 10, self.size - 10)


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
        screen_x = get_canvas_width() // 2
        screen_y = get_canvas_height() // 2
        self.image.draw(screen_x, screen_y, self.width, self.height)




def init():
    global char, back_ui
    char = game_playmode.char
    back_ui = Back(get_canvas_width() // 2, get_canvas_height() // 2, 846, 528)
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
            if event.key == SDLK_ESCAPE or event.key == SDLK_v:
                game_framework.pop_mode()
        elif event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            mx, my = event.x, get_canvas_height() - event.y


def pause():
    pass


def resume():
    pass
