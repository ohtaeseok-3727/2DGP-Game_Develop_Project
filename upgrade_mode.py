from pico2d import *
import game_framework
import game_playmode
from Attack import Attack
from weapon import weapon
import game_world


class UpgradeButton:
    images = {}
    def __init__(self, x, y, width, height, rank, text):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rank = rank
        self.text = text

        if rank not in UpgradeButton.images:
            UpgradeButton.images[rank] = load_image(f'resource/UI/Upgrade_Tooltip_{rank}.png')

        self.image = UpgradeButton.images[rank]

    def is_clicked(self, mx, my):
        return (self.x - self.width // 2 < mx < self.x + self.width // 2 and
                self.y - self.height // 2 < my < self.y + self.height // 2)

    def draw(self):
        self.image.draw(self.x, self.y, self.width, self.height)




def init():
    global char, buttons
    char = game_playmode.char

    buttons = [
        UpgradeButton(500, 450, 300, 125, 1, "호우 (원거리)"),
        UpgradeButton(500, 300, 300, 125, 2, "무라마사 (연속공격)")
    ]


def finish():
    pass


def update():
    game_world.update()
    pass


def draw():
    clear_canvas()

    game_world.render()

    draw_rectangle(0, 0, get_canvas_width(), get_canvas_height())

    draw_rectangle(200, 200, 900, 600)

    for button in buttons:
        button.draw()

    if char:
        rank_text = f"현재 무기 랭크: {char.weapon_rank}"

    update_canvas()


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE or event.key == SDLK_f:
                game_framework.pop_mode()
        elif event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            mx, my = event.x, get_canvas_height() - event.y

            for button in buttons:
                if button.is_clicked(mx, my):
                    # 무기 랭크 변경
                    char.weapon_rank = button.rank

                    # Attack과 weapon 객체 재생성
                    char.attack = Attack(char)
                    char.weapon = weapon(char)

                    print(f"무기 변경: 랭크 {button.rank}")


def pause():
    pass


def resume():
    pass
