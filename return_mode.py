from pico2d import *
import game_framework
import game_playmode
from Attack import Attack
from weapon import weapon
import game_world
from worldmap import WorldMap
import math
import boss_mode
import title_mode

class Button:
    def __init__(self, x, y, width, height, text, font):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.font = font
        self.hovered = False

    def draw(self):
        # 버튼 배경
        if self.hovered:
            r, g, b = 100, 100, 100
        else:
            r, g, b = 50, 50, 50
        draw_rectangle(self.x - self.width // 2, self.y - self.height // 2,
                       self.x + self.width // 2, self.y + self.height // 2)

        # 버튼 텍스트
        if self.font:
            text_x = self.x - (len(self.text) * 16)
            self.font.draw(text_x, self.y, self.text, (255, 255, 255))

    def is_clicked(self, mx, my):
        return (self.x - self.width // 2 < mx < self.x + self.width // 2 and
                self.y - self.height // 2 < my < self.y + self.height // 2)

    def is_hovered(self, mx, my):
        return (self.x - self.width // 2 < mx < self.x + self.width // 2 and
                self.y - self.height // 2 < my < self.y + self.height // 2)


class talk_UI:
    def __init__(self):
        self.width = 1041
        self.height = 393
        self.x = self.width // 2
        self.y = self.height // 2
        self.image = load_image(f'resource/UI/talk_UI.png')
        candidates = [
            'resource/font/NanumGothic.ttf',
            'C:/Windows/Fonts/malgun.ttf',
            None
        ]
        for fp in candidates:
            try:
                self.font = load_font(fp, 30)
                break
            except:
                continue

        self.buttons = [
            Button(self.x - 200, self.y - 30, 250, 60, '돌아간다', self.font),
        ]

    def is_clicked(self, mx, my):
        pass
    def draw(self):
        self.image.draw(self.x+160, self.y, int(self.width*1.3), int(self.height*1.2))

        if self.font:
            self.font.draw(self.x - 450, self.y + 60,
                           "일단 마을로 되돌아가자", (255, 255, 255))

        # 버튼 출력
        for button in self.buttons:
            button.draw()

    def handle_event(self, event):
        if event.type == SDL_MOUSEMOTION:
            mx, my = event.x, get_canvas_height() - 1 - event.y
            for button in self.buttons:
                button.hovered = button.is_hovered(mx, my)
        elif event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            mx, my = event.x, get_canvas_height() - 1 - event.y
            if self.buttons[0].is_clicked(mx, my):
                game_framework.change_mode(title_mode)



def init():
    global talk_ui
    talk_ui = talk_UI()


def finish():
    global talk_ui
    del talk_ui


def update():
    game_world.update()
    pass


def draw():
    global talk_ui
    clear_canvas()
    game_world.render()
    talk_ui.draw()
    game_world.render_cursor()
    update_canvas()


def handle_events():
    events = get_events()
    for event in events:
        talk_ui.handle_event(event)


def pause():
    pass


def resume():
    pass