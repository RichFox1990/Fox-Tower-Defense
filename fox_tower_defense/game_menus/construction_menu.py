import pygame as pg
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fox_tower_defense.game import Game

from fox_tower_defense.utils.SETTINGS import COLOURS, TOWER_COSTS
from fox_tower_defense.game_menus.tower_menu import TowerMenuButton
from fox_tower_defense.utils.helper_classes import Vec


class ConstructionMenu:
    # img = self.game.build_menu_img, button_xy = self.game.build_button_xy, text_xy = self.game.build_text_xy):
    def __init__(self, game: 'Game'):
        self.game = game

        self.image = self.game.images["menu"]["tower_construct_menu"]
        self.rect = self.image.get_rect(
            midbottom=self.game.status_bar.construct_rect.midtop)
        # self.button_xy =  # Dict of item blit locations (tl, tr, bl, br)
        # self.text_xy =  # Dict of text blit locations (tl, tr, bl, br)
        self.button_height = 55
        self.spacing = int(self.button_height / 10)
        self.start = Vec(10, 0)
        self.tower_names = self.game.tower_names
        self.font_size = 15
        self.create_tower_icons()  # list of 4 (change to grabbing info from tower)
        self.create_buttons()
        self.update_button_values()
        self.render_cost_info()

    def create_tower_icons(self):
        game_towers = self.game.tower_names
        self.button_images = {}
        for tower in game_towers:
            image = self.game.images["towers"][tower]["tower"][0]
            orig_size = image.get_size()
            scale = image.get_height() / self.button_height
            image = pg.transform.scale(
                image, (int(orig_size[0] / scale), int(orig_size[1] / scale)))
            self.button_images[tower] = image

    def create_buttons(self):
        location = self.start
        self.buttons = {}
        for number, key in enumerate(self.button_images.keys()):
            new_button = TowerMenuButton(self, self.button_images[key], (self.rect.midleft + Vec((location[0] + self.button_height / 2), location[1])),
                                         (self.rect.midleft + Vec((location[0] + self.button_height / 2), location[1] - self.button_height / 2)), self.tower_names[number], 18)
            # print(self.rect.center, "+", Vec(self.button_xy[order[number]]))
            self.buttons[key] = new_button
            location += Vec(self.spacing + self.button_height, 0)

    def handle_click(self, mpos):
        for key in self.buttons.keys():  # check through buttons
            button = self.buttons[key]
            if button.rect.collidepoint(mpos):
                #print("collided", key)
                self.game.new_tower(key)

    def update_button_values(self):
        for key in self.buttons.keys():
            # print(button.action)
            self.buttons[key].button_value = TOWER_COSTS[self.buttons[key].action][0]

    # self.buttons[key].render_text()

    def render_cost_info(self):
        self.font = pg.font.SysFont(
            "Times New Roman", self.font_size, bold=True)
        self.tower_construct_info = {}

        for tower in self.game.tower_names:
            button = self.buttons[tower]
            cost = self.font.render(
                str(TOWER_COSTS[tower][0]), True, COLOURS["white"])
            cost_rect = cost.get_rect(midtop=button.rect.midbottom + Vec(0, 1))
            name = self.font.render((tower), True, COLOURS["white"])
            name_rect = name.get_rect(
                midbottom=button.rect.midtop + Vec(0, -1))
            self.tower_construct_info[tower] = [
                cost, cost_rect, name, name_rect]

    def draw_cost_info(self, screen):
        for key in self.tower_construct_info.keys():
            tower = self.tower_construct_info[key]
            screen.blit(tower[0], tower[1])
            screen.blit(tower[2], tower[3])

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        # pg.draw.rect(screen, COLOURS["red"], self.rect, 1)
        for key in self.buttons.keys():
            self.buttons[key].draw(screen)
        #	pg.draw.rect(screen, COLOURS["gray"], self.buttons[key].rect, 2)
        self.draw_cost_info(screen)
