from GameMenus import *
from ProjectileClass import *
from CoinClass import *
import itertools


# Individual tower radius, damage, speed, cooldown, splash radius all passed up from child class at the bottom of this page
class Tower(pg.sprite.Sprite):
	def __init__(self):
		self.groups = self.game.towers, self.game.all_sprites
		pg.sprite.Sprite.__init__(self, self.groups)
		self.tower_images = self.game.images["towers"][self.name]["tower"]
		self.particle_images = self.game.images["towers"][self.name]["particles"]
		self.animate_images = self.game.images["towers"][self.name]["animation"]
		self.image = self.tower_images[self.level-1]
		self.image_rect = self.image.get_rect()
		self.rect = pg.Rect(0, 0, TILESIZE*TOWER_MULTIPLIER, TILESIZE) #for collisions
		self.width, self.height = self.image.get_size()

		fire_modes = ["HQ", "High HP", "Low HP", "Fast", "Slow"]
		self.fire_modes = itertools.cycle(fire_modes)
		self.fire_mode = next(self.fire_modes)
		self.target = False
		self.attack_timer = 0
		self.cooldown_timer = 0
		self.placed = False
		self.selected = False
		self.projectile = False
		self.menu = "" # This is built once tower is placed
		if self.platform:
			self.update_attack_images()
		self.setup_animation_values()
		


	# Based on the specific child class of tower, prep the image of its radius
	def prep_radius(self):
		self.rad_surface = pg.Surface((self.radius*2, self.radius*2))
		self.rad_surface.fill(colours["magenta"])
		self.rad_rect = self.rad_surface.get_rect()
		pg.draw.circle(self.rad_surface, colours["gray"], self.rad_rect.center, self.radius)
		pg.draw.circle(self.rad_surface, colours["white"], self.rad_rect.center, self.radius, 1)
		self.rad_surface.set_colorkey(colours["magenta"])
		self.rad_surface.set_alpha(50)
		self.rad_rect.center = self.rect.center


	# Function thats passed intially and when the tower updates to set the attack platform images of the tower and position them corrently. (TODO: tweak a better, less hard coded formula)
	def update_attack_images(self):
		if self.platform:
			# THIS IS THE PLATFORM THAT FIRES THE PROJECTILE
			if self.level < 3:						# use lower level images for firing section
				self.front = self.animate_images[0]
				self.back = self.animate_images[1]
			else:									# use the higher level looking firing images
				self.front = self.animate_images[2]
				self.back = self.animate_images[3]

			if self.name == "Stone":
				self.f_offset = vec(-2, 3)
				self.b_offset = vec(0, 2)

			elif self.name == "Sand":
				self.f_offset = vec(-4, -2)
				self.b_offset = vec(0, 4)

			elif self.name == "Fire":
				self.f_offset = vec(-2, -10)
				self.b_offset = vec(0, 8)
				# correction to center properly

			self.f_rect = self.front.get_rect(midtop = self.image_rect.center + self.f_offset) # front section rect
			self.b_rect = self.back.get_rect(midbottom = self.f_rect.midtop + self.b_offset) # back section rect


			self.orig_f_rect = self.f_rect.copy()


	# setup the values of how many pixels are from the bottom of the firing platform to the top, and also how quick the attack time will be for the tower (taken from child class)
	def setup_animation_values(self):
		if self.platform:
			direction_vec = vec(self.b_rect.top - self.image_rect.top) # distance in pixels how much we have to move to hit the top
			pixels = direction_vec.length() 

			self.pixels = int(abs(pixels)*.8) # total of pixels to move the platform up from the bottom to the top of the animation ( *.7 = only using 70% of the distance)

		self.attack_time = 	self.attack_speed/FPS


	# animate the firing platform when the attack timer has begun (set by the update loop after cooldown is done and the tower also has a target ready)
	def animate(self):
		self.amount = self.attack_timer/self.attack_animation_time  # 0-1 measures how far the attack_timer is towards the end of the timer with a value 0-1 ( 0.5 = 50% , 1 = 100% etc) 

		self.f_rect.midtop = self.orig_f_rect.midtop + vec(0, -(self.pixels*(self.amount))) # front section rect move rect by total pixels multiplied by the progress of the timer to 100%
		self.b_rect.midbottom = self.f_rect.midtop + self.b_offset								# matches the back platform rect to the needed position dependant on the front rects ( + correction vec)


	# Handle the 2 timers (attack_timers - used for the platform animation) and the (cooldown_timer - used to delay the next shots time depending on the stats of the tower)
	def handle_attack_timers(self, dt):

		if self.attack_timer > 0:
			self.attack_timer += FPS*dt
		if self.attack_timer >= self.attack_animation_time:
			self.projectile.shot = True
			self.projectile.set_target(self.target)
			self.projectile = False
			self.attack_timer = 0
			self.reset_animation()

		if self.cooldown_timer > 0:
			self.cooldown_timer += FPS*dt
		if self.cooldown_timer >= self.attack_cooldown:
			self.cooldown_timer = 0


	# Once the projectile has release, reset the animation to 0 (TODO: code and slow descend down to start position)
	def reset_animation(self):
		if self.platform:
			self.f_rect.midtop = self.image_rect.center + self.f_offset
			self.b_rect.midbottom = self.f_rect.midtop + self.b_offset


	# Function to call to make it easier to set the new stat values of the tower once it updates.
	def level_up_values(self):
		self.update_stats()
		self.update_attack_images()
		self.setup_animation_values()
		self.prep_radius()


	# Main update loop (TODO: tidy up and move bits to other functions)
	def update(self, dt):
		if self.placed:
			self.handle_attack_timers(dt) # handles the shooting platform animation timer and cooldown (this function also attacks the relevant mob when timer at the correct point)
			if self.platform:
				self.animate()

			if self.attack_timer == 0:
				self.check_targets()

			# If you have a target and the delay is still 0. Attack the target.
			if self.attack_timer == 0 and self.cooldown_timer == 0: 
				if self.projectile == False:
					self.projectile = Projectile(self.game, self)
				if self.target != False:
					self.attack_timer = 1 			# add to the delay variable to begin a delay to animate the shooting platform	
					self.cooldown_timer = 1			# add to the delay variable to begin a cooldown timer (which is equal to the attack timer + the cooldown before it can shoot again)

		else:
			self.handle_purchase()


	#When the menu is displayed, check if a button has been clicked
	def handle_menu_click(self, mpos):
		for button in self.menu.buttons: 		# check through buttons
			# - vec(self.menu.rect.topleft)):# if the mouse was clicked on one of them. Do the related action/checks
			if button.rect.collidepoint(mpos):
				if button.action == "upgrade":
					if self.handle_upgrade():
						if self.level - 2 < len(self.cost):
							#pass
							self.menu.update_button_values()
						else:
							pass
							# todo, blit greyed out image on upgrade
				elif button.action == "choose":
					self.fire_mode = next(self.fire_modes)
					self.menu.update_button_values()
					print("choose")
				elif button.action == "sell":
					for i in range(button.button_value):
						Coins(self.game, self, 25)

					self.game.selected_tower = False
					pg.sprite.Sprite.kill(self)
					del self

	# Checks if the player can upgrade the tower
	def handle_upgrade(self):
		if self.level < len(self.cost) and self.cost[self.level] <= self.game.money:

			self.game.money -= int(self.cost[self.level])
			#print("paid", self.cost[self.level-1])
			self.level += 1
			self.level_up_values()

			self.image = self.tower_images[self.level-1]
			self.image_rect = self.image.get_rect(midbottom = self.image_rect.midbottom)
			return True

		elif self.level < len(self.cost) and self.cost[self.level] > self.game.money:
			print("NOT ENOUGH MONEY FOR UPGRADE")
			return False

		else:
			print("MAX LEVEL REACHED")
			return False

	# This is called when the tower is selected to be purchased, handles the image following the mouse (on a grid format) and whether it can be purchased whe nthe user clicks
	# if it can it sets the relevant values and calls the relevant functions needed to intiate the tower
	def handle_purchase(self):
		if self.game.building_tower != False:
			# Grid position
			self.tower_sq_pos = ((self.game.mpos[0]//TILESIZE) * TILESIZE, (self.game.mpos[1]//TILESIZE) * TILESIZE)
			self.tower_pos = pg.rect.Rect(self.tower_sq_pos[0], self.tower_sq_pos[1], TILESIZE*TOWER_MULTIPLIER, TILESIZE)

			self.rect = self.tower_pos
			self.image_rect.midbottom = self.rect.midbottom
			if self.platform:
				self.f_rect.midtop = self.image_rect.center + self.f_offset # front section rect
				self.b_rect.midbottom = self.f_rect.midtop + self.b_offset

			# If the player clicks check we are allowed to use this position (check collision with path)
			if self.game.click:
				collide_list = []
				for rect in self.game.path_rects:
					if rect.colliderect(self.tower_pos):
						print("cant place on path")
						collide_list.append("True")

				for rect in self.game.map.obstacles:
					if rect.colliderect(self.tower_pos):
						print("cant place on scenery")
						collide_list.append("True")

				# If we are not placing the first tower, check for collisions with other towers
				if len(self.game.towers) > 1:
					for tower in self.game.towers:
						# Check new tower doesnt collide (excluding colliding with itself)
						if pg.sprite.collide_rect(tower, self) and tower != self:
							print("cant place here, tower already here")
							collide_list.append("True")

				if len(collide_list) == 0:
					cost = self.cost[self.level-1]
					if cost <= self.game.money:
						self.game.money -= int(cost)
						self.image.set_alpha(255)
						self.check_targets()
						self.placed = True
						self.game.building_tower = False
						self.image_rect.midbottom = self.rect.midbottom #pg.Rect(tower_sq_pos[0], tower_sq_pos[1], TILESIZE, TILESIZE)
						self.menu = TowerMenu(self.game, self)
						self.level_up_values()
					else:
						print(f"you cannot afford this tower. You need {cost} coins")

	# This check if a mob is within its radius (TODO: Call this within game once and pass a filtered list to each tower to save processing time)
	def check_targets(self):
		self.targets = []
		f_m = self.fire_mode

		for mob in self.game.mobs:
			if pg.sprite.collide_circle(self, mob) and mob.alive:
				self.targets.append(mob)

		if len(self.targets) != 0:

			if f_m == "HQ":
				self.targets.sort(key=lambda x: (-x.turn_count, x.dist_from_target))
			elif f_m == "Low HP":
				self.targets.sort(key=lambda x: x.health)
			elif f_m == "High HP":
				self.targets.sort(key=lambda x: -x.health)
			elif f_m == "Fast":
				self.targets.sort(key=lambda x: -x.speed)
			elif f_m == "Slow":
				self.targets.sort(key=lambda x: x.speed)

			self.target = self.targets[0]
		else:
			self.target = False

	# Overlays for "dev view"
	def draw_overlays(self, screen):
		pg.draw.circle(screen, colours["gray"], self.rect.center, self.radius, 3)
		if len(self.targets) != 0:
			for target in self.targets:
				pg.draw.line(screen, colours["lightblue"], self.rect.center, target.rect.center, 4)
			pg.draw.line(screen, colours["red"], self.rect.center, self.targets[0].rect.center, 4)
			pg.draw.rect(screen, colours["white"], self.targets[0], 5)
		
	# Method to organise the draw order of the tower (main image, front of platform, back of platform, projectile etc)
	def draw_tower(self, screen):
		if self.platform:
			screen.blit(self.back, self.b_rect)
			if self.projectile != False:
				screen.blit(self.projectile.image, self.projectile.rect)
			screen.blit(self.image, self.image_rect)
			screen.blit(self.front, self.f_rect)
		else:
			screen.blit(self.image, self.image_rect)

	# Draw loop
	def draw(self, screen):

		if self.placed:
			self.draw_tower(screen)

		if self.selected:
			screen.blit(self.rad_surface, self.rad_rect)

		else:
			if self.game.building_tower != False:
				pg.draw.circle(screen, colours["gray"], self.rect.center, self.radius, 3)
				self.draw_tower(screen)


# Towers
class Stone(Tower):
	def __init__(self, game, pos):
		self.name = "Stone"
		self.game = game
		self.pos = pos
		self.level = 1
		self.cost = [40, 50, 75]
		self.firing_type = "splash"
		self.platform = True
		self.update_stats()
		super().__init__()

	def update_stats(self):
		self.radius = int((TILESIZE//1.5 * (4 + int(self.level*1.5)))*TOWER_RADIUS_MULTIPLIER)
		self.damage = 3 + (self.level * 2)
		self.attack_speed = FPS*2.5 - ((self.level-1) * 4)
		self.attack_cooldown = self.attack_speed*.9
		self.attack_animation_time = 20  # self.attack_speed - self.attack_cooldown
		self.loop_height = 50  # amount of pixels the projectile loops in the air when shot toward target
		self.splash = 45 + (self.level * 5)


class Fire(Tower):
	def __init__(self, game, pos):
		self.name = "Fire"
		self.game = game
		self.pos = pos
		self.level = 1
		self.cost = [35, 60, 75]
		self.firing_type = "splash"
		self.platform = True
		self.update_stats()
		super().__init__()

	def update_stats(self):
		self.radius = int((TILESIZE//1.5 * (5 + int(self.level*1.5)))*TOWER_RADIUS_MULTIPLIER)
		self.damage = 2.3 + (self.level * 2)
		self.attack_speed = FPS*3 - ((self.level-1) * 5)
		self.attack_cooldown = self.attack_speed*.9
		self.attack_animation_time = 15  # self.attack_speed - self.attack_cooldown
		self.loop_height = 80  # amount of pixels the projectile loops in the air when shot toward target
		self.splash = 55 + (self.level * 5)


class Sand(Tower):
	def __init__(self, game, pos):
		self.name = "Sand"
		self.game = game
		self.pos = pos
		self.level = 1
		self.cost = [30, 55, 75]
		self.firing_type = "splash"
		self.platform = True
		self.update_stats()
		super().__init__()

	def update_stats(self):
		self.radius = int((TILESIZE//1.5 * (6 + int(self.level*1.5)))*TOWER_RADIUS_MULTIPLIER)
		self.damage = 5 + (self.level * 2)
		self.attack_speed = FPS*3.5 - ((self.level-1) * 3)
		self.attack_cooldown = self.attack_speed
		self.attack_animation_time = 15
		self.loop_height = 80  # amount of pixels the projectile loops in the air when shot toward target
		self.splash = 55 + (self.level * 5)

class Archer(Tower):
	def __init__(self, game, pos):
		self.name = "Archer"
		self.game = game
		self.pos = pos
		self.level = 1
		self.cost = [35, 60, 80]
		self.firing_type = "direct"
		self.platform = False
		self.update_stats()
		super().__init__()

	def update_stats(self):
		self.radius = int((TILESIZE//1.5 * (6 + int(self.level*1.5)))*TOWER_RADIUS_MULTIPLIER)
		self.damage = 0 + (self.level * 2)
		self.attack_speed = FPS*1 - ((self.level-1) * 3)
		self.attack_cooldown = self.attack_speed
		self.attack_animation_time = self.attack_speed*0.2
		self.loop_height = 0  # amount of pixels the projectile loops in the air when shot toward target
		self.splash = 0