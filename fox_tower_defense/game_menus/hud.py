import datetime
import pygame as pg
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fox_tower_defense.game import Game
from fox_tower_defense.utils.SETTINGS import COLOURS, WAVE_TIMER
from fox_tower_defense.utils.helper_classes import Vec
from fox_tower_defense.utils.text_functions import outline_text


class HudBottomBar:
    def __init__(self, game: 'Game'):
        self.game = game
        self.bottom_bar_background_image = self.game.images["menu"]["bottom_bar"]
        self.build_hammer_image = self.game.images["build_hammer"]
        self.heart_image = self.game.images["heart"]
        self.coin_image = self.game.images["gold_star"]
        self._set_up()

    def _set_up_clock_display(self):
        # Setup game Clock
        self.clock_font = pg.font.Font(None, 50, bold=True)
        self.clock_text = outline_text(
            self.clock_font, "00", COLOURS["white"], COLOURS["black"])
        self.clock_rect = self.clock_text.get_rect(
            center=(self.game.screen_width // 2, 20))

    def _set_up_coin_display(self):
        # Load and setup Coin display
        self.coin_font = pg.font.Font(None, 50, bold=True)
        self.coin_text = outline_text(self.coin_font, str(
            int(self.game.money)), COLOURS["white"], COLOURS["black"])
        self.coin_rect = self.coin_text.get_rect(
            center=(self.bottom_bar_rect.width * .75, self.bottom_bar_rect.center[1]))

    def _set_up_life_display(self):
        # Load and setup life display
        self.lifes_font = pg.font.Font(None, 50, bold=True)
        self.lifes_text = outline_text(self.lifes_font, str(
            self.game.lifes), COLOURS["white"], COLOURS["black"])
        self.lifes_rect = self.coin_text.get_rect(
            midright=self.bottom_bar_rect.midright)  # + Vec(-5, 0))

    def _set_up_wave_skip_text_display(self):
        self.skip_font = pg.font.Font(None, 35, bold=True)
        self.skip_text = outline_text(
            self.skip_font, "Press 'S' to commence to the next wave early", COLOURS["white"], COLOURS["black"])
        self.skip_text_rect = self.skip_text.get_rect(
            center=self.bottom_bar_rect.midtop + Vec(0, -25))

    def _set_up_win_text_display(self):
        self.win_text = outline_text(
            self.lifes_font, "-GAME COMPLETE- WIP", COLOURS["white"], COLOURS["black"])
        self.win_text_rect = self.win_text.get_rect(
            center=self.game.screen_rect.center)

    def _set_up_info_text_display(self):
        self.info_text = outline_text(
            self.skip_font, "Press 'Esc' to quit -- Go into 'SETTINGS.py' to add/ edit waves --", COLOURS["white"], COLOURS["black"])
        self.info_text_rect = self.info_text.get_rect(
            center=self.game.screen_rect.center + Vec(0, 50))

    def _set_up_bar_and_hammer_rects(self):
        self.bottom_bar_rect = self.bottom_bar_background_image.get_rect(
            bottomleft=self.game.screen_rect.bottomleft)
        self.construct_rect = self.build_hammer_image.get_rect(
            midbottom=self.bottom_bar_rect.midbottom)

    def _set_up_next_wave_countdown_bar(self):
        self.wave_timer_bar_orginal = pg.Surface((275, 15))
        self.wave_timer_bar_orginal.fill(COLOURS["honeydew"])
        self.wave_timer_bar = self.wave_timer_bar_orginal.copy()
        self.wave_timer_background_bar = self.wave_timer_bar_orginal.copy()
        self.wave_timer_background_bar.fill(COLOURS["darkgray"])
        self.wave_timer_bar_rect = self.wave_timer_bar.get_rect(
            midleft=self.bottom_bar_rect.midleft + Vec(15, 3.25))

        # size = self.wave_timer_bar.get_size()
        # self.rect_image = pg.Surface(size, pg.SRCALPHA)

    def _set_up(self):
        self._set_up_bar_and_hammer_rects()
        self._set_up_clock_display()
        self._set_up_coin_display()
        self._set_up_life_display()
        self._set_up_wave_skip_text_display()
        self._set_up_win_text_display()
        self._set_up_info_text_display()
        self._set_up_next_wave_countdown_bar()

    def update(self, time_passed, money_amount, time_until_next_wave):
        time_display = datetime.timedelta(seconds=int(time_passed))

        self.clock_text = outline_text(
            self.clock_font, str(time_display), COLOURS["white"], COLOURS["black"])
        self.coin_text = outline_text(self.coin_font, str(
            money_amount), COLOURS["white"], COLOURS["black"])
        self.wave_timer_bar = pg.transform.scale(self.wave_timer_bar_orginal, (275 * (time_until_next_wave / WAVE_TIMER), 15))

    def is_build_clicked_on(self, mpos):
        return self.construct_rect.collidepoint(mpos)

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
        
        screen.blit(self.wave_timer_background_bar, self.wave_timer_bar_rect)
        screen.blit(self.wave_timer_bar, self.wave_timer_bar_rect)
        # pg.draw.rect(self.wave_timer_bar, (255, 255, 255), (0, 0, 275, 15), border_radius=5)
        # self.image = self.wave_timer_bar.copy().convert_alpha()
        # screen.blit(self.wave_timer_bar, (0, 0), None) 

        if self.game.wave_not_active_and_level_not_complete():
            screen.blit(self.skip_text, self.skip_text_rect)
        elif self.game.is_game_won():
            screen.blit(self.win_text, self.win_text_rect)
            screen.blit(self.info_text, self.info_text_rect)

        if self.game.show_construct_menu:
            self.game.construction_menu.draw(screen)
