import fnmatch
import os
import pygame as pg
import random as rand
from fox_tower_defense.game_menus.hud import HudBottomBar

from fox_tower_defense.utils.SETTINGS import COIN_SIZE, COLOURS, FPS, HAMMER_SIZE, HUD_IMAGE_SIZE, MOB_WIDE, SCREEN_HEIGHT, SCREEN_WIDTH, MOB_SIZE, MOB_SLIM, STARTING_MONEY, TOWER_SIZE, TILE_SIZE, WAVE_TIMER
from fox_tower_defense.utils.text_functions import outline_text
from fox_tower_defense.game_menus.main_menu import main_menu
from fox_tower_defense.game_menus.construction_menu import ConstructionMenu
from fox_tower_defense.utils.helper_classes import Vec
from fox_tower_defense.mobs.orc import Orc
from fox_tower_defense.mobs.scorpion import Scorpion
from fox_tower_defense.mobs.purple_hippo import PurpleHippo
from fox_tower_defense.map.tiled_tmx import TiledMap
from fox_tower_defense.towers.stone_tower import Stone
from fox_tower_defense.towers.archer_tower import Archer
from fox_tower_defense.towers.fire_tower import Fire
from fox_tower_defense.towers.sand_tower import Sand
from fox_tower_defense.utils.wave_generation import create_all_waves


