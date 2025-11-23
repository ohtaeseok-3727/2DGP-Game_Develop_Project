import random

from pico2d import *

from character import character
from worldmap import WorldMap
from camera import Camera
import game_world
import game_framework
import upgrade_mode
from game_object import *
import inventory_mode
import status_mode
from monster import Monster
from cursor import Cursor
from Attack import *
import item_selection_mode
import enter_mode
import boss_mode

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

def spawn_wave_monsters(wave_number):
    """웨이브별 몬스터 생성"""
    global monsters

    spawn_count = portal.monsters_per_wave

    for i in range(spawn_count):
        # 랜덤 위치 생성 (포탈 주변)
        angle = random.uniform(0, 2 * 3.14159)
        distance = random.randint(100, 200)
        spawn_x = portal.x + distance * math.cos(angle)
        spawn_y = portal.y + distance * math.sin(angle)

        # 맵 범위 내로 제한
        spawn_x = max(50, min(spawn_x, WorldMap.width - 50))
        spawn_y = max(50, min(spawn_y, WorldMap.height - 50))

        # 웨이브에 따라 몬스터 타입 결정
        if wave_number == 1:
            monster_type = 'small_blue_slime'
        elif wave_number == 2:
            monster_type = 'small_blue_slime' if i < 7 else 'blue_slime'
        else:  # wave_number == 3
            monster_type = 'blue_slime'

        monster = Monster(spawn_x, spawn_y, monster_type)
        monster.set_target(char)
        game_world.add_object(monster, 2)
        monsters.append(monster)

    # 충돌 페어 등록
    for monster in monsters:
        game_world.add_collision_pairs('monster:monster', None, monster)
        game_world.add_collision_pairs('monster:monster', monster, None)

    print(f"웨이브 {wave_number}: {spawn_count}마리의 몬스터 소환!")

def init():
    global char, font, monsters, portal, remaining_monsters, reward_manager, backgrounds

    game_world.clear()

    world_map = WorldMap()
    char = character()
    camera = Camera(char)
    portal = Portal(400, 300)
    reward_manager = RewardManager()

    cursor = Cursor()
    char.cursor = cursor
    game_world.set_cursor(cursor)

    monsters = []

    remaining_monsters = 0
    world_map.change_map('default')

    game_world.set_camera(camera)
    game_world.add_object(world_map, 0)
    game_world.add_object(char, 2)
    game_world.add_object(portal, 1)

    for monster in monsters:
        game_world.add_collision_pairs('monster:monster', None, monster)
    for monster in monsters:
        game_world.add_collision_pairs('monster:monster', monster, None)


    font = None
    candidates = [
        'resource/font/NanumGothic.ttf',
        'C:/Windows/Fonts/malgun.ttf',
        None
    ]
    for fp in candidates:
        try:
            font = load_font(fp, 15)
            print(f'Font loaded: {fp}')
            break
        except Exception as e:
            print(f'Font load failed: {fp} -> {e}')
            font = None

def update():
    global remaining_monsters
    remaining_monsters = sum(1 for m in monsters if m.is_alive)

    reward_manager.spawn_rewards(portal.current_wave, remaining_monsters)

    game_world.update()
    game_world.handle_collisions()

def draw():
    clear_canvas()
    game_world.render()

    def draw_interaction_text(target_object, text):
        if font and char and game_world.camera and target_object.in_range(char):
            char_sprite_h = 19
            head_world_y = char.y + (char_sprite_h / 2) + 6
            sx, sy = game_world.camera.apply(char.x, head_world_y)
            font_size = 22
            est_char_w = font_size * 0.6
            text_width = len(text) * est_char_w
            fx = int(sx - text_width / 2)
            fy = int(sy + 4)
            font.draw(fx, fy, text, (0, 0, 0))

    try:
        # Anvil 상호작용 텍스트
        if reward_manager.anvil:
            draw_interaction_text(reward_manager.anvil, "F : 업그레이드")

        # Sephirite 상호작용 텍스트 (가장 가까운 것 하나만)
        closest_sephirite = reward_manager.get_closest_in_range_sephirite(char)
        if closest_sephirite:
            draw_interaction_text(closest_sephirite, "F : 아이템 선택")

    except Exception as e:
        print(f'Font draw error: {e}')
        pass

    game_world.render_cursor()
    update_canvas()

def finish():
    game_world.clear()

def pause():
    global char
    try:
        # 눌린 키 상태 초기화
        char.left_pressed = False
        char.right_pressed = False
        char.up_pressed = False
        char.down_pressed = False

        # 방향값 초기화
        char.dir = 0
        char.updown_dir = 0

        # 상태 머신에 STOP 이벤트 전달하여 이동 상태에서 벗어나게 함
        char.state_machine.handle_state_event(('STOP', 0))
    except Exception:
        pass

def resume():
    pass

def handle_events():
    global remaining_monsters
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            elif event.key == SDLK_f:
                # 상호작용 로직을 RewardManager로 위임
                if not reward_manager.handle_interaction(char):
                    # 포탈 상호작용
                    if portal.in_range(char):
                        remaining_monsters = sum(1 for m in monsters if m.is_alive)
                        if remaining_monsters == 0:
                            success, message = portal.interact()
                            if success:
                                spawn_wave_monsters(portal.current_wave)
                                print(message)
                            else:
                                if portal.is_all_waves_complete():
                                    game_framework.push_mode(enter_mode)
                                print(message)

            elif event.key == SDLK_v:
                game_framework.push_mode(inventory_mode)
            elif event.key == SDLK_c:
                game_framework.push_mode(status_mode)
            else:
                char.handle_event(event, game_world.camera)
        else:
            char.handle_event(event, game_world.camera)