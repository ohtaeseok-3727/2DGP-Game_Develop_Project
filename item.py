from pico2d import *
import math
import game_framework
import game_world
from state_machine import StateMachine

class Item:
    images = {}
    def __init__(self, x, y, item_type):
        self.x=x
        self.y=y
        self.item_type = item_type

        # 아이템 이미지 로드
        if item_type not in Item.images:
            try:
                Item.images[item_type] = load_image(f'resource/item/{item_type}.png')
            except:
                print(f'이미지 로드 실패: {item_type}')
                Item.images[item_type] = None

        self.image = Item.images.get(item_type)

        self.item_effects = {
            'AmuletOfAspiration': {'critical': 0.05},
            'AncientAnvil': {'ATK': 5},
            'Aquamarine': {'max_hp': 20},
            'ArtificialSpiritIfiel': {'critical_damage': 0.2},
            'AstronomicalTelescope': {'critical_damage': 0.5},
            'BlackScales': {'critical': 0.3},
            'BlackteaBag': {'max_hp': 15},
            'BladeOfLight': {'ATK': 10},
            'BloodOfObrus': {'max_hp': 30},
            'BloodstoneRing': {'critical': 0.5},
            'BloodTear': {'max_hp': 50},
            'BlueBand': {'ATK': 20},
            'BlueBohoBracelet': {'critical': 0.15},
            'BlueInkBottle': {'critical_damage': 0.3},
            'BluePearl': {'max_hp': 25},
            'BlueRing': {'ATK': 5},
            'BluntBellKnife': {'critical': 0.1},
            'CrownOfPride': {'critical': 0.7}
        }

    def apply_effect(self, character):
        effects = self.item_effects.get(self.item_type, {})

        for stat, value in effects.items():
            if stat == 'ATK':
                character.ATK += value
            elif stat == 'max_hp':
                character.max_hp += value
                character.now_hp += value
            elif stat == 'critical':
                character.critical += value
            elif stat == 'critical_damage':
                character.critical_damage += value

    def get_bb(self):
        return self.x - 10, self.y - 10, self.x + 10, self.y + 10

    def update(self):
        pass

    def draw(self, camera=None):
        if self.image and camera:
            sx, sy = camera.apply(self.x, self.y)
            zoom = camera.zoom
            self.image.draw(sx, sy, 20 * zoom, 20 * zoom)
        pass

