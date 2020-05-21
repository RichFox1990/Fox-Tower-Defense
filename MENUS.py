from SETTINGS import *
from FUNCTIONS import *
import sys

def main_menu(img):
	start_game = False
	screen_width = SCREENWIDTH//2
	screen_height = SCREENHEIGHT
	screen = pg.display.set_mode((screen_width, screen_height))
	screen_rect = screen.get_rect()

	font = pg.font.Font(None, 35, bold=True)
	game_name = outline_text(font, "FOXY TOWERS", colours["white"], colours["black"])
	g_rect = game_name.get_rect(center = screen_rect.midtop + vec(0, screen_height//4))
	instruction = outline_text(font, "Press any button to PLAY", colours["white"], colours["black"])
	i_rect = instruction.get_rect(center = screen_rect.center)
	quit = outline_text(font, "Press 'Esc' to QUIT", colours["white"], colours["black"])
	q_rect = quit.get_rect(center = screen_rect.midbottom + vec(0, -screen_height//4))

	fade = pg.surface.Surface((screen_width, screen_height))
	fade.fill(colours["black"])
	fade.set_alpha(100)

	while not start_game:
		# shorten the pg get pressed function to 'keyPress'
		keyPress = pg.key.get_pressed()

		# Start event loop.
		for event in pg.event.get():
			if event.type == pg.QUIT:
				sys.exit()

			if event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					sys.exit()

				else:
					screen = pg.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
					return True


		#screen.fill(colours["green"])
		screen.blit(img, screen_rect)
		screen.blit(fade, screen_rect)
		screen.blit(game_name, g_rect)
		screen.blit(instruction, i_rect)
		screen.blit(quit, q_rect)

		pg.display.set_caption("Foxy Towers")
		pg.display.update()


class Tower_menu:
	def __init__(self, game,
				 tower):  # img = self.game.build_menu_img, button_xy = self.game.build_button_xy, text_xy = self.game.build_text_xy):
		self.game = game
		self.tower = tower
		self.image = self.game.images["menu"]["tower_build_menu"]  # .set_colorkey(colours["black"])
		self.rect = self.image.get_rect(center=self.tower.image_rect.center)
		self.create_level_up_menu()
		self.button_images = self.game.images["icons"]  # list of 4 (change to grabbing info from tower)
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
			new_button = Button(self, image, (self.rect.center + vec(self.button_xy[order[number]])),
								(self.rect.center + vec(self.text_xy[order[number]])), action[number], 12)
			#print(self.rect.center, "+", vec(self.button_xy[order[number]]))
			self.buttons.append(new_button)

	def update_button_values(self):
		for button in self.buttons:
			if self.tower.level < len(self.tower.cost):
				if button.action == "upgrade":
					button.button_value = self.tower.cost[self.tower.level]
				elif button.action == "gem":
					button.button_value = self.tower.level
				elif button.action == "choose":
					button.button_value = self.tower.fire_mode
			if button.action == "sell":
				button.button_value = int(((self.tower.cost[0]) * self.tower.level) * .9)
			button.render_text()

	def draw(self, screen):
		screen.blit(self.image, self.rect)
		# pg.draw.rect(screen, colours["red"], self.rect, 1)
		for button in self.buttons:
			button.draw(screen)
	# pg.draw.rect(screen, colours["red"], button.rect, 1)


class Construction_menu:
	def __init__(self,
				 game):  # img = self.game.build_menu_img, button_xy = self.game.build_button_xy, text_xy = self.game.build_text_xy):
		self.game = game

		self.image = self.game.images["menu"]["tower_construct_menu"]
		self.rect = self.image.get_rect(midbottom=self.game.construct_rect.midtop)
		# self.button_xy =  # Dict of item blit locations (tl, tr, bl, br)
		# self.text_xy =  # Dict of text blit locations (tl, tr, bl, br)
		self.button_height = 55
		self.spacing = int(self.button_height / 10)
		self.start = vec(10, 0)
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
			image = pg.transform.scale(image, (int(orig_size[0] / scale), int(orig_size[1] / scale)))
			self.button_images[tower] = image

	# ["stone", "fire", "archer"]
	def create_buttons(self):
		location = self.start
		self.buttons = {}
		for number, key in enumerate(self.button_images.keys()):
			new_button = Button(self, self.button_images[key],
								(self.rect.midleft + vec((location[0] + self.button_height / 2), location[1])), (
											self.rect.midleft + vec((location[0] + self.button_height / 2),
																	location[1] - self.button_height / 2)),
								self.tower_names[number], 18)
			# print(self.rect.center, "+", vec(self.button_xy[order[number]]))
			self.buttons[key] = new_button
			location += vec(self.spacing + self.button_height, 0)

	def handle_click(self, mpos):
		for key in self.buttons.keys():  # check through buttons
			button = self.buttons[key]
			if button.rect.collidepoint(mpos):
				print("collided", key)
				self.game.new_tower(key)

	def update_button_values(self):
		self.construction_price = {"stone": 30, "fire": 30, "archer": 30, "sand": 35}
		for key in self.buttons.keys():
			# print(button.action)
			self.buttons[key].button_value = self.construction_price[self.buttons[key].action]

	# self.buttons[key].render_text()

	def render_cost_info(self):
		self.font = pg.font.SysFont("Times New Roman", self.font_size, bold=True)
		self.tower_construct_info = {}

		for tower in self.game.tower_names:
			button = self.buttons[tower]
			cost = self.font.render(str(self.construction_price[tower]), True, colours["white"])
			cost_rect = cost.get_rect(midtop=button.rect.midbottom + vec(0, 1))
			name = self.font.render((tower), True, colours["white"])
			name_rect = name.get_rect(midbottom=button.rect.midtop + vec(0, -1))
			self.tower_construct_info[tower] = [cost, cost_rect, name, name_rect]

	def draw_cost_info(self, screen):
		for key in self.tower_construct_info.keys():
			tower = self.tower_construct_info[key]
			screen.blit(tower[0], tower[1])
			screen.blit(tower[2], tower[3])

	def draw(self, screen):
		screen.blit(self.image, self.rect)
		# pg.draw.rect(screen, colours["red"], self.rect, 1)
		for key in self.buttons.keys():
			self.buttons[key].draw(screen)
			pg.draw.rect(screen, colours["gray"], self.buttons[key].rect, 2)
		self.draw_cost_info(screen)


class Button:
	def __init__(self, menu, img, location, t_location, action, font_size, button_value=False):
		self.menu = menu
		self.image = img
		self.action = action
		self.location = location
		self.t_location = t_location
		self.button_value = button_value
		self.font_size = font_size

		# self.text_center = text_center
		# self.offset_vec_to_add = vec(offset_vec_to_add)
		self.build_button()

	def build_button(self):
		self.rect = self.image.get_rect(center=self.location)

	# def generate_text(self):
	# 	self.text_font = pg.font.Font(None , 20, bold=True)
	# 	self.text = outline_text(self.text_font, self.button_image, colours["white"], colours["black"])
	# 	self.text_rect = self.text.get_rect(midtop = (self.rect.midtop + vec(0,2)))

	def render_text(self):
		self.value_font = pg.font.SysFont("Times New Roman", self.font_size, bold=True)
		self.value = self.value_font.render(str(self.button_value), True, colours["white"])
		# self.value = outline_text(self.value_font, str(self.button_value), colours["white"], colours["black"])
		self.value_rect = self.value.get_rect(center=self.t_location)

	def draw(self, screen):
		screen.blit(self.image, self.rect)
		try:
			screen.blit(self.value, self.value_rect)
		except:
			pass
