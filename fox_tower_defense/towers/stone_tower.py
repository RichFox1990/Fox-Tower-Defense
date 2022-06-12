from fox_tower_defense.towers.tower import Tower
from fox_tower_defense.utils.SETTINGS import FPS, TILE_SIZE, TOWER_RADIUS_MULTIPLIER


class Stone(Tower):
    def __init__(self, game, pos):
        self.name = "Stone"
        self.pos = pos
        self.level = 1
        self.cost = [40, 50, 75]
        self.firing_type = "splash"
        self.platform = True
        self.update_stats()
        super().__init__(game)

    def update_stats(self):
        self.radius = int(
            (TILE_SIZE//1.5 * (4 + int(self.level*1.5)))*TOWER_RADIUS_MULTIPLIER)
        self.damage = 3 + (self.level * 2)
        self.attack_speed = FPS*2.5 - ((self.level-1) * 4)
        self.attack_cooldown = self.attack_speed*.9
        self.attack_animation_time = 20  # self.attack_speed - self.attack_cooldown
        # amount of pixels the projectile loops in the air when shot toward target
        self.loop_height = 50
        self.splash = 45 + (self.level * 5)
