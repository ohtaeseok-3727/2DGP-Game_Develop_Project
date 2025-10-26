from pico2d import *

class Camera:
    def __init__(self, target):
        self.target = target
        self.x = 0
        self.y = 0
        self.screen_width = get_canvas_width()
        self.screen_height = get_canvas_height()
        pass
    def update(self):
        self.x = self.target.x - self.screen_width // 2
        self.y = self.target.y - self.screen_height // 2
        pass
    def set_for_draw(self):
        pass
    def unset_for_draw(self):
        pass