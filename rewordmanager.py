import game_framework
import game_world
import item_selection_mode
import upgrade_mode
from game_object import anvil, Sephirite
from worldmap import WorldMap


class RewardManager:
    def __init__(self):
        self.wave_rewards_spawned = {1: False, 2: False, 3: False}
        self.sephirites = []
        self.anvil = None

    def spawn_rewards(self, wave_num, remaining_monsters):
        if remaining_monsters > 0:
            return

        # 웨이브 1 보상: Anvil 1개, Sephirite 1개
        if wave_num == 1 and not self.wave_rewards_spawned[1]:
            if not self.anvil:
                self.anvil = anvil(350, 250)
                game_world.add_object(self.anvil, 1)
            self._spawn_sephirites(1)
            self.wave_rewards_spawned[1] = True

        # 웨이브 2 보상: Sephirite 2개
        elif wave_num == 2 and not self.wave_rewards_spawned[2]:
            self._spawn_sephirites(2)
            self.wave_rewards_spawned[2] = True

        # 웨이브 3 보상: Sephirite 3개
        elif wave_num == 3 and not self.wave_rewards_spawned[3]:
            self._spawn_sephirites(3)
            self.wave_rewards_spawned[3] = True

    def _spawn_sephirites(self, count):
        spawn_positions = [portal.x, portal.x+30, portal.x+60]

        for i in range(count):
            y = portal.y - 50
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
                dist_sq = (sephirite.x - char.x)**2 + (sephirite.y - char.y)**2
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    closest_sephirite = sephirite
        return closest_sephirite

    def handle_interaction(self, char):
        # Anvil 상호작용
        if self.anvil and self.anvil in game_world.all_objects() and self.anvil.in_range(char):
            game_world.remove_object(self.anvil)
            self.anvil = None # 참조 제거
            game_framework.push_mode(upgrade_mode)
            return True

        # Sephirite 상호작용
        closest_sephirite = self.get_closest_in_range_sephirite(char)
        if closest_sephirite:
            game_world.remove_object(closest_sephirite)
            self.sephirites.remove(closest_sephirite)
            game_framework.push_mode(item_selection_mode)
            return True
        return False
