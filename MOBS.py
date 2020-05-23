import itertools

from OBJECTS import *


class Mob(pg.sprite.Sprite):
	def __init__(self):
		self.groups = self.game.mobs, self.game.all_sprites
		pg.sprite.Sprite.__init__(self, self.groups)
		self.max_health = self.health
		self.health_percentage = self.health / self.max_health
		self.vel = vec(0, 0)#.rotate(uniform(0, 360))
		self.acc = vec(0, 0)
		self.alive = True
		self.death_delay = 0
		self.particles = []

		self.walk_images = self.game.images["mobs"][self.name]["walk"]
		self.image_number = 0
		self.image = self.walk_images[self.image_number]
		self.width, self.height = self.image.get_size()

		self.level_directions = itertools.cycle(self.game.level_directions)
		self.turn_points = itertools.cycle(self.game.level_turns)
		self.target = next(self.turn_points)
		self.target_direction = next(self.level_directions)

		self.turn_count = 0
		self.level_directions = self.game.level_directions
		self.turn_points = self.game.level_turns

		self.target = self.turn_points[self.turn_count]
		self.target_direction = self.level_directions[self.turn_count]

		#mob_path_width comes from level tmx file.
		path_width = int(self.game.mob_path_width)
		random = rand.randint(-int(path_width/2), int(path_width/2))

		#mob_start_offset comes from tmx level file (distance to the center of the starting path)
		self.start_offset = self.game.mob_start_offset + random# - self.height/2

		# depending if the first point the mobs are targeting is either a "x" or "y" vector, do the following (apply this random path offset to the correct coordinate)
		if "y" in self.target_direction:
			self.pos = vec(self.start_offset, MOB_START_POS)
		else:
			self.pos = vec(MOB_START_POS, self.start_offset)

		self.pos -= vec(self.height, self.height)/2 # to account for using the center postion to blit (makes the mobs midbottom appear where the path offset was chosen)

		self.rect = self.image.get_rect(center = self.pos) # now set the rect we use to draw the image equal to the position

		self.prep_shadow()
		self.offset = random # the same random value generated on line 136
		self.original_offset = abs(random)

		if self.offset < 0:
			self.e_or_l = "early"
		else:
			self.e_or_l = "late"
		self.desired = (vec(self.target + self.offset, self.pos.y) - self.pos)

		self.calculate_path_distances()

		self.health_images = self.game.health_bar_images.copy()
		self.health_original_width = self.health_images[1].get_width()
		self.health_original_height = self.health_images[1].get_height()
		self.health_rect = self.health_images[0].get_rect(center = self.rect.midtop + vec(0, -5))

		self.update_animation = time.time()
		self.flipped = False
		self.x_target = "positive"
		self.create_flipped_images()


	# Prep our surface which will imatate shadow under the mob (scales to mobs width)
	def prep_shadow(self):
		shad_height = int(self.height/4)
		if shad_height <=9:
			self.shadow_height = 10
		else:
			self.shadow_height = shad_height
		self.shadow_surface = pg.Surface((self.width, self.shadow_height))
		self.shadow_surface.fill(colours["magenta"])
		self.shadow_rect = self.shadow_surface.get_rect(midbottom = self.rect.midbottom - vec(0, self.shadow_height))
		pg.draw.ellipse(self.shadow_surface, colours["black"], (0,0, self.width, self.shadow_height))
		self.shadow_surface.set_colorkey(colours["magenta"])
		self.shadow_surface.set_alpha(100)


	# Pre create the flipped images we used whe nthe mobs are facing left
	def create_flipped_images(self):
		self.flipped_images = []
		for image in self.walk_images:
			new = pg.transform.flip(image, True, False)
			self.flipped_images.append(new)



	# Tower class calls this when damaging a mob (passing the damage to inflict to the mob with it "tower_damage")
	def handle_health(self, tower_damage):
		if self.health - tower_damage > 0:
			self.health -= tower_damage
		else:
			self.health = 0
		self.health_percentage = self.health / self.max_health
		self.health_images[1] = pg.transform.scale(self.health_images[1], (int(self.health_original_width * self.health_percentage), self.health_original_height))
		if self.health == 0:
			self.alive = False
			self.death_delay = 1


	# Method used to send the mob to the next target while taking into account its next offset
	def follow_target(self, target, dt):

		if self.target_direction == "x":
			self.desired = vec(vec(target + self.offset, self.pos.y) - self.pos)
			self.dist_from_target = abs(self.desired.x - self.offset)

		if self.target_direction == "y":
			self.desired = vec(vec(self.pos.x, target + self.offset - self.height/1.5) - self.pos)
			self.dist_from_target = abs(self.desired.y - self.offset + self.height/1.5)

		dist = self.desired.length()
		
		move_to = self.desired


		if move_to.length() > 0:
			move_to = move_to.normalize()

		if dist <= 1:
			self.path_update()

		if dist <= APPROACH_RADIUS:
			self.vel = move_to * (dist / APPROACH_RADIUS * (self.speed*dt))

		else:
			self.vel = move_to * (self.speed*dt)

		self.pos += self.vel




	# This gets called to change the mobs "turn_count", this is used as a counter to choose the mobs next postional target to walk to. 
	# if its at the end of the list then its at the base currently, so the mob removes a life
	def path_update(self):
		if self.turn_count+1 >= len(self.turn_points):
			pg.sprite.Sprite.kill(self)
			#print("i got you")
			
			self.game.lose_life(1)

		else:
			self.turn_count += 1
			self.calculate_path_distances()
			self.handle_offset()


	# Calculate the mobs next target to walk to depending on its "turn_count"
	def calculate_path_distances(self):
		self.target = self.turn_points[self.turn_count]
		self.target_direction = self.level_directions[self.turn_count]

		# potentially obselete section, not used currently
		"""#self.travelled_dist = 0 # Total travelled by mob
						
								#if self.target_direction == "x":
									#vec_dist = (vec(self.target + self.offset, self.pos.y) - self.pos)
									#self.total_dist = abs(vec_dist[0])
									#dist = (self.desired.length() + self.offset)
						
								#if self.target_direction == "y":
									#vec_dist = (vec(self.pos.x, self.target + self.offset - self.height/1.5) - self.pos)
									#self.total_dist = abs(vec_dist[1])"""


	 #This handles the mobs offset when changing to the next positional target (taking into account the +/- of the current vector and if the next vector is negative), to make sure 
	 #the mob travels equal distances and doesnt alwayscut the corner etc.
	def handle_offset(self):		
		if self.target_direction == "x":
			if self.target < self.pos.x: # if negative vector
				self.x_target = "negative"

				if self.e_or_l == "early":
					self.offset = -(self.original_offset)
					self.e_or_l = "late"
				else:
					self.offset = self.original_offset
					self.e_or_l = "early"
			else:
				self.x_target = "positive"

				if self.e_or_l == "early":
					self.offset = self.original_offset
					self.e_or_l = "late"
				else:
					self.offset = -(self.original_offset)
					self.e_or_l = "early"

		if self.target_direction == "y":
			if self.target < self.pos.y: # if negative vector
				if self.e_or_l == "early":
					self.offset = -(self.original_offset)
					self.e_or_l = "late"
				else:
					self.offset = self.original_offset
					self.e_or_l = "early"
			else:
				if self.e_or_l == "early":
					self.offset = self.original_offset
					self.e_or_l = "late"
				else:
					self.offset = -(self.original_offset)
					self.e_or_l = "early"

	# Determine what image we should be showing (changes after a set amount of time based on the walk speed of mob to animate the walking)
	def animate(self):
		now = time.time()
		if self.x_target == "positive":
			images = self.walk_images
		else:
			images = self.flipped_images

		if now - self.update_animation > 1.5/self.speed:
			self.image_number += 1
			self.image = images[self.image_number % len(images)-1]
			self.update_animation = now


	# Once the handle_health method sets "self.alive = False" run this method containing coin drop and a delay to make the mob stop for 10 frames before dissapearing.
	def death_actions(self):

		if self.death_delay == 1:
			image = self.image.copy()
			image.fill((colours["red"]), special_flags=pg.BLEND_RGB_MIN)
			self.image = image

		self.death_delay += 1

		if self.death_delay == 15:
			for i in range(self.kill_value):
				Coins(self.game, self, 10)
			self.particles = []
			pg.sprite.Sprite.kill(self)
			del self

	def death_particles(self):
		col_list = [colours["red"]]
		x, y = self.pos
		self.particles.append(
			[[x, y], [rand.randint(0, 20) / 10 - 1, rand.randint(0, 40) / 10 - 1], rand.randint(2, 4),
			 col_list[rand.randint(0, len(col_list) - 1)]])

		for particle in self.particles:
			particle[0][0] += particle[1][0]
			particle[0][1] += particle[1][1]
			particle[2] -= 0.1
			particle[1][1] += 0.05
			if particle[2] <= 0:
				self.particles.remove(particle)



	# TOGGLES VISUAL INFORMATION ON THE MOBS TARGET WHEN PRESSING 'i' ingame (dev view)
	def draw_vectors(self, screen):
		# desired point the mob wants to travel to
		pg.draw.line(screen, self.colour, self.pos, (self.pos + self.desired), 5)


	# Main update loop for mob
	def update(self, dt):
		# self.follow_mouse()

		if self.alive:

			self.animate()
			self.acc = self.follow_target(self.target, dt)

			self.rect.center = self.pos
			self.shadow_rect.midtop = self.rect.midbottom + vec(0, -self.shadow_height/1.5)
			self.health_rect.center = self.rect.midtop + vec(0, -5)
		else:
			#self.death_particles()
			self.death_actions()


	# the draw loop
	def draw(self, screen):
		screen.blit(self.image, self.rect)
		screen.blit(self.shadow_surface, self.shadow_rect)
		for i in self.health_images:
			#print(i)
			screen.blit(i, (self.health_rect))
		if not self.alive:
			for particle in self.particles:
				pg.draw.circle(screen, particle[3], [int(particle[0][0]), int(particle[0][1])], int(particle[2]))



