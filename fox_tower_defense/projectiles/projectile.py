import time
import pygame as pg
import random as rand

from fox_tower_defense.utils.SETTINGS import PROJECTILE_SPEED, FPS, PARTICLE_ANIMATION_SPEED, COLOURS
from fox_tower_defense.utils.helper_classes import Vec


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
			self.pos = Vec(self.rect.midbottom)
		else:
			self.rect = self.image.get_rect(center = self.tower.image_rect.midtop)
			self.pos = Vec(self.rect.center)
		self.loop_speed = self.tower.loop_height 			# height the projection arcs into the air towards target

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
		self.orig_rect = self.rect.copy()  	# used to reference when moving the projectile in "move" method
		self.target = target
		self.target_pos = target.rect.center# + Vec(0, -5)

		t_pos = Vec(self.target_pos)  # position i want the projectile to hit (midbottom of mob (the floor at mobs
		# feet))
		my_pos = Vec(self.pos)			# want to use the center of projectile to match with the above

		self.t_vec = Vec(t_pos - my_pos)
		self.t_vec_norm = self.t_vec.normalize()

		self.shot_timer = 1 	# start the shot

		if self.firing_type == "direct":
			self.angle = self.t_vec.angle_to(Vec(-1,0))
			self.image = pg.transform.rotate(self.image, self.angle)
			self.rect = self.image.get_rect(center = self.rect.center)

	def move(self, dt):
		stage_of_shot = self.shot_timer/self.shot_total			# gets a value between 0 and 1 representing how far through the shot we are (i.e 0.5 would equal 50%)

		if self.firing_type == "splash":

			if not self.hit:
				self.pos = self.orig_rect.midbottom + Vec(self.t_vec * stage_of_shot)

				if stage_of_shot <= 0.5:
					loop = -(self.loop_speed*2) * stage_of_shot
				else:
					stage_of_shot -= .5
					loop = (self.loop_speed*2 * stage_of_shot) - self.loop_speed

				self.pos += Vec(0, loop)
				
				self.rect.midbottom = self.pos

			else:
				self.pos = self.target_pos
				self.rect.center = self.pos

		elif self.firing_type == "direct":

			try:
				self.target_pos = self.target.rect.center
				self.desired = Vec(Vec(self.target.rect.center) - self.pos)

				full_dist = Vec(Vec(self.target.rect.center) - Vec(self.orig_rect.center))
				dist = full_dist.length()

			except:
				print("mob died in travel")
				
			move_to = self.desired

			if move_to.length() > 0:
				move_to.normalize_ip()			

			self.vel = (move_to * (dist*dt*(FPS/self.shot_total)))

			self.pos += self.vel#self.orig_rect.midbottom + Vec(self.t_vec * stage_of_shot)
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
				dist = Vec(self.target_pos) - Vec(mob.rect.center)
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
		if self.tower.name == "Fire":
			col_list = [COLOURS["red"], COLOURS["orange"], COLOURS["yellow"]]
			for iteration in range(amount):
				mob_pos = Vec(self.pos)
				list_offset = [-offset, offset]
				offset = list_offset[rand.randrange(2)]
				particle_pos = Vec(1,0).rotate(rand.randrange(360))
				particle_pos.scale_to_length(offset)
				particle_pos += mob_pos
				self.tracers.append([particle_pos, Vec(rand.randint(0, 20) / 10 - 1, rand.randint(0, 20) / 10), rand.randint(1, 2), col_list[rand.randint(0, len(col_list)-1)]])
	 
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
		# if self.target != False:
			# pass
			# pg.draw.rect(screen, COLOURS["blue"], (*self.crest, 10 ,10))
			# pg.draw.rect(screen, COLOURS["red"], (*self.target_pos, 10 ,10))
