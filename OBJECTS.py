import random as rand
import time

from SETTINGS import *


class Projectile(pg.sprite.Sprite):
	def __init__(self, game, tower):
		self.game = game
		self.groups = self.game.projectiles
		pg.sprite.Sprite.__init__(self, self.groups)
		self.tower = tower

		self.shot = False
		self.firing_type = self.tower.firing_type
		if self.firing_type == "splash":
			self.shot_total = PROJECTILE_SPEED		# Time in seconds it takes for the shot to land
		elif self.firing_type == "direct":
			self.shot_total = PROJECTILE_SPEED/2
		self.shot_timer = 0
		self.tracers = []

		self.images = self.tower.particle_images
		self.image_number = 0
		self.image = self.images[self.image_number]
		if self.tower.platform:
			self.rect = self.image.get_rect(midbottom = self.tower.b_rect.midbottom)
			self.pos = vec(self.rect.midbottom)
		else:
			self.rect = self.image.get_rect(center = self.tower.image_rect.midtop)
			self.pos = vec(self.rect.center)
		self.loop_speed = self.tower.loop_height 			# height the projection arcs into the air towards target
		#self.vel = vec(0, -self.loop_speed)

		self.target = False    		# target given from tower when tower shoot animation completes
		self.target_rect = False 	# as above
		self.hit = False 			# set to true to enable animation when shot hits the target
		self.start_particles = False
		self.update_hit = time.time()


	def set_rect(self):
		if self.tower.platform:
			self.pos = self.tower.b_rect.midbottom
			self.rect.midbottom = self.pos


	def set_target(self, target):
		self.orig_rect = self.rect.copy()  		# used to reference when moving the projectile in "move" method
		self.target = target
		self.target_pos = target.rect.center# + vec(0, -5)

		t_pos = vec(self.target_pos)		# position i want the projectile to hit (midbottom of mob (the floor at mobs feet))
		my_pos = vec(self.pos)					# want to use the center of projectile to match with the above

		self.t_vec = vec(t_pos - my_pos)
		self.t_vec_norm = self.t_vec.normalize()

		self.shot_timer = 1 	# start the shot

		if self.firing_type == "direct":
			self.angle = self.t_vec.angle_to(vec(-1,0))
			self.image = pg.transform.rotate(self.image, self.angle)
			self.rect = self.image.get_rect(center = self.rect.center)


	def move(self, dt):

		stage_of_shot = self.shot_timer/self.shot_total			# gets a value between 0 and 1 representing how far through the shot we are (i.e 0.5 would equal 50%)

		if self.firing_type == "splash":

			if not self.hit:
				self.pos = self.orig_rect.midbottom + vec(self.t_vec * stage_of_shot)

				if stage_of_shot <= 0.5:
					loop = -(self.loop_speed*2) * stage_of_shot
				else:
					stage_of_shot -= .5
					loop = (self.loop_speed*2 * stage_of_shot) - self.loop_speed

				self.pos += vec(0, loop)
				
				self.rect.midbottom = self.pos

			else:
				self.pos = self.target_pos
				self.rect.center = self.pos

		elif self.firing_type == "direct":

			try:
				self.target_pos = self.target.rect.center
				self.desired = vec(vec(self.target.rect.center) - self.pos)

				full_dist = vec(vec(self.target.rect.center) - vec(self.orig_rect.center))
				dist = full_dist.length()

			except:
				print("mob died in travel")
				
			move_to = self.desired

			if move_to.length() > 0:
				move_to.normalize_ip()			

			# if dist <= APPROACH_RADIUS:
			# 	self.vel = move_to * (dist / APPROACH_RADIUS * (dist*dt))

			# else:
			self.vel = (move_to * (dist*dt*(FPS/self.shot_total)))

			self.pos += self.vel#self.orig_rect.midbottom + vec(self.t_vec * stage_of_shot)
			self.rect.center = self.pos


	def handle_timer(self, dt):

		if self.shot_timer > 0:
			self.shot_timer += FPS*dt


		if self.shot_timer >= self.shot_total:
			self.hit = True
			self.shot_timer = 0
			self.attack()
			self.hit = True


	def attack(self):
		if self.firing_type == "splash":
			for mob in self.game.mobs:
				dist = vec(self.target_pos) - vec(mob.rect.center)
				dist = abs(dist.length())
				if dist <= self.tower.splash:
					if dist > 0:
						ratio = 1 - abs(dist/self.tower.splash)
					else:
						ratio = 1
			
					mob.handle_health(self.tower.damage*ratio)
		else:
			self.target.handle_health(self.tower.damage)


	def animate_hit(self):
		if self.firing_type == "splash":
			now = time.time()
			if now - self.update_hit > PARTICLE_ANIMATION_SPEED:
				if self.image_number != len(self.images):
					self.image_number += 1
					self.image = self.images[self.image_number % len(self.images)-1] 
					self.rect = self.image.get_rect(center = self.target_pos)
					self.update_hit = now

				else:
					pg.sprite.Sprite.kill(self)
					del self
		else:
			pg.sprite.Sprite.kill(self)
			del self


	def particles(self, amount, offset=0):
		if self.tower.name == "fire":
			col_list = [colours["red"], colours["orange"], colours["yellow"]]
			#x, y = self.pos
			for iteration in range(amount):
				mob_pos = vec(self.pos)
				list_offset = [-offset, offset]
				offset = list_offset[rand.randrange(2)]
				particle_pos = vec(1,0).rotate(rand.randrange(360))
				particle_pos.scale_to_length(offset)
				particle_pos += mob_pos
				self.tracers.append([particle_pos, vec(rand.randint(0, 20) / 10 - 1, rand.randint(0, 20) / 10), rand.randint(1, 2), col_list[rand.randint(0, len(col_list)-1)]])
	 
			for particle in self.tracers:
				particle[0] += particle[1]
				particle[2] -= 0.1
				particle[1][1] += 0.05
				if particle[2] <= 0:
					self.tracers.remove(particle)


	def update(self, dt):
		if not self.shot and not self.hit:
			self.set_rect()				

		if self.shot:
			self.move(dt)
			self.handle_timer(dt)
			self.particles(1)

		if self.hit:
			self.particles(5, self.tower.splash//2)
			self.animate_hit()

	def draw(self, screen):
		if self.shot:
			screen.blit(self.image, self.rect)
			for particle in self.tracers:
				pg.draw.circle(screen, particle[3], [int(particle[0][0]), int(particle[0][1])], int(particle[2]))

		if self.target != False:
			pass
			#pg.draw.rect(screen, colours["blue"], (*self.crest, 10 ,10))
			#pg.draw.rect(screen, colours["red"], (*self.target_pos, 10 ,10))



# Coin class, drops upon mob death
class Coins(pg.sprite.Sprite):
	def __init__(self, game, mob):

		self.game = game
		self.groups = self.game.coins, self.game.all_sprites
		pg.sprite.Sprite.__init__(self, self.groups)

		self.mob = mob
		self.images = self.game.images["coin"] # list of images used to animate the coin
		self.image_number = 0
		self.image = self.images[self.image_number]

		self.rect = self.image.get_rect(center = self.mob.rect.center)
		self.width, self.height = self.image.get_size()
		self.prep_shadow()
		self.randomize_pos()
		self.collected = False

		self.update_animation = 0
		self.animate_speed = .025 # in seconds

		self.time_alive = 0
		self.despawn_time = 10

		self.follow_speed = 100
		self.follow_radius = TILESIZE*2

		self.delay_loop = 0
		self.despawning = False
		self.flash = False
		self.last_flash = False


	# if determined amount of time has passed, move to the next image to animate the coin
	def animate(self, dt):
		self.update_animation += dt
		if self.update_animation > self.animate_speed:
			self.image_number += 1
			self.image = self.images[self.image_number % len(self.images)-1]
			self.update_animation = 0
			self.rect = self.image.get_rect(center= self.rect.center)

		self.time_alive += dt
		if self.time_alive > self.despawn_time/2: # if the coin has been alive more than 5 seconds
			#print("coins alive for over 5 secs")
			if not self.despawning:
				self.flash = True
				self.despawning = True
				self.last_flash = 0
			elif self.despawning and self.last_flash >= 0.2:
				self.flash = not self.flash
				self.last_flash = 0
			elif self.time_alive >10:
				self.collected = True
			self.last_flash += dt


	# Prep our surface which will show a "shadow" under the coin
	def prep_shadow(self):
		self.shadow_height = int(self.height/2.1)/1.5
		self.shadow_surface = pg.Surface((self.width*.8, self.shadow_height))
		self.shadow_surface.fill(colours["magenta"])
		self.shadow_rect = self.shadow_surface.get_rect(midtop = self.rect.midbottom)
		pg.draw.ellipse(self.shadow_surface, colours["black"], (0,0, self.width*.8, self.shadow_height))
		self.shadow_surface.set_colorkey(colours["magenta"])
		self.shadow_surface.set_alpha(50)


	# Method to slightly scatter the coin start position from the mobs center
	def randomize_pos(self):
		randomx, randomy = rand.randrange(-10, 10), rand.randrange(-10, 10)
		self.rect.center += vec(randomx, randomy)
		self.original_center = self.rect.center
		self.shadow_rect.midtop = self.rect.midbottom# + vec(0, -5)


	# this makes the coin follow the mouse if the mouse is within a certain distance from the coin
	def follow_mouse(self, mpos, dt):
		vector = vec(mpos) - vec(self.rect.center)
		distance = vector.length()
		if distance <= self.follow_radius:
			if distance > 0:
				vector.normalize_ip()
				vector.scale_to_length(self.follow_speed*dt)
			self.rect.center += vector


	# Main update loop
	def update(self, mpos, dt):	
		if self.rect.collidepoint(mpos):
			self.game.money += 1
			self.collected = True
		else:
			#animate
			pass
		self.animate(dt)

		self.follow_mouse(mpos, dt)
		self.shadow_rect.midtop = self.rect.midbottom

		if self.collected:
			pg.sprite.Sprite.kill(self)
			del self

	# Draw loop
	def draw(self, screen):
		if not self.flash:
			screen.blit(self.image, self.rect)
		screen.blit(self.shadow_surface, self.shadow_rect)

