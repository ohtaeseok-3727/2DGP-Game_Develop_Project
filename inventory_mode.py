from pico2d import *
import game_framework
import game_playmode
from Attack import Attack
from weapon import weapon
import game_world
from worldmap import WorldMap

class itemslot:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.item = None
        self.hovered = False

    def set_item(self, item):
        self.item = item


    def is_clicked(self, mx, my):
        return (self.x - self.width // 2 < mx < self.x + self.width // 2 and
                self.y - self.height // 2 < my < self.y + self.height // 2)

    def is_hovered(self, mx, my):
        half = self.size//2
        return (self.x - half < mx < self.x + half and
                self.y - half < my < self.y + half)

    def draw(self):
        color = (255, 255, 100) if self.hovered else (200, 200, 200)
        draw_rectangle(self.x - self.size // 2, self.y - self.size // 2,
                       self.x + self.size // 2, self.y + self.size // 2, color)
        if self.item and self.item.image:
            self.item.image.draw(self.x, self.y, self.size - 10, self.size - 10)


class InventoryUI:
    image = None
    def __init__(self):
        self.width = 846
        self.height = 528
        self.x = get_canvas_width() // 2
        self.y = get_canvas_height() // 2

        self.image = load_image(f'resource/UI/inventory.png')

        self.slots = []
        self.rows = 4
        self.cols = 5
        self.padding = 10
        self.slot_size = 70

        start_x = self.x - (self.cols * self.slot_size) // 2
        start_y = self.y + (self.rows * self.slot_size) // 2

        for row in range(self.rows):
            for col in range(self.cols):
                slot_x = start_x + col * (self.slot_size + self.padding) + self.slot_size // 2
                slot_y = start_y - row * (self.slot_size + self.padding) - self.slot_size // 2
                self.slots.append(itemslot(slot_x, slot_y, self.slot_size))

        self.hovered_slot = None
        self.font = load_font('resource/font/NanumGothic.ttf', 16)

    def update_items(self, inventory):
        for i, item in enumerate(inventory):
            if i < len(self.slots):
                self.slots[i].set_item(item)

    def update_hovered(self, mx, my):
        self.hovered_slot = None
        for slot in self.slots:
            if slot.is_hovered(mx, my):
                slot.hovered = True
                self.hovered_slot = slot
            else:
                slot.hovered = False

    def draw(self):
        self.background.draw(self.x, self.y, self.width, self.height)

        for slot in self.slots:
            slot.draw()

        if self.hovered_slot and self.hovered_slot.item:
            self.draw_tooltip(self.hovered_slot)

    def draw_tooltip(self, slot):
        item = slot.item
        tooltip_x = slot.x + 80
        tooltip_y = slot.y + 40

        draw_rectangle(
            tooltip_x - 100, tooltip_y - 60,
            tooltip_x + 100, tooltip_y + 20
        )

        if self.font:
            self.font.draw(tooltip_x - 90, tooltip_y + 5,
                           item.item_type, (255, 255, 255))

            effects = item.item_effects.get(item.item_type, {})
            y_offset = -15
            for stat, value in effects.items():
                stat_text = f"{stat}: +{value}"
                self.font.draw(tooltip_x - 90, tooltip_y + y_offset,
                               stat_text, (200, 200, 200))
                y_offset -= 20


def init():
    global char, back_ui
    char = game_playmode.char
    back_ui = Back(get_canvas_width() // 2, get_canvas_height() // 2, 846, 528)
    pass

def finish():
    pass

def update():
    game_world.update()
    pass


def draw():
    clear_canvas()
    game_world.render()
    back_ui.draw()
    game_world.render_cursor()
    update_canvas()


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE or event.key == SDLK_v:
                game_framework.pop_mode()
        elif event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            mx, my = event.x, get_canvas_height() - event.y


def pause():
    pass


def resume():
    pass
