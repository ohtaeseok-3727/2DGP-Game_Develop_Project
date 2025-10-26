from pico2d import *
from worldmap import *
import ctypes
import sdl2
from OpenGL.GL import *

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

        self.x = max(0, min(self.x, WorldMap.width - self.screen_width))
        self.y = max(0, min(self.y, WorldMap.height - self.screen_height))
        pass
    def set_for_draw(self):
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glTranslatef(-self.x, -self.y, 0)
        pass
    def unset_for_draw(self):
        glPopMatrix()
        pass