from pico2d import *
from character import character
from worldmap import WorldMap
from camera import Camera
import game_world
import game_framework
from game_object import anvil
import upgrade_mode

def handle_events():
    global running, anvil
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            elif event.key == SDLK_f:
                if anvil.in_range(char):
                    game_framework.push_mode(upgrade_mode)
                else:
                    print("대장간이 너무 멀다")
            else:
                char.handle_event(event, game_world.camera)
        else:
            char.handle_event(event, game_world.camera)

def init():
    global char, anvil, font

    game_world.clear()

    world_map = WorldMap()
    char = character()
    camera = Camera(char)
    anvil = anvil()

    game_world.set_camera(camera)
    game_world.add_object(world_map, 0)
    game_world.add_object(char, 2)
    game_world.add_object(anvil, 1)
    font = None
    candidates = [
        'resource/font/NanumGothic.ttf',  # 프로젝트 내 폰트 (있다면 추가)
        'C:/Windows/Fonts/malgun.ttf',  # Windows: 맑은 고딕 (대부분 존재)
        None  # pico2d 기본(환경에 따라 실패할 수 있음)
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
    game_world.update()

def draw():
    clear_canvas()
    game_world.render()
    try:
        if font and char and anvil and game_world.camera and anvil.in_range(char):
            char_sprite_h = 19

            head_world_y = char.y + (char_sprite_h / 2) + 6

            sx, sy = game_world.camera.apply(char.x, head_world_y)

            text = "F : 업그레이드"

            font_size = 22
            est_char_w = font_size * 0.6
            text_width = len(text) * est_char_w

            fx = int(sx - text_width / 2)
            fy = int(sy + 4)

            font.draw(fx, fy, text, (255, 255, 255))
    except Exception as e:
        print(f'Font draw error: {e}')
        pass
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