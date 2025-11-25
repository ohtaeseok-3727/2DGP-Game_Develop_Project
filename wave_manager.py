import random
import math
from pico2d import *
import game_world
import game_framework
import upgrade_mode
import item_selection_mode
from worldmap import WorldMap
from monster import Monster
from game_object import anvil, Sephirite


class WaveSpawner:
    def __init__(self, portal, char, monsters, buildings):
        self.portal = portal
        self.char = char
        self.monsters = monsters
        self.buildings = buildings
        self.current_wave = 0
        self.current_phase = 0
        self.is_wave_active = False
        self.phase_monsters_spawned = False

    def start_wave(self, wave_number):
        """웨이브 시작"""
        self.current_wave = wave_number
        self.current_phase = 0
        self.is_wave_active = True
        self.phase_monsters_spawned = False
        print(f"웨이브 {wave_number} 시작!")

    def check_and_spawn_next_phase(self, remaining_monsters):
        """몬스터가 모두 처치되면 다음 페이즈 소환"""
        if not self.is_wave_active:
            return False

        if remaining_monsters == 0 and self.phase_monsters_spawned:
            self.current_phase += 1
            self.phase_monsters_spawned = False

            if self.current_phase >= 3:
                self.is_wave_active = False
                print(f"웨이브 {self.current_wave} 완료!")
                return False

        if not self.phase_monsters_spawned:
            self._spawn_phase_monsters()
            self.phase_monsters_spawned = True
            return True

        return False

    def _spawn_phase_monsters(self):
        """현재 페이즈의 몬스터 소환"""
        spawn_count = self.portal.monsters_per_wave

        print(f"웨이브 {self.current_wave} - 페이즈 {self.current_phase + 1}/3: {spawn_count}마리 소환")

        for i in range(spawn_count):
            spawn_x, spawn_y = self._find_valid_spawn_position()

            if self.current_wave == 1:
                monster_type = 'small_blue_slime'
            elif self.current_wave == 2:
                monster_type = 'small_blue_slime' if i < 7 else 'blue_slime'
            else:
                monster_type = 'blue_slime'

            monster = Monster(spawn_x, spawn_y, monster_type, 1 + self.current_wave * 0.5)
            monster.set_target(self.char)
            game_world.add_object(monster, 2)
            self.monsters.append(monster)

            game_world.add_collision_pairs('monster:monster', None, monster)
            game_world.add_collision_pairs('monster:monster', monster, None)

    def _find_valid_spawn_position(self):
        """유효한 소환 위치 찾기"""
        max_attempts = 50
        for attempt in range(max_attempts):
            angle = random.uniform(0, 2 * 3.14159)
            distance = random.randint(100, 200)
            spawn_x = self.portal.x + distance * math.cos(angle)
            spawn_y = self.portal.y + distance * math.sin(angle)

            spawn_x = max(50, min(spawn_x, WorldMap.width - 50))
            spawn_y = max(50, min(spawn_y, WorldMap.height - 50))

            if is_valid_spawn_position(spawn_x, spawn_y, self.buildings):
                return spawn_x, spawn_y

        return spawn_x, spawn_y

    def is_wave_complete(self):
        """웨이브가 완전히 완료되었는지 확인"""
        return not self.is_wave_active and self.current_phase >= 3


class RewardManager:
    def __init__(self, portal):
        self.portal = portal
        self.wave_rewards_spawned = {1: False, 2: False, 3: False}
        self.sephirites = []
        self.anvil = None

    def spawn_rewards(self, wave_num, remaining_monsters):
        if remaining_monsters > 0:
            return

        if wave_num == 1 and not self.wave_rewards_spawned[1]:
            if not self.anvil:
                self.anvil = anvil(350, 250)
                game_world.add_object(self.anvil, 1)
            self._spawn_sephirites(1)
            self.wave_rewards_spawned[1] = True

        elif wave_num == 2 and not self.wave_rewards_spawned[2]:
            self._spawn_sephirites(2)
            self.wave_rewards_spawned[2] = True

        elif wave_num == 3 and not self.wave_rewards_spawned[3]:
            self._spawn_sephirites(3)
            self.wave_rewards_spawned[3] = True

    def _spawn_sephirites(self, count):
        spawn_positions = [self.portal.x, self.portal.x + 30, self.portal.x + 60]

        for i in range(count):
            y = self.portal.y - 50
            x = spawn_positions[i]

            x = max(50, min(x, WorldMap.width - 50))
            y = max(50, min(y, WorldMap.height - 50))

            sephirite_instance = Sephirite(x, y)
            self.sephirites.append(sephirite_instance)
            game_world.add_object(sephirite_instance, 1)

    def get_closest_in_range_sephirite(self, char):
        closest_sephirite = None
        min_dist_sq = float('inf')
        for sephirite in self.sephirites:
            if sephirite.in_range(char):
                dist_sq = (sephirite.x - char.x) ** 2 + (sephirite.y - char.y) ** 2
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    closest_sephirite = sephirite
        return closest_sephirite

    def handle_interaction(self, char):
        if self.anvil and self.anvil in game_world.all_objects() and self.anvil.in_range(char):
            game_world.remove_object(self.anvil)
            self.anvil = None
            game_framework.push_mode(upgrade_mode)
            return True

        closest_sephirite = self.get_closest_in_range_sephirite(char)
        if closest_sephirite:
            game_world.remove_object(closest_sephirite)
            self.sephirites.remove(closest_sephirite)
            game_framework.push_mode(item_selection_mode)
            return True
        return False


def is_valid_spawn_position(x, y, buildings):
    """건물과 겹치지 않는 유효한 위치인지 확인"""
    test_half_w = 17 / 2
    test_half_h = 12 / 2

    monster_left = x - test_half_w
    monster_right = x + test_half_w
    monster_bottom = y - test_half_h
    monster_top = y + test_half_h

    for building in buildings:
        building_left, building_bottom, building_right, building_top = building.get_bb()

        if not (monster_right < building_left or
                monster_left > building_right or
                monster_top < building_bottom or
                monster_bottom > building_top):
            return False

    return True