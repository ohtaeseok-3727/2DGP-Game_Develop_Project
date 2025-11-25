import random
from pico2d import *
import game_world
import game_framework
from worldmap import WorldMap
from character import character
from wave_manager import WaveSpawner, RewardManager
from camera import Camera
from game_object import *
import inventory_mode
import status_mode
from cursor import Cursor
import enter_mode

def init():
    global char, font, monsters, portal, remaining_monsters, reward_manager, wave_spawner
    global building1, building2, building3, building4, building5, building6, building7

    game_world.clear()
    game_world.clear_collision_pairs()

    world_map = WorldMap()
    char = character()
    camera = Camera(char)
    portal = Portal(400, 300)
    building1 = Building(400, 550, 1, 1)
    building2 = Building(100, 500, 2, 1.2)
    building3 = Building(700, 550, 3, 1.2)
    building4 = Building(650, 400, 4, 1.2)
    building5 = Building( 50, 370, 5, 1.2)
    building6 = Building(100, 100, 6, 1.2)
    building7 = Building(570, 150, 7, 1.2)

    cursor = Cursor()
    char.cursor = cursor
    game_world.set_cursor(cursor)

    monsters = []

    buildings = [building1, building2, building3, building4, building5, building6, building7]

    reward_manager = RewardManager(portal)
    wave_spawner = WaveSpawner(portal, char, monsters, buildings)

    remaining_monsters = 0
    world_map.change_map('default')

    game_world.set_camera(camera)
    game_world.add_object(world_map, 0)
    game_world.add_object(building1, 0)
    game_world.add_object(building2, 0)
    game_world.add_object(building3, 0)
    game_world.add_object(building4, 0)
    game_world.add_object(building5, 0)
    game_world.add_object(building6, 0)
    game_world.add_object(building7, 0)
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

    wave_spawner.check_and_spawn_next_phase(remaining_monsters)

    if wave_spawner.is_wave_complete():
        reward_manager.spawn_rewards(portal.current_wave, 0)

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
                if not reward_manager.handle_interaction(char):
                    if portal.in_range(char):
                        remaining_monsters = sum(1 for m in monsters if m.is_alive)
                        if remaining_monsters == 0 and not wave_spawner.is_wave_active:
                            success, message = portal.interact()
                            if success:
                                wave_spawner.start_wave(portal.current_wave)
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