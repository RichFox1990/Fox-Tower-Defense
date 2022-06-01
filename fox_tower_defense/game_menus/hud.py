import pygame as pg

from fox_tower_defense.utils.SETTINGS import COLOURS
from fox_tower_defense.utils.helper_classes import Vec
from fox_tower_defense.utils.text_functions import outline_text


class HudBottomBar:
    def __init__(self, game):
        self.game = game
        self.bottom_bar_background_image = self.game.images["menu"]["bottom_bar"]
        self.build_hammer_image = self.game.images["build_hammer"]
        self.heart_image = self.game.images["heart"]
        self.coin_image = self.game.images["gold_star"]
        self.set_up()

    def build_rects(self):
        pass

    def set_up(self):
        # SETUP RECTS
        self.bottom_bar_rect = self.bottom_bar_background_image.get_rect(
            bottomleft=self.game.screen_rect.bottomleft)

        # Setup game Clock
        self.clock_font = pg.font.Font(None, 50, bold=True)
        self.clock_text = outline_text(
            self.clock_font, "00", COLOURS["white"], COLOURS["black"])
        self.clock_rect = self.clock_text.get_rect(
            center=(self.game.screen_width // 2, 20))

        # Load and setup Coin display
        self.coin_font = pg.font.Font(None, 50, bold=True)
        self.coin_text = outline_text(self.coin_font, str(
            int(self.game.money)), COLOURS["white"], COLOURS["black"])
        self.coin_rect = self.coin_text.get_rect(
            center=(self.bottom_bar_rect.width * .75, self.bottom_bar_rect.center[1]))

        # Load and setup life display
        self.lifes_font = pg.font.Font(None, 50, bold=True)
        self.lifes_text = outline_text(self.lifes_font, str(
            self.game.lifes), COLOURS["white"], COLOURS["black"])
        self.lifes_rect = self.coin_text.get_rect(
            midright=self.bottom_bar_rect.midright)  # + Vec(-5, 0))

        self.skip_font = pg.font.Font(None, 35, bold=True)
        self.skip_text = outline_text(
            self.skip_font, "Press 'S' to commence to the next wave early", COLOURS["white"], COLOURS["black"])
        self.skip_text_rect = self.skip_text.get_rect(
            center=self.bottom_bar_rect.midtop + Vec(0, -25))
        self.win_text = outline_text(
            self.lifes_font, "-GAME COMPLETE- WIP", COLOURS["white"], COLOURS["black"])
        self.win_text_rect = self.win_text.get_rect(
            center=self.game.screen_rect.center)
        self.info_text = outline_text(
            self.skip_font, "Press 'Esc' to quit -- Go into 'SETTINGS.py' to add/ edit waves --", COLOURS["white"], COLOURS["black"])
        self.info_text_rect = self.info_text.get_rect(
            center=self.game.screen_rect.center + Vec(0, 50))

        self.construct_rect = self.build_hammer_image.get_rect(
            midbottom=self.bottom_bar_rect.midbottom)

    def draw(self, screen):
        spacer = Vec(5, 1)
        screen.blit(self.bottom_bar_background_image, self.bottom_bar_rect)
        screen.blit(self.clock_text, self.clock_rect)  # Blit game clock
        screen.blit(self.coin_text, self.coin_rect)  # Blit money amount
        screen.blit(self.heart_image,
                    self.heart_image.get_rect(midright=self.lifes_rect.midleft - spacer))  # + self.lifes_rect.y))
        screen.blit(self.coin_image,
                    self.coin_image.get_rect(midright=self.coin_rect.midleft - spacer))  # + self.coin_rect.y))
        screen.blit(self.lifes_text, self.lifes_rect)
        screen.blit(self.build_hammer_image, self.construct_rect)

        if not self.game.wave_active and not self.game.level_complete:
            screen.blit(self.skip_text, self.skip_text_rect)
        elif self.game.level_complete and self.game.wave_complete:
            screen.blit(self.win_text, self.win_text_rect)
            screen.blit(self.info_text, self.info_text_rect)

        if self.game.show_construct_menu:
            self.game.construction_menu.draw(screen)
