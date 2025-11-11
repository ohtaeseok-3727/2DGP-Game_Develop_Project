from pico2d import *
import game_framework
import game_playmode
from Attack import Attack
from weapon import weapon
import game_world
from worldmap import WorldMap
import math


class State_UI:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = load_image(f'resource/character/CharacterUI_Base.png')
        self.font_15 = None
        self.font_20 = None
        candidates = [
            'resource/font/NanumGothic.ttf',
            'C:/Windows/Fonts/malgun.ttf',
            None
        ]
        for fp in candidates:
            try:
                self.font_15 = load_font(fp, 15)
                self.font_20 = load_font(fp, 20)
                break
            except:
                continue

    def is_clicked(self, mx, my):
        pass
    def draw(self):
        self.image.draw(self.x, self.y, self.width, self.height)
        if game_playmode.char.weapon.image:
            game_playmode.char.weapon.image.clip_composite_draw(0, 0, 11, 35,
                math.radians(270), 'h',
                self.x, self.y + self.height/6,
                11 * 8, 35 * 8)

        if self.font:
            char = game_playmode.char
            wp = game_playmode.char.weapon
            at = game_playmode.char.attack
            base_x = self.x - 180
            base_y = self.y - 130
            line_height = 30

            if self.font_15 and self.font_20:
                char = game_playmode.char
                wp = game_playmode.char.weapon
                at = game_playmode.char.attack
                base_x = self.x - 180
                base_y = self.y - 130
                line_height = 30

                self.font_20.draw(base_x + 50, base_y + 120, f'무기 정보({wp.name})', (255, 255, 255))

                self.font_15.draw(base_x, base_y + 100, f'무기계수: {wp.attack_coefficient}', (255, 255, 255))
                self.font_15.draw(base_x, base_y + 80, f'무기 공격 횟수: {at.max_attack_count}', (255, 255, 255))
                self.font_15.draw(base_x, base_y, f'HP: {char.now_hp} / {char.max_hp}', (255, 255, 255))
                self.font_15.draw(base_x, base_y - line_height, f'STR: {char.STR}', (255, 255, 255))
                self.font_15.draw(base_x, base_y - line_height * 2, f'치명타율: {char.critical * 100:.1f}%',
                                  (255, 255, 255))
                self.font_15.draw(base_x, base_y - line_height * 3, f'치명타 데미지: {char.critical_damage * 100:.0f}%',
                                  (255, 255, 255))
                self.font_15.draw(base_x, base_y - line_height * 4, f'대쉬: {char.can_dash} / {char.max_dash}',
                                  (255, 255, 255))
        pass




def init():
    global char, state_ui
    char = game_playmode.char
    state_ui = State_UI(WorldMap.width/5, WorldMap.height/2, 480, 669)
    pass

def finish():
    pass

def update():
    game_world.update()
    pass


def draw():
    clear_canvas()
    game_world.render()
    state_ui.draw()
    game_world.render_cursor()
    update_canvas()


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE or event.key == SDLK_c:
                game_framework.pop_mode()
            else:
                char.handle_event(event, game_world.camera)
        elif event.type == SDL_KEYUP:
            char.handle_event(event, game_world.camera)
        elif event.type == SDL_MOUSEBUTTONDOWN or event.type == SDL_MOUSEBUTTONUP:
            char.handle_event(event, game_world.camera)


def pause():
    pass


def resume():
    pass
