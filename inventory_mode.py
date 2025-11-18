from pico2d import *
import game_framework
import game_playmode
from Attack import Attack
from weapon import weapon
import game_world
from worldmap import WorldMap

class itemslot:
    slot_image = None
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.item = None
        self.hovered = False

        if itemslot.slot_image is None:
            try:
                itemslot.slot_image = load_image('resource/UI/slot.png')
            except Exception as e:
                print(f'슬롯 이미지 로드 실패: {e}')
                itemslot.slot_image = None

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
        if itemslot.slot_image:
            itemslot.slot_image.draw(self.x, self.y, self.size, self.size)
        else:
            if self.hovered:
                draw_rectangle(self.x - self.size // 2, self.y - self.size // 2,
                               self.x + self.size // 2, self.y + self.size // 2)
            else:
                draw_rectangle(self.x - self.size // 2, self.y - self.size // 2,
                               self.x + self.size // 2, self.y + self.size // 2)

        if self.item and self.item.image:
            self.item.image.draw(self.x, self.y, self.size - 10, self.size - 10)

        if self.hovered:
            pass


class InventoryUI:
    image = None
    tooltip_image = None
    def __init__(self):
        self.width = 796
        self.height = 528
        self.x = get_canvas_width() // 2
        self.y = get_canvas_height() // 2

        if InventoryUI.image is None:
            self.image = load_image(f'resource/UI/inventory.png')

        if InventoryUI.tooltip_image is None:
            try:
                InventoryUI.tooltip_image = load_image('resource/UI/Item_ToolTip.png')
            except Exception as e:
                print(f'툴팁 이미지 로드 실패: {e}')
                InventoryUI.tooltip_image = None

        self.slots = []
        self.rows = 4
        self.cols = 6
        self.padding = 10
        self.slot_size = 100

        start_x = self.x - (self.cols * self.slot_size) // 2
        start_y = self.y + (self.rows * self.slot_size) // 2

        for row in range(self.rows):
            for col in range(self.cols):
                slot_x = start_x + col * (self.slot_size + self.padding) + self.slot_size // 2 - 25
                slot_y = start_y - row * (self.slot_size + self.padding) - self.slot_size // 2
                self.slots.append(itemslot(slot_x, slot_y, self.slot_size))

        self.hovered_slot = None
        self.font = None
        candidates = [
            'resource/font/NanumGothic.ttf',
            'C:/Windows/Fonts/malgun.ttf',
            None
        ]
        for fp in candidates:
            try:
                self.font = load_font(fp, 16)
                print(f'Font loaded: {fp}')
                break
            except Exception as e:
                print(f'Font load failed: {fp} -> {e}')
                self.font = None

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
        self.image.draw(self.x, self.y, self.width, self.height)

        for slot in self.slots:
            slot.draw()

        if self.hovered_slot and self.hovered_slot.item:
            self.draw_tooltip(self.hovered_slot)

    def draw_tooltip(self, slot):
        from sdl2.mouse import SDL_GetMouseState

        # 마우스 화면 좌표 읽기 (pico2d 좌표계로 변환)
        mx = ctypes.c_int(0)
        my = ctypes.c_int(0)
        SDL_GetMouseState(ctypes.byref(mx), ctypes.byref(my))
        screen_x = mx.value
        screen_y = get_canvas_height() - my.value

        item = slot.item
        tooltip_width = 210
        tooltip_height = 90

        tooltip_x = screen_x + 100
        tooltip_y = screen_y - 50

        if self.tooltip_image:
            self.tooltip_image.draw(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        else:
            draw_rectangle(
                tooltip_x - tooltip_width // 2, tooltip_y - tooltip_height // 2,
                tooltip_x + tooltip_width // 2, tooltip_y + tooltip_height // 2
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
    global char, inventory_ui, mouse_x, mouse_y
    char = game_playmode.char
    inventory_ui = InventoryUI()
    inventory_ui.update_items(char.inventory)
    mouse_x, mouse_y = 0, 0

def finish():
    pass

def update():
    game_world.update()
    pass


def draw():
    clear_canvas()
    game_world.render()
    inventory_ui.draw()
    game_world.render_cursor()
    update_canvas()


def handle_events():
    global mouse_x, mouse_y
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE or event.key == SDLK_v:
                game_framework.pop_mode()
        elif event.type == SDL_MOUSEMOTION:
            mouse_x = event.x
            mouse_y = get_canvas_height() - event.y
            inventory_ui.update_hovered(mouse_x, mouse_y)
        elif event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            mx, my = event.x, get_canvas_height() - event.y


def pause():
    pass


def resume():
    pass
