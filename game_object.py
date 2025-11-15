from pico2d import *
import math
from worldmap import WorldMap


class anvil:
    def __init__(self):
        self.image = load_image('resource/object/Anvil.png')
        self.x = 300
        self.y = 200
        self.interaction_range = 30
    def update(self, camera=None):
        pass
    def in_range(self, character):
        distance = math.sqrt((self.x - character.x) ** 2 + (self.y - character.y) ** 2)
        return distance <= self.interaction_range
    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.x, self.y)
            zoom = camera.zoom
            self.image.draw(screen_x, screen_y,
                          self.image.w * zoom,
                          self.image.h * zoom)
        else:
            self.image.draw(self.x, self.y)


class Sephrite:
    def __init__(self):
        pass
    def update(self, camera=None):
        pass
    def in_range(self, character):
        pass

    def draw(self, camera=None):
        pass