from fox_tower_defense.towers.tower import Tower
from fox_tower_defense.utils.SETTINGS import FPS, TILE_SIZE, TOWER_RADIUS_MULTIPLIER


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
		self.radius = int((TILE_SIZE//1.5 * (6 + int(self.level*1.5)))*TOWER_RADIUS_MULTIPLIER)
		self.damage = 0 + (self.level * 2)
		self.attack_speed = FPS*1 - ((self.level-1) * 3)
		self.attack_cooldown = self.attack_speed
		self.attack_animation_time = self.attack_speed*0.2
		self.loop_height = 0  # amount of pixels the projectile loops in the air when shot toward target
		self.splash = 0
