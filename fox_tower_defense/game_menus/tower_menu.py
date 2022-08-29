import pygame as pg
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fox_tower_defense.game import Game
from fox_tower_defense.utils.SETTINGS import COLOURS
from fox_tower_defense.utils.helper_classes import Vec


class TowerMenu:
    # img = self.game.build_menu_img, button_xy = self.game.build_button_xy,
    def __init__(self, game: 'Game', tower):
        # text_xy = self.game.build_text_xy):
        self.game = game
        self.tower = tower
        # .set_colorkey(COLOURS["black"])
        self.image = self.game.images["menu"]["tower_build_menu"]
        self.rect = self.image.get_rect(center=self.tower.image_rect.center)
        self.create_level_up_menu()
        # list of 4 (change to grabbing info from tower)
        self.button_images = self.game.images["icons"]
        self.create_buttons()
        self.update_button_values()

    def create_level_up_menu(self):
        # self.build_menu = Tiled_map(path.join(self.tower_folder, "build_menu.tmx"))
        # self.build_menu_img = self.images["tower_build_menu"]#self.build_menu.make_map()
        # find_rgb(self, (0,0,127))

        offset_I = [(-52, -43), (54, -43), (-52, 41), (54, 41)]
        offset_T = [(-51, -19), (55, -19), (-51, 65), (55, 65)]
        ref_pos = ["topleft", "topright", "bottomleft", "bottomright"]
        self.button_xy = {"topleft": offset_I[0], "topright": offset_I[1], "bottomleft": offset_I[2],
                          "bottomright": offset_I[3]}
        self.text_xy = {"topleft": offset_T[0], "topright": offset_T[1], "bottomleft": offset_T[2],
                        "bottomright": offset_T[3]}

    def create_buttons(self):
        order = ["topleft", "topright", "bottomleft", "bottomright"]
        action = ["upgrade", "gem", "choose", "sell"]
        self.buttons = []
        for number, image in enumerate(self.button_images):
            new_button = TowerMenuButton(self, image.copy(), (self.rect.center + Vec(self.button_xy[order[number]])),
                                         (self.rect.center + Vec(self.text_xy[order[number]])), action[number], 12)
            #print(self.rect.center, "+", Vec(self.button_xy[order[number]]))
            self.buttons.append(new_button)

    def update_button_values(self):
        for button in self.buttons:
            if self.tower.level < len(self.tower.cost):
                if button.action == "upgrade":
                    button.button_value = self.tower.cost[self.tower.level]
                elif button.action == "gem":
                    button.button_value = self.tower.level
            elif button.action in ["upgrade", "gem"]:
                button.button_value = "-MAX-"
                button.handle_max_level_reached()

            if button.action == "choose":
                button.button_value = self.tower.fire_mode
            if button.action == "sell":
                button.button_value = int(
                    ((self.tower.cost[0]) * self.tower.level) * .9)
            button.render_text()

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        # pg.draw.rect(screen, COLOURS["red"], self.rect, 1)
        for button in self.buttons:
            button.draw(screen, self.game.mpos)
        # pg.draw.rect(screen, COLOURS["red"], button.rect, 1)


class TowerMenuButton:
    def __init__(self, menu, img, location, text_location, action, font_size, button_value=False):
        self.menu = menu
        self.image = img
        self.location = location
        self.rect = self.image.get_rect(center=self.location)
        self.action = action
        self.text_location = text_location
        self.button_value = button_value
        self.font_size = font_size
        self.max_level_reached = False

        # self.text_center = text_center
        # self.offset_vec_to_add = Vec(offset_vec_to_add)
        self.build_button_image_overlays()

    def handle_max_level_reached(self):
        self.max_level_reached = True
        self.image.set_alpha(85)

    def build_button_image_overlays(self):
        self.highlight = self.image.copy()
        self.highlight.fill((255, 255, 128), special_flags=pg.BLEND_RGB_ADD)
        self.highlight.set_alpha(55)

    def render_text(self):
        self.value_font = pg.font.SysFont(
            "Times New Roman", self.font_size, bold=True)
        self.value = self.value_font.render(
            str(self.button_value), True, COLOURS["white"])
        # self.value = outline_text(self.value_font, str(self.button_value), COLOURS["white"], COLOURS["black"])
        self.value_rect = self.value.get_rect(center=self.text_location)

    def draw(self, screen, mpos):
        screen.blit(self.image, self.rect)
        if self.rect.collidepoint(mpos) and not self.max_level_reached:
            screen.blit(self.highlight, self.rect)
        try:
            screen.blit(self.value, self.value_rect)
        except:
            pass
