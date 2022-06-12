from fox_tower_defense.utils.SETTINGS import COLOURS, MOB_SPEED_MULTIPLIER
from fox_tower_defense.mobs.mob import Mob


class PurpleHippo(Mob):
    def __init__(self, game):
        self.name = "Purple_Hippo"
        self.type = "ground"
        self.speed = 45 * MOB_SPEED_MULTIPLIER
        self.colour = COLOURS["red"]
        self.health = 16 + (game.wave_number * 2)
        self.kill_value = int((self.health/10 + 1) + 0.5)  # Coins
        super().__init__(game)
