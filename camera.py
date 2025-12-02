from pico2d import *
from worldmap import WorldMap

class Camera:
    def __init__(self, target):
        self.target = target
        self.x = 0
        self.y = 0
        self.screen_width = get_canvas_width()
        self.screen_height = get_canvas_height()
        self.zoom = 3.5
        self.smooth = 0.2
        pass
    def update(self):
        effective_width = self.screen_width / self.zoom
        effective_height = self.screen_height / self.zoom

        target_x = self.target.x - effective_width / 2
        target_y = self.target.y - effective_height / 2

        target_x = max(0, min(target_x, WorldMap.width - effective_width))
        target_y = max(0, min(target_y, WorldMap.height - effective_height))

        # 선형 보간을 사용한 부드러운 카메라 이동
        self.x += (target_x - self.x) * self.smooth
        self.y += (target_y - self.y) * self.smooth
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