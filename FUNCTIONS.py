from os import path
import numpy as np
from PIL import Image
from SETTINGS import *


def particles(colours):
    col_list = [colours["red"], colours["orange"], colours["yellow"]]
    x, y = self.pos
    self.tracers.append([[x, y], [rand.randint(0, 20) / 10 - 1, rand.randint(0, 40) / 10 - 2], rand.randint(2, 4),
                         col_list[rand.randint(0, len(col_list) - 1)]])

    for particle in self.tracers:
        particle[0][0] += particle[1][0]
        particle[0][1] += particle[1][1]
        particle[2] -= 0.1
        particle[1][1] += 0.05
        if particle[2] <= 0:
            self.tracers.remove(particle)

def find_rgb(game, colour):
    img = Image.open(path.join(game.tower_folder, f"build_menu.png"))
    img = img.convert("RGB")
    pix = img.load()
    r_query, g_query, b_query = colour
    # print(r_query, g_query, b_query)
    coordinates = []
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            r, g, b = pix[x, y]
            if matching_algo(r, g, b, r_query, g_query, b_query):
                # print("{},{} contains {}-{}-{} ".format(x, y, r, g, b))
                coordinates.append((x, y))
    #print(coordinates)


def matching_algo(r, g, b, r_query, g_query, b_query):
    if r == r_query and g == g_query:
        return True
    elif r == r_query and b == b_query:
        return True
    elif b == b_query and g == g_query:
        return True
    else:
        return False


def change_alpha(img, alpha=255):
    chan = pg.surfarray.pixels_alpha(img)
    chan2 = np.minimum(chan, np.ones(chan.shape, dtype=chan.dtype)) * alpha
    np.copyto(chan, chan2)
    del chan


def find_location_colour(img, colour):
    r = 0
    g = 1
    b = 2
    img = pg.surfarray.pixels_alpha(img)
    r_query = 255
    g_query = 0
    b_query = 255
    location = []
    location.append((np.where((img[r] >= r_query) & (img[g] >= g_query) & (img[b] <= b_query))))
    print(location)


# Function found online to draw hollow text (no credit to me here)
def hollow_text(font, message, fontcolor):
    notcolor = [c ^ 0xFF for c in fontcolor]
    base = font.render(message, 0, fontcolor, notcolor)
    size = base.get_width() + 2, base.get_height() + 2
    img = pg.Surface(size, 16)
    img.fill(notcolor)
    base.set_colorkey(0)
    img.blit(base, (0, 0))
    img.blit(base, (2, 0))
    img.blit(base, (0, 2))
    img.blit(base, (2, 2))
    base.set_colorkey(0)
    base.set_palette_at(1, notcolor)
    img.blit(base, (1, 1))
    img.set_colorkey(notcolor)
    return img


# Function found online to outline text (no credit to me here)
def outline_text(font, message, fontcolor, outlinecolor):
    base = font.render(message, 0, fontcolor)
    outline = hollow_text(font, message, outlinecolor)
    img = pg.Surface(outline.get_size(), 16)
    img.fill(colours["magenta"])
    img.blit(base, (1, 1))
    img.blit(outline, (0, 0))
    img.set_colorkey(colours["magenta"])
    return img


"""# Simple button class
class Button:
	def __init__(self, game, menu, x, y, width, height, colour, button_image = False, button_value = False):
		self.game = game
		self.menu = menu
		self.width = width
		self.height = height
		self.x, self.y = x, y
		self.colour = colours[colour]
		self.create_button()
		self.action = button_image
		self.button_value = button_value
		if button_image != False:
			self.button_image = button_image
			self.generate_images()
			self.render_value()
		else:
			self.button_image = False

	def create_button(self):
		self.surface = pg.Surface((self.width, self.height))
		self.surface.fill(self.colour)
		self.rect = self.surface.get_rect(topleft = (self.x, self.y))

	def generate_images(self):
		self.text_font = pg.font.Font(None , 20, bold=True)
		self.text = outline_text(self.text_font, self.button_image, colours["white"], colours["black"])
		self.text_rect = self.text.get_rect(midtop = (self.rect.midtop + vec(0,2)))

	def render_value(self):
		self.val_font = pg.font.Font(None , 30, bold=True)
		if self.action == "Sell":
			self.val_text = outline_text(self.val_font, f" +{self.button_value}", colours["white"], colours["black"])
		else:
			self.val_text = outline_text(self.val_font, str(self.button_value), colours["white"], colours["black"])
		self.val_text_rect = self.val_text.get_rect(midbottom = (self.rect.midbottom + vec(0,-2)))"""

"""# Simple class to build up a menu using the above
class Tower_menu:
	def __init__(self, game, tower):
		self.game = game
		self.tower = tower
		self.type = self.tower.type
		self.build_surface()
		self.build_buttons()
		self.update_button_values()

	def build_surface(self):
		self.surface = pg.Surface((round(self.tower.width*4.2), self.tower.height//1))
		self.surface.fill(colours["white"])
		self.rect = self.surface.get_rect(center = self.tower.image_rect.center)

	def build_buttons(self):
		self.buttons = Surface_buttons(self.game, self, self.surface, "x", 3)

		self.rect.center -= vec(0, 2)

	def update_button_values(self):
		for button in self.buttons:
			if self.tower.level < len(self.tower.cost): 
				if button.action == "Upgrade":
					button.button_value = self.tower.cost[self.tower.level]
				elif button.action == "BLAH":
					button.button_value = 30
			if button.action == "Sell":
				button.button_value = int(self.tower.cost[0] * (0.75*self.tower.level))
			button.render_value()

	def draw(self, screen):
		#print("menu draw")
		pg.draw.rect(screen, colours["blue"], self.rect)
		for button in self.buttons:
			self.surface.blit(button.surface, button.rect)
			pg.draw.rect(self.surface, colours["black"], button.rect, 1)
			if button.button_image != False:
				#self.surface.blit(button.button_image, button.button_image_rect)
				self.surface.blit(button.text, button.text_rect)
				self.surface.blit(button.val_text, button.val_text_rect)
				#pg.draw.circle(self.surface, colours["black"], button.button_image_rect.center, int(button.button_image_rect.width/2+1), 1)
		screen.blit(self.surface, self.rect)
		pg.draw.rect(screen, colours["black"], self.rect, 1)
		
		
# Quick and easy button drawing function that spaces out buttons and resizes them based on the amount you need and the surface size you pass (TODO: clean up and make more functional)
def Surface_buttons(game, menu, surface, direction, button_total, spacing=4):
		# pass a surface and what direction you want the buttons to be and how many buttons
		total_width = surface.get_width()
		total_height = surface.get_height()

		if direction == "x":
			button_width = (total_width - (spacing*(button_total+1))) / button_total
			button_height = total_height - spacing*2
		elif direction == "y":
			button_width = total_width - spacing*2
			button_height = (total_height - (spacing*(button_total+1))) / button_total
		else:
			print("direction incorrect, choose 'x' or 'y'")

		buttons = []
		button_images = ["Upgrade", "BLAH", "Sell"]
		button_value = [str(menu.tower.cost[menu.tower.level-1]), "30", int(menu.tower.cost[0]*0.75)]
		for num, button in enumerate(range(button_total)):
			button = Button(game, menu, (spacing + (button_width*num) + spacing*num), spacing, button_width, button_height, "red", button_images[num], button_value[num])
			buttons.append(button)
		return buttons"""
