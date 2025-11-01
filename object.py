from pico2d import *
import math
from worldmap import WorldMap


class anvil:
    def __init__(self):
        self.image = load_image('resource/object/Anvil.png')
        self.x = 300
        self.y = 200
        self.interaction_x1 = self.x - 20
        self.interaction_x2 = self.x + 20
        self.interaction_y1 = self.y - 20
        self.interaction_y2 = self.y + 20
    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.x, self.y)
            zoom = camera.zoom
            self.image.draw(screen_x, screen_y,
                          self.image.w * zoom,
                          self.image.h * zoom)
        else:
            self.image.draw(self.x, self.y)