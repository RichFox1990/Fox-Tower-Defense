from towers.tower import Tower
from utils.SETTINGS import FPS, TILE_SIZE, TOWER_RADIUS_MULTIPLIER


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
		self.radius = int((TILE_SIZE//1.5 * (5 + int(self.level*1.5)))*TOWER_RADIUS_MULTIPLIER)
		self.damage = 2.3 + (self.level * 2)
		self.attack_speed = FPS*3 - ((self.level-1) * 5)
		self.attack_cooldown = self.attack_speed*.9
		self.attack_animation_time = 15  # self.attack_speed - self.attack_cooldown
		self.loop_height = 80  # amount of pixels the projectile loops in the air when shot toward target
		self.splash = 55 + (self.level * 5)