class Orc(Mob):
	def __init__(self, game):
		self.name = "Orc"
		self.game = game
		self.type = "ground"
		self.speed = 40 * MOBSPEED_MULTIPLIER
		self.colour = colours["green"]
		self.health = 12 + (self.game.wave_number * 2)
		self.kill_value = int((self.health/10 + 1) + 0.5) # Coins
		super().__init__()

class Scorpion(Mob):
	def __init__(self, game):
		self.name = "Scorpion"
		self.game = game
		self.type = "ground"
		self.speed = 60 * MOBSPEED_MULTIPLIER
		self.colour = colours["red"]
		self.health = 7 + (self.game.wave_number * 2)
		self.kill_value = int((self.health/10 + 1) + 0.5) # Coins
		super().__init__()

class Purple_Hippo(Mob):
	def __init__(self, game):
		self.name = "Purple_Hippo"
		self.game = game
		self.type = "ground"
		self.speed = 45 * MOBSPEED_MULTIPLIER
		self.colour = colours["red"]
		self.health = 16 + (self.game.wave_number * 2)
		self.kill_value = int((self.health/10 + 1) + 0.5) # Coins
		super().__init__()


# Original pygame shape mobs
class Square(Mob):
	def __init__(self, game):
		self.game = game
		self.width = MOBSIZE
		self.height = MOBSIZE
		self.colour = colours["red"]
		self.image = pg.Surface((self.width, self.height))
		self.image.fill(self.colour)
		self.health = 10 + (self.game.wave_number * 2)
		self.kill_value = int((self.health/10 + 1) + 0.5) #Coins
		super().__init__("square")

class Circle(Mob):
	def __init__(self, game):
		self.game = game
		self.width = MOBSIZE
		self.height = MOBSIZE
		self.colour = colours["blue"]
		self.image = pg.Surface((self.width, self.height))
		pg.draw.circle(self.image, self.colour, (self.width//2, self.height//2), self.width//2, 0)
		self.image.set_colorkey(colours["black"])
		self.health = 12 + (self.game.wave_number * 2)
		self.kill_value = int((self.health/10 + 1) + 0.5) # Coins
		super().__init__("circle")

	# potential obslete method of counting how far the mob has travelled since it last turned, then comparing to the initial length needed to get to the target. then using this
	# to track when to turn the mob
	"""def update_travel_dist(self, move_vector):
					if self.target_direction == "x":
						self.travelled_dist += abs(self.vel[0])

					if self.target_direction == "y":
						self.travelled_dist += abs(self.vel[1])

					if self.travelled_dist >= self.total_dist: #and self.game_delay ==0:
						#self.game_delay = 1
						#print(f"i travelled {self.travelled_dist} out of a total of {self.total_dist}")
						self.path_update()"""