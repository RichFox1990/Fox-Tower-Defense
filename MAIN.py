import fnmatch
import os
from FUNCTIONS import *
from MOBS import *
from TILED import *
from TOWERS import *


class Game:
	def __init__(self):
		pg.init()
		self.screen_width = SCREENWIDTH
		self.screen_height = SCREENHEIGHT
		self.screen = pg.display.set_mode((self.screen_width, self.screen_height))
		self.screen_rect = self.screen.get_rect()
		self.clock = pg.time.Clock()
		pg.display.set_caption(str(self.clock.get_fps()))
		self.defeated = False
		self.delay_counter = 0
		self.draw_overlay = False

		# Used for displayed game timer
		self.time = 0 # Updated in the update loop

		# Used as a timer to spawn mobs at the set intervals defined by the "new_mob" method
		self.mob_timer = 0

		self.pause = False
		self.click = False

		self.show_construct_menu = False  # variable to show the build menu
		self.building_tower = False  # Variable used to enable or disable player adding towers.

		self.selected_tower = False
		self.mpos = pg.mouse.get_pos()
		self.draw_grid = []
		self.money = 250
		self.lifes = 10
		self.right_click = False
		self.setup_waves()
		self.new()
		self.print = True

	# SETS THE FOLDER VARIABLES and BUILDS MAP FROM THE TMX FILE ETC
	def load_data(self):
		self.game_folder = os.path.dirname(__file__)
		self.map_folder = os.path.join(self.game_folder, "levels")
		self.image_folder = os.path.join(self.game_folder, "images")
		self.mob_folder = os.path.join(self.image_folder, "enemies")
		self.tower_folder = os.path.join(self.image_folder, "towers")

		self.map = Tiled_map(os.path.join(self.map_folder, "level.tmx"))
		self.map_img = self.map.make_map()
		self.map_rect = self.map_img.get_rect()

		self.all_sprites = pg.sprite.Group()
		self.mobs = pg.sprite.Group()
		self.towers = pg.sprite.Group()
		self.projectiles = pg.sprite.Group()
		self.player = pg.sprite.Group()
		self.coins = pg.sprite.Group()

	# RUNS ON __init__ , CALLS VARIOUS METHODS TO SET UP INITIAL DATA AS STATED BELOW
	def new(self):
		# Loads map data from txt file
		self.load_data()

		# Creates map for TMX level file
		self.create_map()

		# Loads all images and sound files to dictionaries
		self.initialize_media()

		# Loads image of a 32x32 gridline for use when placing towers
		self.prep_grid()

		self.construction_menu = Construction_menu(self)  # Build the construction meny for choosing a tower

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
				self.base_location = pg.Rect(tile_object.x, tile_object.y, tile_object.width, tile_object.height)
			if tile_object.name == "mob_start":
				self.mob_start_offset = int(tile_object.value)
			if tile_object.name == "path_width":
				self.mob_path_width = int(tile_object.value) - 10
			if tile_object.name == "path_rect":
				self.path_rects.append(pg.Rect(tile_object.x, tile_object.y, tile_object.width, tile_object.height))

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
		mob_names = [["Orc", MOBSLIM], ["Scorpion", MOBWIDE], ["Purple_Hippo", MOBSLIM]]  # list(self.mob_images.keys())
		actions = ["walk"]
		for mob in mob_names:
			for action in actions:
				self.images["mobs"][mob[0]] = {action: []}
				folder = os.path.join(self.mob_folder, f"{mob[0]}\\{action}")
				for number in range(len(fnmatch.filter(os.listdir(folder), '*.png'))):
					new_image = pg.image.load(os.path.join(folder, f"{action}_{number}.png")).convert_alpha()
					orig_size = new_image.get_size()
					scale = (orig_size[0] / mob[1]) / 1.2
					new_image = pg.transform.scale(new_image, (int(orig_size[0] / scale), int(orig_size[1] / scale)))
					self.images["mobs"][mob[0]][action].append(new_image)

		# Tower images
		self.images["towers"] = {}
		self.tower_names = ["stone", "fire", "archer", "sand"]
		parts = ["tower", "particles", "animation"]
		# len(fnmatch.filter(os.listdir(dirpath), '*.txt'))

		temp_folder = os.path.join(self.tower_folder, f"{self.tower_names[0]}\\{parts[0]}")
		image = pg.image.load(os.path.join(temp_folder, f"0.png")).convert_alpha()
		orig = image.get_size()
		tower_scale = orig[0] / TOWERSIZE[0]
		for tower in self.tower_names:
			for part in parts:
				if part == "tower":
					self.images["towers"][tower] = {part: []}
				else:
					self.images["towers"][tower][part] = []

				folder = os.path.join(self.tower_folder, f"{tower}\\{part}")
				for number in range(len(fnmatch.filter(os.listdir(folder), '*.png'))):
					new_image = pg.image.load(os.path.join(folder, f"{number}.png")).convert_alpha()
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
			new_image = pg.image.load(os.path.join(self.tower_folder, f"icons\\{icon}.png")).convert_alpha()
			# self.icons[icon] = new_image
			self.images["icons"].append(new_image)

		# Health bar images for mobs
		h_images = ["health_bar_red", "health_bar_green"]
		self.health_bar_images = []
		for i in h_images:
			new_image = pg.image.load(os.path.join(self.image_folder, f"health_bar\\{i}.png")).convert_alpha()
			new_image = pg.transform.scale(new_image, (int(MOBSIZE * 1.5), MOBSIZE // 3))
			# change_alpha(new_image, 200)
			self.health_bar_images.append(new_image)

		# Other unsorted images

		images_to_load = [["heart", HUD_IMAGE_SIZE], ["gold_star", HUD_IMAGE_SIZE], ["build_hammer", HAMMERSIZE]]
		for i in images_to_load:
			new_image = pg.image.load(os.path.join(self.image_folder, f"HUD\\{i[0]}.png")).convert_alpha()
			new_image = pg.transform.scale(new_image, i[1])
			self.images[i[0]] = new_image

		# Dirty insert of another image (TODO: tidy up and condense the above into one thing)
		images_to_load = [["coin", COINSIZE]]
		for i in images_to_load:
			image_list = []
			folder = os.path.join(self.image_folder, f"{i[0]}")
			for num in range(len(fnmatch.filter(os.listdir(folder), '*.png'))):
				new_image = pg.image.load(os.path.join(folder, f"{num}.png")).convert_alpha()
				orig_size = new_image.get_size()
				scale = (orig_size[1] / i[1])
				new_image = pg.transform.scale(new_image, (int(orig_size[0] / scale), int(orig_size[1] / scale)))
				image_list.append(new_image)
			self.images[i[0]] = image_list

		self.images["menu"] = {}
		HUD_images = [["tower_construct_menu", 1], ["tower_build_menu", 0.7], ["bottom_bar", 1]]
		for img in HUD_images:
			image = pg.image.load(os.path.join(self.image_folder, f"menu\\{img[0]}.png")).convert_alpha()
			orig = image.get_size()
			image = pg.transform.scale(image, (int(orig[0] * img[1]), int(orig[1] * img[1])))
			self.images["menu"][img[0]] = image


		self.bottom_bar_rect = self.images["menu"]["bottom_bar"].get_rect(bottomleft=self.screen_rect.bottomleft)

		# Setup game Clock
		self.clock_font = pg.font.Font(None, 50, bold=True)
		self.clock_text = outline_text(self.clock_font, "00", colours["white"], colours["black"])
		self.clock_rect = self.clock_text.get_rect(center=(self.screen_width // 2, 20))

		# Load and setup Coin display
		self.coin_font = pg.font.Font(None, 50, bold=True)
		self.coin_text = outline_text(self.coin_font, str(int(self.money)), colours["white"], colours["black"])
		self.coin_rect = self.coin_text.get_rect(
			center=(self.bottom_bar_rect.width * .75, self.bottom_bar_rect.center[1]))

		# Load and setup life display
		self.lifes_font = pg.font.Font(None, 50, bold=True)
		self.lifes_text = outline_text(self.lifes_font, str(self.lifes), colours["white"], colours["black"])
		self.lifes_rect = self.coin_text.get_rect(midright=self.bottom_bar_rect.midright)  # + vec(-5, 0))

		self.skip_font = pg.font.Font(None, 35, bold=True)
		self.skip_text = outline_text(self.skip_font, "Press 'S' to commense to the next wave early", colours["white"], colours["black"])
		self.skip_text_rect = self.skip_text.get_rect(center = self.bottom_bar_rect.midtop + vec(0, -25))

		self.construct_rect = self.images["build_hammer"].get_rect(midbottom=self.bottom_bar_rect.midbottom)

	# PREPS AN OUTLINE OF A 32x32 GRID (used on dev view)
	def prep_grid(self):
		self.empty_grid = pg.Surface((SCREENWIDTH, SCREENHEIGHT))

		for x in range(0, SCREENWIDTH // TILESIZE + 1):
			for y in range(0, SCREENHEIGHT // TILESIZE + 1):
				pg.draw.rect(self.empty_grid, colours["white"], (TILESIZE * x, TILESIZE * y, TILESIZE, TILESIZE), 1)

		self.empty_grid.set_colorkey(colours["black"])
		self.empty_grid.set_alpha(100)


	def new_game(self):
		self.clock = pg.time.Clock()


	# Basic implementation of waves (TODO: pack data into different form and make more elegant)
	def setup_waves(self):
		self.wave_active = False
		self.wave_complete = False
		self.pre_wave_setup = True 	# Variable used to not add to the wave number during the first pregame timer
		self.next_wave_timer = WAVETIMER

		self.waves = [[[0, 10], [1, 15], [2, 0]], [[0, 10], [1, 10], [2, 0]], [[0, 10], [1, 20], [2, 5]], [[0, 10], [1, 25], [2, 20]]]

		self.wave_number = 0

		self.wave = self.waves[self.wave_number]

	# SPAWNS THE ENEMY when the "time" ARGUMENT HAS PASSED
	def handle_wave(self, dt, time_delay = 0.5):  # SPAWNS MOBS

		self.mob_timer += dt
		mob = [Orc, Scorpion, Purple_Hippo]
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
					mob[self.wave[num][0]](self)  # Spawn that refence mob (passing the game instance into the class)

				self.mob_timer = 0  # reset time
			elif len(self.mobs) == 0:
				self.mob_timer = 0
				print("wave over")
				self.wave_active = False
				self.wave_complete = True


	def next_wave(self):
		if not self.pre_wave_setup:
			self.wave_number += 1
		self.pre_wave_setup = False
		self.wave_complete = False
		self.wave = self.waves[self.wave_number]
		print(f"changed wave to {self.wave}")
		self.wave_active = True


	def wave_countdown(self, dt):
		self.next_wave_timer -= dt
		if self.next_wave_timer <= 0:
			self.next_wave()
			self.next_wave_timer = WAVETIMER


	# Method to choose a tower temporary (TODO: intregrate choice to a menu and change/remove this method to suit this)
	def new_tower(self, tower_name):
		# if cost <= self.player_money:
		tower_spawn = {"stone": Stone, "fire": Fire, "archer": Archer, "sand": Sand}  # , Sand]
		self.click = False
		if self.building_tower == False:
			self.building_tower = tower_spawn[tower_name](self, self.mpos)
			self.show_construct_menu = False

	# Deducts a life from the player and ends game upon losing all lifes
	def lose_life(self, number):
		self.lifes -= number
		self.lifes_text = outline_text(self.lifes_font, str(self.lifes), colours["white"], colours["black"])
		if self.lifes == 0:
			print("YOU LOST")
			self.defeated = True

	# DRAWS OVERLAYS FOR MORE INFORMATION AND FOR TROUBLESHOOTING
	def draw_overlays(self, screen):
		for mob in self.mobs:
			mob.draw_vectors(screen)
			pg.draw.rect(screen, colours["red"], mob.rect, 1)

		for point in self.locations:
			pg.draw.circle(screen, colours["red"], point, 8)

		for tower in self.towers:
			if tower.placed:
				tower.draw_overlays(screen)
		for rect in self.map.obstacles:
			pg.draw.rect(screen, colours["red"], rect, 2)

		rects = [self.clock_rect, self.coin_rect, self.lifes_rect]
		for rect in rects:
			pg.draw.rect(screen, colours["red"], rect, 1)

		self.handle_grid(False)

	# BLITS WHITE SQUARE ON CURRENT SELECTED SQUARE OF MAP WHEN CREATING/MOVING TOWERS (pass false to enable drawing of the grid (dev view))
	def handle_grid(self, tower=True):
		screen = self.screen
		self.grid = self.empty_grid.copy()
		mpos = pg.mouse.get_pos()
		mpos = ((mpos[0] // 32) * 32, (mpos[1] // 32) * 32)
		if not tower:
			highlight_surf = pg.Surface((TILESIZE, TILESIZE))
			highlight_surf.fill(colours["white"])
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

		elif self.construct_rect.collidepoint(mpos):
			self.show_construct_menu = not self.show_construct_menu

		if self.selected_tower != False:  # If theres a tower selected

			if self.selected_tower.rect.collidepoint(mpos):  # If you click the same tower again
				self.selected_tower.selected = False  # Tower state change to False
				self.selected_tower = False  # Game's selected tower set to False

			elif self.selected_tower.menu.rect.collidepoint(mpos):  # and the mouse is clicked inside the menu rect of that tower
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
						if self.selected_tower != False and self.selected_tower != tower:  # If the tower you clicked isnt the same as the one already selected
							self.selected_tower.selected = False
						self.selected_tower = tower
						tower.selected = True

				if len(
						tower_collide) == 0:  # If you didnt click on any other tower (i.e. you clicked onto the map somewhere)
					self.selected_tower.selected = False  # Deselect everything
					self.selected_tower = False

		else:   # There's no tower selected before you clicked (check if you clicked a tower)
			for tower in self.towers:
				if tower.rect.collidepoint(mpos):
					# print("clicked on tower")
					if self.selected_tower != False and self.selected_tower != tower:
						self.selected_tower.selected = False
					self.selected_tower = tower
					tower.selected = True

	# GAME UPDATE LOOP
	def update(self, mpos, dt):

		if self.wave_active:
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

		# Update Clock ( TODO: put in seperate method)
		self.time += dt
		time_display = str(int(self.time))
		if len(str(int(self.time))) < 1:
			time_display = f"0{str(int(self.time))}"

		self.clock_text = outline_text(self.clock_font, time_display, colours["white"], colours["black"])
		self.coin_text = outline_text(self.coin_font, str(self.money), colours["white"], colours["black"])

	# Draws the lifes, time, coins and images next to them
	def draw_HUD(self, screen):
		spacer = vec(5, 1)
		screen.blit(self.images["menu"]["bottom_bar"], self.bottom_bar_rect)
		screen.blit(self.clock_text, self.clock_rect)  # Blit game clock
		screen.blit(self.coin_text, self.coin_rect)  # Blit money amount
		screen.blit(self.images["heart"],
					self.images["heart"].get_rect(midright=self.lifes_rect.midleft - spacer))  # + self.lifes_rect.y))
		screen.blit(self.images["gold_star"],
					self.images["gold_star"].get_rect(midright=self.coin_rect.midleft - spacer))  # + self.coin_rect.y))
		screen.blit(self.lifes_text, self.lifes_rect)
		screen.blit(self.images["build_hammer"], self.construct_rect)

		if self.show_construct_menu:
			self.construction_menu.draw(screen)

	# Draw loop (TODO: Tidy up into methods)
	def draw(self, screen):

		screen.fill(colours["black"])
		screen.blit(self.map_img, self.screen_rect)  # Blit map

		if self.draw_grid:
			self.handle_grid()
		if self.draw_overlay:
			self.draw_overlays(screen)
		for sprite in sorted(self.all_sprites, key=lambda spr: spr.rect.bottom):    #sorts blitting order (sprites that is the lowest on the screen postion gets blitted over the top of anything above it)
			sprite.draw(screen)
		for i in self.projectiles:
			i.draw(screen)
		if self.selected_tower != False:
			self.selected_tower.menu.draw(screen)

		if not self.wave_active:
			screen.blit(self.skip_text, self.skip_text_rect)

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
					#sys.exit()
					#pg.quit()
					return False

				if event.type == pg.KEYDOWN:
					if event.key == pg.K_ESCAPE:
						if self.building_tower != False:
							self.building_tower = False
							for tower in self.towers:  # player cancelled the building of the tower. Now loop through towers and delete any that aren't placed.
								if not tower.placed:
									pg.sprite.Sprite.kill(tower)
							del tower

						elif self.selected_tower != False:
							self.selected_tower.selected = False
							self.selected_tower = False
						else:
							return False
							#sys.exit()

					if event.key == pg.K_i:  # and self.delay_counter == 0:
						# self.delay_counter = 1
						self.draw_overlay = not self.draw_overlay
						self.print = True

					if event.key == pg.K_s:
						if not self.wave_active:
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
							for tower in self.towers:  # player cancelled the building of the tower. Now loop through towers and delete any that aren't placed.
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


playing = True
g = Game()
while True:
	start = main_menu(g.map_img)
	if start:
		g.new_game()
		start = g.run()