class Game:
    def __init__(self):
        pg.init()
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT

        self.screen = pg.display.set_mode(
            (self.screen_width, self.screen_height))
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        pg.display.set_caption(str(self.clock.get_fps()))
        self.defeated = False
        self.delay_counter = 0
        self.draw_overlay = False

        # Used for displayed game timer
        self.time = 0  # Updated in the update loop

        # Used as a timer to spawn mobs at the set intervals defined by the "new_mob" method
        self.mob_timer = 0

        self.pause = False
        self.click = False

        self.show_construct_menu = False  # variable to show the build menu
        # Variable used to enable or disable player adding towers.
        self.building_tower = False

        self.selected_tower = False
        self.mpos = pg.mouse.get_pos()
        self.draw_grid = []
        self.money = STARTING_MONEY
        self.lifes = 10
        self.right_click = False
        self.setup_waves()
        self.new()
        self.print = True

    # SETS THE FOLDER VARIABLES and BUILDS MAP FROM THE TMX FILE ETC
    def load_data(self):
        self.game_folder = os.path.dirname(__file__)
        self.map_folder = os.path.join(self.game_folder, "data/levels")
        self.image_folder = os.path.join(self.game_folder, "data/images")
        self.mob_folder = os.path.join(self.image_folder, "enemies")
        self.tower_folder = os.path.join(self.image_folder, "towers")

        self.map = TiledMap(os.path.join(self.map_folder, "level.tmx"))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

        self.all_sprites = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.towers = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        self.player = pg.sprite.Group()
        self.coins = pg.sprite.Group()

        self.spawn_mobs = {"Orc": Orc, "Scorpion": Scorpion,
                           "Purple_Hippo": PurpleHippo}

    # RUNS ON __init__ , CALLS VARIOUS METHODS TO SET UP INITIAL DATA AS STATED BELOW
    def new(self):
        # Loads map data from txt file
        self.load_data()

        # Creates map for TMX level file
        self.create_map()

        # Loads all images and sound files to dictionaries
        self.initialize_media()

        # Loads image of a 32x32 grid line for use when placing towers
        self.prep_grid()

        # Build the HUD for the bottom status bar info
        self.status_bar = HudBottomBar(self)

        # Build the construction menu for choosing a tower
        self.construction_menu = ConstructionMenu(self)

    # CREATES THE REFERENCES NEEDED FOR THE LEVEL. COLLECTS INFO FROM THE OBJECT LAYER IN THE TMX LEVEL FILE
    def create_map(self):

        self.level_dict = {}
        self.locations = []
        self.path_rects = []
        self.scenery = []

        for tile_object in self.map.tmx_data.objects:
            if tile_object.name == "mob_target_x":
                self.level_dict[tile_object.type] = tile_object.x
                self.locations.append((int(tile_object.x), int(tile_object.y)))
            if tile_object.name == "mob_target_y":
                self.level_dict[tile_object.type] = tile_object.y
                self.locations.append((int(tile_object.x), int(tile_object.y)))
            if tile_object.name == "player_base":
                self.base_location = pg.Rect(
                    tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name == "mob_start":
                self.mob_start_offset = int(tile_object.value)
            if tile_object.name == "path_width":
                self.mob_path_width = int(tile_object.value) - 10
            if tile_object.name == "path_rect":
                self.path_rects.append(
                    pg.Rect(tile_object.x, tile_object.y, tile_object.width, tile_object.height))

        self.sorted_dict = sorted(self.level_dict.keys())
        self.level_turns = []
        self.level_directions = []
        for number in self.sorted_dict:
            if "y" in number:
                self.level_directions.append("y")
            elif "x" in number:
                self.level_directions.append("x")

            self.level_turns.append(self.level_dict[number])

    # LOADS ALL IMAGES AND AUDIO NEEDED
    def initialize_media(self):
        self.images = {}
        # mob images
        self.images["mobs"] = {}
        mob_names = [["Orc", MOB_SLIM], ["Scorpion", MOB_WIDE], [
            "Purple_Hippo", MOB_SLIM]]  # list(self.mob_images.keys())
        actions = ["walk"]
        for mob in mob_names:
            for action in actions:
                self.images["mobs"][mob[0]] = {action: []}
                folder = os.path.join(self.mob_folder, f"{mob[0]}\\{action}")
                for number in range(len(fnmatch.filter(os.listdir(folder), '*.png'))):
                    new_image = pg.image.load(os.path.join(
                        folder, f"{action}_{number}.png")).convert_alpha()
                    orig_size = new_image.get_size()
                    scale = (orig_size[0] / mob[1]) / 1.2
                    new_image = pg.transform.scale(
                        new_image, (int(orig_size[0] / scale), int(orig_size[1] / scale)))
                    self.images["mobs"][mob[0]][action].append(new_image)

        # Tower images
        self.images["towers"] = {}
        self.tower_names = ["Stone", "Fire", "Archer", "Sand"]
        parts = ["tower", "particles", "animation"]
        # len(fnmatch.filter(os.listdir(dirpath), '*.txt'))

        temp_folder = os.path.join(
            self.tower_folder, f"{self.tower_names[0]}\\{parts[0]}")
        image = pg.image.load(os.path.join(
            temp_folder, f"0.png")).convert_alpha()
        orig = image.get_size()
        tower_scale = orig[0] / TOWER_SIZE[0]
        for tower in self.tower_names:
            for part in parts:
                if part == "tower":
                    self.images["towers"][tower] = {part: []}
                else:
                    self.images["towers"][tower][part] = []

                folder = os.path.join(self.tower_folder, f"{tower}\\{part}")
                for number in range(len(fnmatch.filter(os.listdir(folder), '*.png'))):
                    new_image = pg.image.load(os.path.join(
                        folder, f"{number}.png")).convert_alpha()
                    orig_size = new_image.get_size()
                    if part == "particles":
                        new_image = pg.transform.scale(new_image, (
                            int(orig_size[0] / (tower_scale / 1.3)), int(orig_size[1] / (tower_scale / 1.3))))
                    else:
                        new_image = pg.transform.scale(new_image, (
                            int(orig_size[0] / tower_scale), int(orig_size[1] / tower_scale)))
                    self.images["towers"][tower][part].append(new_image)

        self.images["icons"] = []
        icons = ["upgrade", "gem", "choose", "sell"]
        for icon in icons:
            new_image = pg.image.load(os.path.join(
                self.tower_folder, f"icons\\{icon}.png")).convert_alpha()
            # self.icons[icon] = new_image
            self.images["icons"].append(new_image)

        # Health bar images for mobs
        h_images = ["health_bar_red", "health_bar_green"]
        self.health_bar_images = []
        for i in h_images:
            new_image = pg.image.load(os.path.join(
                self.image_folder, f"health_bar\\{i}.png")).convert_alpha()
            new_image = pg.transform.scale(
                new_image, (int(MOB_SIZE * 1.5), MOB_SIZE // 3))
            # change_alpha(new_image, 200)
            self.health_bar_images.append(new_image)

        # Other unsorted images

        images_to_load = [["heart", HUD_IMAGE_SIZE], [
            "gold_star", HUD_IMAGE_SIZE], ["build_hammer", HAMMER_SIZE]]
        for i in images_to_load:
            new_image = pg.image.load(os.path.join(
                self.image_folder, f"HUD\\{i[0]}.png")).convert_alpha()
            new_image = pg.transform.scale(new_image, i[1])
            self.images[i[0]] = new_image

        # Dirty insert of another image (TODO: tidy up and condense the above into one thing)
        images_to_load = [["coin", COIN_SIZE]]
        for i in images_to_load:
            image_list = []
            folder = os.path.join(self.image_folder, f"{i[0]}")
            for num in range(len(fnmatch.filter(os.listdir(folder), '*.png'))):
                new_image = pg.image.load(os.path.join(
                    folder, f"{num}.png")).convert_alpha()
                orig_size = new_image.get_size()
                scale = (orig_size[1] / i[1])
                new_image = pg.transform.scale(
                    new_image, (int(orig_size[0] / scale), int(orig_size[1] / scale)))
                image_list.append(new_image)
            self.images[i[0]] = image_list

        self.images["menu"] = {}
        HUD_images = [["tower_construct_menu", 1], [
            "tower_build_menu", 0.7], ["bottom_bar", 1]]
        for img in HUD_images:
            image = pg.image.load(os.path.join(
                self.image_folder, f"menu\\{img[0]}.png")).convert_alpha()
            orig = image.get_size()
            image = pg.transform.scale(
                image, (int(orig[0] * img[1]), int(orig[1] * img[1])))
            self.images["menu"][img[0]] = image

    # PREPS AN OUTLINE OF A 32x32 GRID (used on dev view)
    def prep_grid(self):
        self.empty_grid = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        for x in range(0, SCREEN_WIDTH // TILE_SIZE + 1):
            for y in range(0, SCREEN_HEIGHT // TILE_SIZE + 1):
                pg.draw.rect(
                    self.empty_grid, COLOURS["white"], (TILE_SIZE * x, TILE_SIZE * y, TILE_SIZE, TILE_SIZE), 1)

        self.empty_grid.set_colorkey(COLOURS["black"])
        self.empty_grid.set_alpha(100)

    def new_game(self):
        self.clock = pg.time.Clock()

    # Basic implementation of waves (TODO: pack data into different form and make more elegant)

    def setup_waves(self):
        self.level_complete = False
        self.wave_active = False
        self.wave_complete = False
        # Variable used to not add to the wave number during the first pregame timer
        self.pre_wave_setup = True
        self.next_wave_timer = WAVE_TIMER

        self.waves = create_all_waves()
        print("length of wave are", len(self.waves))
        print(self.waves)

        self.wave_number = 1

        self.wave = self.waves[self.wave_number]

    # SPAWNS THE ENEMY when the "time" ARGUMENT HAS PASSED
    def handle_wave(self, dt, time_delay=0.5):  # SPAWNS MOBS

        self.mob_timer += dt
        self.wave = self.waves[self.wave_number]  # [MOB ID, AMOUNT TO SPAWN]

        if self.mob_timer >= time_delay:  # If the delay time has passed

            mobs_all_spawned = []
            mobs_to_spawn = []
            for mobs_in_wave in self.wave:
                if mobs_in_wave[1] > 0:
                    mobs_to_spawn.append(mobs_in_wave[0])
                else:
                    self.wave.remove(mobs_in_wave)
                # mobs_all_spawned.append("true")

            if len(self.wave) != 0:  # len(mobs_all_spawned):

                num = rand.randrange(len(self.wave))

                # print(f"spawning {self.wave[num]}")
                # print(f"mobs empty {mobs_all_spawned}")
                # print(f"{self.wave}")
                if self.wave[num][1] > 0:
                    self.wave[num][1] -= 1
                    # Spawn that reference mob (passing the game instance into the class)
                    self.spawn_mobs[self.wave[num][0]](self)

                self.mob_timer = 0  # reset time
            elif len(self.mobs) == 0:
                self.mob_timer = 0
                print("wave over")
                self.wave_active = False
                self.wave_complete = True

    def next_wave(self):
        if not self.pre_wave_setup:
            self.wave_number += 1
        if self.wave_number > len(self.waves):
            print("level complete!")
            self.wave_number = 1
            self.level_complete = True
        else:
            print("wave ", self.wave_number+1)
        self.pre_wave_setup = False
        if not self.level_complete:
            self.wave_complete = False
            self.wave = self.waves[self.wave_number]
            print(f"changed wave to {self.wave}")
            self.wave_active = True

    def wave_countdown(self, dt):
        self.next_wave_timer -= dt
        if self.next_wave_timer <= 0:
            self.next_wave()
            self.next_wave_timer = WAVE_TIMER

    # Method to choose a tower temporary (TODO: integrate choice to a menu and change/remove this method to suit this)
    def new_tower(self, tower_name):
        # if cost <= self.player_money:
        tower_spawn = {"Stone": Stone, "Fire": Fire,
                       "Archer": Archer, "Sand": Sand}
        self.click = False
        if self.building_tower == False:
            self.building_tower = tower_spawn[tower_name](self, self.mpos)
            self.show_construct_menu = False

    # Deducts a life from the player and ends game upon losing all lifes
    def lose_life(self, number):
        self.lifes -= number
        self.lifes_text = outline_text(self.lifes_font, str(
            self.lifes), COLOURS["white"], COLOURS["black"])
        if self.lifes == 0:
            print("YOU LOST")
            self.defeated = True

    # DRAWS OVERLAYS FOR MORE INFORMATION AND FOR TROUBLESHOOTING
    def draw_overlays(self, screen):
        for mob in self.mobs:
            mob.draw_vectors(screen)
            pg.draw.rect(screen, COLOURS["red"], mob.rect, 1)

        for point in self.locations:
            pg.draw.circle(screen, COLOURS["red"], point, 8)

        for tower in self.towers:
            if tower.placed:
                tower.draw_overlays(screen)
        for rect in self.map.obstacles:
            pg.draw.rect(screen, COLOURS["red"], rect, 2)

        rects = [self.clock_rect, self.coin_rect, self.lifes_rect]
        for rect in rects:
            pg.draw.rect(screen, COLOURS["red"], rect, 1)

        self.handle_grid(False)

    # DISPLAYS WHITE SQUARE ON CURRENT SELECTED SQUARE OF MAP WHEN CREATING/MOVING TOWERS (pass false to enable drawing of the grid (dev view))
    def handle_grid(self, tower=True):
        screen = self.screen
        self.grid = self.empty_grid.copy()
        mpos = pg.mouse.get_pos()
        mpos = ((mpos[0] // 32) * 32, (mpos[1] // 32) * 32)
        if not tower:
            highlight_surf = pg.Surface((TILE_SIZE, TILE_SIZE))
            highlight_surf.fill(COLOURS["white"])
            highlight_surf.set_alpha(250)
            self.grid.blit(highlight_surf, mpos)
        screen.blit(self.grid, self.screen_rect)

        # if self.click:
        #     print(mpos)

    # Method to handle a click on towers (selecting, deselecting, swapping when another already highlighted etc)
    def handle_click(self, mpos):
        if self.show_construct_menu:
            if self.construction_menu.rect.collidepoint(mpos):
                self.construction_menu.handle_click(mpos)
            else:
                self.show_construct_menu = False

        elif self.status_bar.is_build_clicked_on(mpos):
            self.show_construct_menu = not self.show_construct_menu

        if self.selected_tower != False:  # If theres a tower selected

            # If you click the same tower again
            if self.selected_tower.rect.collidepoint(mpos):
                self.selected_tower.selected = False  # Tower state change to False
                self.selected_tower = False  # Game's selected tower set to False

            # and the mouse is clicked inside the menu rect of that tower
            elif self.selected_tower.menu.rect.collidepoint(mpos):
                self.selected_tower.handle_menu_click(mpos)
            # if self.right_click:
            # 	print("offset", self.selected_tower.menu.rect.center, mpos)
            # 	self.right_click = False

            else:  # If neither of the 2 above. Check if you clicked any another tower on the map
                tower_collide = []
                for tower in self.towers:
                    if tower.rect.collidepoint(mpos):
                        tower_collide.append("clicked")
                        # print("clicked on tower")
                        # If the tower you clicked isn't the same as the one already selected
                        if self.selected_tower != False and self.selected_tower != tower:
                            self.selected_tower.selected = False
                        self.selected_tower = tower
                        tower.selected = True

                if len(
                        tower_collide) == 0:  # If you didn't click on any other tower (i.e. you clicked onto the map somewhere)
                    self.selected_tower.selected = False  # Deselect everything
                    self.selected_tower = False

        # There's no tower selected before you clicked (check if you clicked a tower)
        else:
            for tower in self.towers:
                if tower.rect.collidepoint(mpos):
                    # print("clicked on tower")
                    if self.selected_tower != False and self.selected_tower != tower:
                        self.selected_tower.selected = False
                    self.selected_tower = tower
                    tower.selected = True

    def is_wave_active(self):
        return self.wave_active

    def is_level_complete(self):
        return self.level_complete

    def is_wave_complete(self):
        return self.wave_complete

    def is_game_won(self):  # expand when more levels added
        return self.level_complete and self.wave_complete

    def wave_not_active_and_level_not_complete(self):
        return not self.is_wave_active() and not self.is_level_complete()

    # GAME UPDATE LOOP
    def update(self, mpos, dt):

        if self.is_wave_active():
            self.handle_wave(dt)

        self.wave_countdown(dt)

        for mob in self.mobs:
            mob.update(dt)

        for coin in self.coins:
            coin.update(mpos, dt)

        # self.draw_grid = False

        for tower in self.towers:
            tower.update(dt)
            if not tower.placed:
                if self.building_tower == False:
                    self.towers.remove(tower)
            # self.draw_grid = True
        for i in self.projectiles:
            i.update(dt)

        self.time += dt
        self.status_bar.update(self.time, self.money)

    # Draws the lifes, time, coins and images next to them
    def draw_HUD(self, screen):
        self.status_bar.draw(screen)

    # Draw loop (TODO: Tidy up into methods)
    def draw(self, screen):

        screen.fill(COLOURS["black"])
        screen.blit(self.map_img, self.screen_rect)  # Blit map

        if self.draw_grid:
            self.handle_grid()
        if self.draw_overlay:
            self.draw_overlays(screen)
        # sorts blitting order (sprites that is the lowest on the screen i gets blitted over the top of anything above it)
        for sprite in sorted(self.all_sprites, key=lambda spr: spr.rect.bottom):
            sprite.draw(screen)
        for i in self.projectiles:
            i.draw(screen)
        if self.selected_tower != False:
            self.selected_tower.menu.draw(screen)

        self.draw_HUD(screen)

    # MAIN GAME LOOP (TODO: tidy up into methods more)
    def run(self):

        while not self.defeated:

            dt = self.clock.tick(FPS) / 1000

            self.click = False
            self.mpos = pg.mouse.get_pos()

            if self.delay_counter > 0:
                self.delay_counter += FPS * dt
            if self.delay_counter > FPS * .2:
                self.delay_counter = 0
            # print("reset zero")

            # shorten the pg get pressed function to 'keyPress'
            keyPress = pg.key.get_pressed()

            # Start event loop.
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    # sys.exit()
                    # pg.quit()
                    return False

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        if self.building_tower != False:
                            self.building_tower = False
                            # player cancelled the building of the tower. Now loop through towers and delete any that aren't placed.
                            for tower in self.towers:
                                if not tower.placed:
                                    pg.sprite.Sprite.kill(tower)
                            del tower

                        elif self.selected_tower != False:
                            self.selected_tower.selected = False
                            self.selected_tower = False
                        else:
                            return False
                            # sys.exit()

                    if event.key == pg.K_i:  # and self.delay_counter == 0:
                        # self.delay_counter = 1
                        self.draw_overlay = not self.draw_overlay

                    if event.key == pg.K_s:
                        if not self.is_wave_active():
                            self.next_wave_timer = 0

                    if event.key == pg.K_b:
                        self.show_construct_menu = not self.show_construct_menu

                    if event.key == pg.K_p:
                        if self.pause:
                            print("let's go")
                        else:
                            print("Paused")
                        self.pause = not self.pause

                    if event.key == pg.K_t:
                        pass

                if event.type == pg.MOUSEMOTION:
                    if self.status_bar.construct_rect.collidepoint(self.mpos):
                        self.status_bar.construct_rect.midbottom = self.status_bar.bottom_bar_rect.midbottom + \
                            Vec(0, -5)
                    else:
                        self.status_bar.construct_rect.midbottom = self.status_bar.bottom_bar_rect.midbottom

                if event.type == pg.MOUSEBUTTONDOWN and self.delay_counter == 0:
                    if event.button == 1:
                        self.click = True
                        if self.building_tower == False:
                            # self.click = False
                            self.handle_click(self.mpos)
                        self.delay_counter = 1
                    # print("clicked")
                    if event.button == 3:
                        if self.building_tower != False:
                            self.building_tower = False
                            # player cancelled the building of the tower. Now loop through towers and delete any that aren't placed.
                            for tower in self.towers:
                                if not tower.placed:
                                    pg.sprite.Sprite.kill(tower)
                            del tower

                        elif self.selected_tower != False:
                            self.selected_tower.selected = False
                            self.selected_tower = False
                        self.show_construct_menu = False
                    # self.right_click = True
                    # print(self.mpos)

            if not self.pause:
                self.update(self.mpos, dt)
                self.draw(self.screen)

            pg.display.set_caption(str(self.clock.get_fps()))
            pg.display.update()


def main():
    playing = True
    g = Game()
    while playing:
        start = main_menu(g.map_img)
        if start:
            g.new_game()
            start = g.run()
