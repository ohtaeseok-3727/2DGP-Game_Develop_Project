from pico2d import *
import math
from worldmap import WorldMap
import game_framework

class anvil:
    def __init__(self):
        self.image = load_image('resource/object/Anvil.png')
        self.x = 300
        self.y = 200
        self.interaction_range = 30

        self.frame_width = 12
        self.frame_height = 15
        self.total_frames = 11
        self.current_frame = 0
        self.frame_time = 0
        self.fps = 10
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
        self.image = load_image('resource/object/Sephirite_SpriteSheet.png')
        self.x = 400
        self.y = 300
        self.interaction_range = 30
        pass
    def update(self, camera=None):
        self.frame_time += game_framework.frame_time

        if self.frame_time > 1.0 / self.fps:
            self.current_frame = (self.current_frame + 1) % self.total_frames
            self.frame_time = 0
        pass
    def in_range(self, character):
        distance = math.sqrt((self.x - character.x) ** 2 + (self.y - character.y) ** 2)
        return distance <= self.interaction_range
        pass

    def draw(self, camera=None):
        if camera:
            sx, sy = camera.apply(self.x, self.y)
            zoom = camera.zoom
        else:
            sx, sy = self.x, self.y
            zoom = 1.0

        frame_x = int(self.current_frame) * self.frame_width

        Sephrite.image.clip_draw(
            frame_x, 0,
            self.frame_width, self.frame_height,
            sx, sy,
            self.frame_width * zoom, self.frame_height * zoom
        )
    def get_bb(self):
        return self.x - 6, self.y - 7, self.x + 6, self.y + 7