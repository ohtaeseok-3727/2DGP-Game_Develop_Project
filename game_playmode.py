import random

from pico2d import *
from character import character
from worldmap import WorldMap
from camera import Camera
import game_world
import game_framework
from game_object import *
import upgrade_mode
import inventory_mode
import status_mode
from monster import Monster
from cursor import Cursor
from Attack import *
import item_selection_mode
import enter_mode
import boss_mode

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
    global char, anvil, font, monsters, sephirite, portal, remaining_monsters

    game_world.clear()

    world_map = WorldMap()
    char = character()
    camera = Camera(char)
    anvil = anvil(300, 200)
    sephirite = Sephirite(400, 400)
    portal = Portal(400, 300)

    cursor = Cursor()
    char.cursor = cursor
    game_world.set_cursor(cursor)

    monsters = []

    remaining_monsters = sum(1 for m in monsters if m.is_alive)

    game_world.set_camera(camera)
    game_world.add_object(world_map, 0)
    game_world.add_object(char, 2)
    game_world.add_object(sephirite, 1)
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
    remaining_monsters = sum(1 for m in monsters if m.is_alive)
    if portal.current_wave == 1 and remaining_monsters == 0:
        game_world.add_object(anvil, 1)
    game_world.update()
    game_world.handle_collisions()

def draw():
    clear_canvas()
    game_world.render()
    try:
        if font and char and anvil and game_world.camera and anvil.in_range(char) and portal.current_wave == 1 and sum(1 for m in monsters if m.is_alive) == 0:
            char_sprite_h = 19

            head_world_y = char.y + (char_sprite_h / 2) + 6

            sx, sy = game_world.camera.apply(char.x, head_world_y)

            text = "F : 업그레이드"

            font_size = 22
            est_char_w = font_size * 0.6
            text_width = len(text) * est_char_w

            fx = int(sx - text_width / 2)
            fy = int(sy + 4)

            font.draw(fx, fy, text, (0, 0, 0))
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
    global running, anvil, remaining_monsters
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            elif event.key == SDLK_f:
                if anvil.in_range(char) and portal.current_wave == 1 and remaining_monsters == 0:
                    game_framework.push_mode(upgrade_mode)

                if remaining_monsters == 0 and sephirite.in_range(char):
                    game_framework.push_mode(item_selection_mode)

                if portal.in_range(char):
                    success, message = portal.interact()
                    remaining_monsters = sum(1 for m in monsters if m.is_alive)
                    if remaining_monsters == 0:
                        if success:
                            spawn_wave_monsters(portal.current_wave)
                            print(message)
                        else:
                            # 모든 웨이브 완료 시 보스 모드로 전환
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