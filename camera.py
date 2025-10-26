from pico2d import *
from worldmap import WorldMap

class Camera:
    def __init__(self, target):
        self.target = target
        self.x = 0
        self.y = 0
        self.screen_width = get_canvas_width()
        self.screen_height = get_canvas_height()
        self.zoom = 2.0
        pass
    def update(self):
        effective_width = self.screen_width / self.zoom
        effective_height = self.screen_height / self.zoom

        self.x = self.target.x - effective_width / 2
        self.y = self.target.y - effective_height / 2

        self.x = max(0, min(self.x, WorldMap.width - effective_width))
        self.y = max(0, min(self.y, WorldMap.height - effective_height))
        pass
    def apply(self, x, y):
        screen_x = (x - self.x) * self.zoom
        screen_y = (y - self.y) * self.zoom
        return screen_x, screen_y

    def screen_to_world(self, screen_x, screen_y):
        world_x = screen_x / self.zoom + self.x
        world_y = screen_y / self.zoom + self.y
        return world_x, world_y

    def set_for_draw(self):
        pass
    def unset_for_draw(self):
        pass