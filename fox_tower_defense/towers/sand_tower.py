from fox_tower_defense.towers.tower import Tower
from fox_tower_defense.utils.SETTINGS import FPS, TILE_SIZE, TOWER_RADIUS_MULTIPLIER


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
		self.radius = int((TILE_SIZE//1.5 * (6 + int(self.level*1.5)))*TOWER_RADIUS_MULTIPLIER)
		self.damage = 5 + (self.level * 2)
		self.attack_speed = FPS*3.5 - ((self.level-1) * 3)
		self.attack_cooldown = self.attack_speed
		self.attack_animation_time = 15
		self.loop_height = 80  # amount of pixels the projectile loops in the air when shot toward target
		self.splash = 55 + (self.level * 5)

