from utils.SETTINGS import COLOURS, MOB_SPEED_MULTIPLIER
from mobs.mob import Mob


class Scorpion(Mob):
	def __init__(self, game):
		self.name = "Scorpion"
		self.game = game
		self.type = "ground"
		self.speed = 60 * MOB_SPEED_MULTIPLIER
		self.colour = COLOURS["red"]
		self.health = 7 + (self.game.wave_number * 2)
		self.kill_value = int((self.health/10 + 1) + 0.5) # Coins
		super().__init__()
