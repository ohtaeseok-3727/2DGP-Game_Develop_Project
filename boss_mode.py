import random
from pico2d import *
from character import character
from worldmap import WorldMap
from camera import Camera
import game_world
import game_framework
import inventory_mode
import status_mode
from cursor import Cursor
from Attack import *
import Boss

def handle_events():
    global running
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            elif event.key == SDLK_v:
                game_framework.push_mode(inventory_mode)
            elif event.key == SDLK_c:
                game_framework.push_mode(status_mode)
            else:
                char.handle_event(event, game_world.camera)
        else:
            char.handle_event(event, game_world.camera)

def init():
    global monsters, sephirite, portal, boss, char

    game_world.clear()

    world_map = WorldMap()
    char = character()
    camera = Camera(char)
    boss = Boss.KingSlime(600, 400)
    boss.set_target(char)

    cursor = Cursor()
    char.cursor = cursor
    game_world.set_cursor(cursor)


    game_world.set_camera(camera)
    game_world.add_object(world_map, 0)
    game_world.add_object(char, 2)
    game_world.add_object(boss, 2)


def update():
    game_world.update()
    game_world.handle_collisions()

def draw():
    clear_canvas()
    game_world.render()
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