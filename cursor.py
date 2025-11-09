from pico2d import *
from worldmap import WorldMap
import ctypes
from sdl2.mouse import SDL_GetMouseState


class Cursor:
    def __init__(self):
        self.image = load_image('resource/character/Cursor.png')
        self.x = 0
        self.y = 0

    def update(self, camera=None):
        x = ctypes.c_int(0)
        y = ctypes.c_int(0)
        SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))

        screen_x = x.value
        screen_y = get_canvas_height() - y.value

        if camera:
            self.x, self.y = camera.screen_to_world(screen_x, screen_y)
        else:
            self.x, self.y = screen_x, screen_y

    def draw(self, camera=None):
        if camera:
            sx, sy = camera.apply(self.x, self.y)
        else:
            sx, sy = self.x, self.y

        self.image.draw(sx, sy, 56, 66)