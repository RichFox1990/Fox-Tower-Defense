import pygame as pg
import random as rand

from fox_tower_defense.utils.SETTINGS import TILE_SIZE
from fox_tower_defense.utils.SETTINGS import COLOURS, TILE_SIZE
from fox_tower_defense.utils.helper_classes import Vec


# Coin class, drops upon mob death
class Coins(pg.sprite.Sprite):
	def __init__(self, game, entity, spread):

		self.game = game
		self.groups = self.game.coins, self.game.all_sprites
		pg.sprite.Sprite.__init__(self, self.groups)

		self.spread = spread  # Random spread value in pixels the coin can spawn from the entity's center point
		self.entity = entity
		self.images = self.game.images["coin"] # list of images used to animate the coin
		self.image_number = 0
		self.image = self.images[self.image_number]

		self.rect = self.image.get_rect(center = self.entity.rect.center)
		self.width, self.height = self.image.get_size()
		self.prep_shadow()
		self.randomize_pos()
		self.collected = False

		self.update_animation = 0
		self.animate_speed = .025 # in seconds

		self.time_alive = 0
		self.despawn_time = 10

		self.follow_speed = 100
		self.follow_radius = TILE_SIZE*2

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
		self.shadow_surface.fill(COLOURS["magenta"])
		self.shadow_rect = self.shadow_surface.get_rect(midtop = self.rect.midbottom)
		pg.draw.ellipse(self.shadow_surface, COLOURS["black"], (0,0, self.width*.8, self.shadow_height))
		self.shadow_surface.set_colorkey(COLOURS["magenta"])
		self.shadow_surface.set_alpha(50)

	# Method to slightly scatter the coin start position from the entitys center
	def randomize_pos(self):
		randomx, randomy = rand.randrange(-self.spread, self.spread), rand.randrange(-self.spread, self.spread)
		self.rect.center += Vec(randomx, randomy)
		self.original_center = self.rect.center
		self.shadow_rect.midtop = self.rect.midbottom# + Vec(0, -5)

	# this makes the coin follow the mouse if the mouse is within a certain distance from the coin
	def follow_mouse(self, mpos, dt):
		vector = Vec(mpos) - Vec(self.rect.center)
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
