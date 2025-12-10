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
import game_playmode

from game_object import BossPortal

cutscene = None
cutscene_active = False
boss_portal = None

def handle_events():
    global running, cutscene_active

    # 컷신 중에는 입력 무시
    if cutscene_active:
        events = get_events()
        for event in events:
            if event.type == SDL_QUIT:
                game_framework.quit()
        return

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            elif event.key == SDLK_f:
                if boss_portal and char and boss_portal.in_range(char):
                    boss_portal.interact()
            elif event.key == SDLK_v:
                game_framework.push_mode(inventory_mode)
            elif event.key == SDLK_c:
                game_framework.push_mode(status_mode)
            else:
                char.handle_event(event, game_world.camera)
        else:
            char.handle_event(event, game_world.camera)


def on_cutscene_complete():
    """컷신 완료 콜백"""
    global cutscene_active, boss
    cutscene_active = False

    # 보스를 게임 월드에 추가
    game_world.add_object(boss, 2)

    # 보스 충돌 쌍 재등록
    game_world.add_collision_pairs('character:Boss', None, boss)
    game_world.add_collision_pairs('Boss:attack', boss, None)

    # 카메라를 캐릭터로 전환
    game_world.camera.target = char

    print("보스 등장! 전투 시작!")

def init():
    global monsters, sephirite, boss_portal, boss, char, cutscene, cutscene_active, sound

    game_world.clear()
    game_world.clear_collision_pairs()

    world_map = WorldMap()
    char = game_playmode.char
    boss_portal = None
    boss = Boss.KingSlime(600, 400)
    boss.set_target(char)

    world_map.change_map('boss map')
    cursor = Cursor()
    char.cursor = cursor
    game_world.set_cursor(cursor)

    sound = load_music('resource/sound/boss_thema.mp3')
    sound.set_volume(64)
    sound.repeat_play()

    # 컷신 시작 - 카메라는 나중에 설정
    cutscene = Boss.BossCutscene(600, 400, on_cutscene_complete)
    cutscene_active = True

    # 컷신용 임시 카메라 타겟 객체
    class CutsceneTarget:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    cutscene_target = CutsceneTarget(600, 400)
    camera = Camera(cutscene_target)

    game_world.set_camera(camera)
    game_world.add_object(world_map, 0)
    game_world.add_object(char, 2)

    game_world.add_collision_pairs('character:monster', char, None)
    game_world.add_collision_pairs('character:Boss', char, None)
    game_world.add_collision_pairs('building:character', None, char)

    game_world.add_collision_pairs('building:monster', None, None)
    game_world.add_collision_pairs('monster:monster', None, None)

    # 캐릭터 이동 제한
    char.left_pressed = False
    char.right_pressed = False
    char.up_pressed = False
    char.down_pressed = False
    char.dir = 0
    char.updown_dir = 0


def on_cutscene_complete():
    """컷신 완료 콜백"""
    global cutscene_active, boss, char
    cutscene_active = False

    # 보스를 게임 월드에 추가
    game_world.add_object(boss, 2)

    # 카메라를 캐릭터로 전환
    game_world.camera.target = char

    print("보스 등장! 전투 시작!")


def update():
    global cutscene, cutscene_active, boss_portal

    if cutscene_active and cutscene:
        cutscene.update()
        # 컷신 중에도 카메라는 업데이트
        if game_world.camera:
            game_world.camera.update()
    else:
        game_world.update()
        game_world.handle_collisions()

    try:
        if boss_portal is None and boss is not None and not getattr(boss, 'is_alive', True):
            cx = WorldMap.width // 2
            cy = WorldMap.height // 2
            boss_portal = BossPortal(cx, cy)
            game_world.add_object(boss_portal, 1)
    except Exception:
        pass


def draw():
    global cutscene, cutscene_active

    clear_canvas()
    game_world.render()

    # 컷신 그리기
    if cutscene_active and cutscene:
        cutscene.draw(game_world.camera)

    try:
        if boss_portal and char and game_world.camera and boss_portal.in_range(char):
            # 캐릭터 머리 위에 간단 텍스트
            font_candidates = [
                'resource/font/NanumGothic.ttf',
                'C:/Windows/Fonts/malgun.ttf',
                None
            ]
            font = None
            for fp in font_candidates:
                try:
                    font = load_font(fp, 20)
                    break
                except:
                    continue
            if font:
                sx, sy = game_world.camera.apply(char.x, char.y + 20)
                font.draw(int(sx - 80), int(sy + 4), "F \: 돌아가기", (0, 0, 0))
    except Exception:
        pass

    game_world.render_cursor()
    update_canvas()


def finish():
    game_world.clear()


def pause():
    global char
    try:
        char.left_pressed = False
        char.right_pressed = False
        char.up_pressed = False
        char.down_pressed = False
        char.dir = 0
        char.updown_dir = 0
        char.state_machine.handle_state_event(('STOP', 0))
    except Exception:
        pass


def resume():
    pass
