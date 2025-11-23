from pico2d import *
import math
from worldmap import WorldMap
import game_framework

TIME_PER_ACTION = 0.01
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION

class anvil:
    def __init__(self, x, y):
        self.image = load_image('resource/object/Anvil.png')
        self.x = x
        self.y = y
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


class Sephirite:
    def __init__(self, x, y):
        self.image = load_image('resource/object/Sephirite_SpriteSheet.png')
        self.x = x
        self.y = y
        self.interaction_range = 30

        self.frame_width = 12
        self.frame_height = 15
        self.total_frames = 11
        self.current_frame = 0
        self.frame_time = 0
        self.fps = 10
        pass
    def update(self, camera=None):
        if get_time() - self.frame_time > 1.0 / self.fps:
            self.current_frame = (self.current_frame + ACTION_PER_TIME * self.total_frames * game_framework.frame_time) % self.total_frames
            self.frame_time = get_time()
        pass
    def in_range(self, character):
        distance = math.sqrt((self.x - character.x) ** 2 + (self.y - character.y) ** 2)
        return distance <= self.interaction_range

    def draw(self, camera=None):
        if camera:
            sx, sy = camera.apply(self.x, self.y)
            zoom = camera.zoom
        else:
            sx, sy = self.x, self.y
            zoom = 1.0

        frame_x = int(self.current_frame) * self.frame_width

        self.image.clip_draw(
            frame_x, 0,
            self.frame_width, self.frame_height,
            sx, sy,
            self.frame_width * zoom, self.frame_height * zoom
        )

    def get_bb(self):
        return self.x - 6, self.y - 7, self.x + 6, self.y + 7

class Portal:
    def __init__(self, x, y):
        self.image = load_image('resource/object/Portal_SpriteSheet.png')
        self.x = x
        self.y = y
        self.interaction_range = 30

        self.frame_width = 64
        self.frame_height = 64
        self.total_frames = 7
        self.current_frame = 0
        self.frame_time = 0
        self.fps = 10

        self.current_wave = 0
        self.max_waves = 3
        self.monsters_per_wave = 10
        self.wave_completed = False

    def interact(self):
        """포탈 상호작용 - 몬스터 소환"""
        if self.current_wave >= self.max_waves:
            return False, "모든 웨이브가 완료되었습니다!"

        self.current_wave += 1
        return True, f"웨이브 {self.current_wave} 시작!"

    def is_all_waves_complete(self):
        return self.current_wave >= self.max_waves

    def update(self, camera=None):
        self.frame_time += game_framework.frame_time

        if self.frame_time > 1.0 / self.fps:
            self.current_frame = (self.current_frame + ACTION_PER_TIME * self.total_frames * game_framework.frame_time) % self.total_frames
            self.frame_time = 0

    def in_range(self, character):
        distance = math.sqrt((self.x - character.x) ** 2 + (self.y - character.y) ** 2)
        return distance <= self.interaction_range

    def draw(self, camera=None):
        if not self.image:
            return

        if camera:
            sx, sy = camera.apply(self.x, self.y)
            zoom = camera.zoom
        else:
            sx, sy = self.x, self.y
            zoom = 1.0

        frame_x = int(self.current_frame) * self.frame_width
        self.image.clip_draw(
            frame_x, 0,
            self.frame_width, self.frame_height,
            sx, sy,
            self.frame_width * zoom, self.frame_height * zoom
        )

    def get_bb(self, camera=None):
        half_w = (self.frame_width / 2)
        half_h = (self.frame_height / 2)
        left, bottom, right, top = self.x - half_w, self.y - half_h, self.x + half_w, self.y + half_h

        if camera:
            sl, sb = camera.apply(left, bottom)
            sr, st = camera.apply(right, top)
            return sl, sb, sr, st
        return left, bottom, right, top

class Tree:
    def __init__(self, x, y):
        self.image = load_image('resource/title/N_Title_Tree_SpriteSheet.png')
        self.x = x
        self.y = y
        self.interaction_range = 30

        self.frame_width = 147
        self.frame_height = 155
        self.total_frames = 16
        self.current_frame = 0
        self.frame_time = 0
        self.fps = 10
        pass
    def update(self, camera=None):
        if get_time() - self.frame_time > 1.0 / self.fps:
            self.current_frame = (self.current_frame + ACTION_PER_TIME * self.total_frames * game_framework.frame_time) % self.total_frames
            self.frame_time = get_time()
        pass
    def in_range(self, character):
        pass

    def draw(self, camera=None):

        frame_x = int(self.current_frame) * self.frame_width

        self.image.clip_draw(
            frame_x, 0,
            self.frame_width, self.frame_height,
            self.x, self.y,
            self.frame_width * 1.5, self.frame_height * 1.5
        )

    def get_bb(self):
        pass

class building:
    image = None
    def __init__(self, x, y, building_type):
        self.x = x
        self.y = y
        self.building_type = building_type
        if building_type == 1:
            building.image = load_image('resource/map/broken_building1.png')
            self.width = 477
            self.height = 123
        if building_type == 2:
            building.image = load_image('resource/map/broken_building2.png')
            self.width = 56
            self.height = 76
        if building_type == 3:
            building.image = load_image('resource/map/broken_building3.png')
            self.width = 54
            self.height = 61
        if building_type == 4:
            building.image = load_image('resource/map/broken_building4.png')
            self.width = 54
            self.height = 43
        if building_type == 5:
            building.image = load_image('resource/map/broken_building5.png')
            self.width = 54
            self.height = 61
        if building_type == 6:
            building.image = load_image('resource/map/broken_building6.png')
            self.width = 55
            self.height = 42
        if building_type == 7:
            building.image = load_image('resource/map/broken_building7.png')
            self.width = 72
            self.height = 73
    def update(self, camera=None):

        pass
    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(self.x, self.y)
            zoom = camera.zoom
            self.image.draw(screen_x, screen_y,
                          self.image.w * zoom,
                          self.image.h * zoom)
        else:
            self.image.draw(self.x, self.y)
    def get_bb(self, camera=None):
        half_w = self.width / 2
        half_h = self.height / 2
        left, bottom, right, top = self.x - half_w, self.y - half_h, self.x + half_w, self.y + half_h

        if camera:
            sl, sb = camera.apply(left, bottom)
            sr, st = camera.apply(right, top)
            return sl, sb, sr, st
        return left, bottom, right, top
