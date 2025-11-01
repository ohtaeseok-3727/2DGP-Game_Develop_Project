import ctypes
import math

from pico2d import load_image
from sdl2 import SDL_GetMouseState

from worldmap import WorldMap


class weapon:
    #기본 카타나
    default_katana = {'name': '기본 카타나', 'damage': 0, 'attack_width' :40, 'attack_height': 88, 'speed': 1.0}
    #무라마사(평타 강화 : 2회 연속 공격)
    katana_muramasa = {'name': '무라마사', 'damage': 0, 'attack_width' :66, 'attack_height': 133, 'speed': 1.2}
    #호우(원거리 평타)
    katana_hou = {'name': '호우', 'damage': 0, 'width' :79, 'attack_height': 79, 'attack_speed': 1.0}
    #기본 대검
    default_greatsword = {'name': '기본 대검', 'damage': 0, 'attack1_width' :70, 'attack1_height': 66, 'attack2_width' :75, 'attack2_height': 74, 'speed': 0.8}
    #쯔바이핸더(평타 강화)
    greatsword_zweihander = {'name': '쯔바이핸더', 'damage': 0, 'attack1_width' :90, 'attack1_height': 82, 'attack2_width' :100, 'attack2_height': 98, 'speed': 1.0}
    #브레이커(특수 기술 생성)
    greatsword_breaker = {'name': '브레이커', 'damage': 0, 'attack1_width' :74, 'attack1_height': 111, 'attack2_width' :120, 'attack2_height': 116, 'speed': 0.9}

    image = None

    def __init__(self, character):
        self.character = character
        self.x = character.x
        self.y = character.y

        self.angle = 0
        # 캐릭터 중심에서 손까지의 거리
        self.hand_distance = 4
        # 손에서 카타나 중심까지의 거리 (카타나 길이의 절반 정도)
        self.katana_offset = 5

        if self.character.weapon_type == 'katana':
            if self.character.weapon_rank == 0:
                weapon.image = load_image('resource/weapon/katana/katana_Default.png')
            elif self.character.weapon_rank == 1:
                weapon.image = load_image('resource/weapon/katana/katana_Hou.png')
            elif self.character.weapon_rank == 2:
                weapon.image = load_image('resource/weapon/katana/katana_Muramasa.png')
        pass

    def update(self, camera=None):
        x = ctypes.c_int(0)
        y = ctypes.c_int(0)
        SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))

        screen_x = x.value
        screen_y = WorldMap.height - y.value

        # 카메라가 있으면 스크린 좌표를 월드 좌표로 변환
        if camera:
            mx, my = camera.screen_to_world(screen_x, screen_y)
        else:
            mx, my = screen_x, screen_y

        dx = mx - self.character.x
        dy = my - self.character.y

        mouse_angle = math.atan2(dy, dx)

        if dx >= 0:
            katana_angle = mouse_angle - math.pi / 2
        else:
            katana_angle = mouse_angle + math.pi / 2

        self.x = self.character.x + math.cos(katana_angle) * self.katana_offset
        self.y = self.character.y + math.sin(katana_angle) * self.katana_offset - 5

        self.angle = mouse_angle

    def draw(self, camera=None):
        draw_angle = math.degrees(self.angle) + 90 + 180
        zoom = camera.zoom if camera else 1.0

        draw_x, draw_y = (camera.apply(self.x, self.y)) if camera else (self.x, self.y)

        if self.character.face_dir == 1:
            weapon.image.clip_composite_draw(
                0, 0, 14, 40,
                math.radians(draw_angle), 'h',
                draw_x, draw_y,
                14 * zoom, 40 * zoom
            )
        else:
            weapon.image.clip_composite_draw(
                0, 0, 14, 40,
                math.radians(draw_angle), '',
                draw_x, draw_y,
                14 * zoom, 40 * zoom
            )
