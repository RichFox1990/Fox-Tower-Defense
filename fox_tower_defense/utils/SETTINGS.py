# BASIC SETTINGS TO TWEAK CERTAIN GAME PLAY AND OTHER SETTINGS TO HELP WHEN CODING

# Screen and tile info
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
TILE_SIZE = 32
HUD_IMAGE_SIZE = (30,30)

WAVE_1_MOB_COUNT = 15
NUMBER_OF_WAVES = 30

STARTING_MONEY = 160

# Mob setting
MOB_SIZE = 20
MOB_SLIM = 26
MOB_WIDE = 30
MOB_SPEED_MULTIPLIER = .8
MOB_START_POS = -40
APPROACH_RADIUS = 2  # how close in pixels mob has to get before the speed scales to ensure it doesnt overshoot its target (making sure it turns effectively)

# Tower settings
TOWER_LEVELS = 3
TOWER_MULTIPLIER = 2 # size
TOWER_RADIUS_MULTIPLIER = 1.1
TOWER_SIZE = (int(30*TOWER_MULTIPLIER), int(60*(TOWER_MULTIPLIER*0.7)))
TOWER_SPACE = (TILE_SIZE*TOWER_MULTIPLIER - TOWER_SIZE[0])
PROJECTILE_SPEED = FPS/2
PARTICLE_ANIMATION_SPEED = 0.05 # in seconds for projectile animation upon hit

TOWER_COSTS = {"Stone": [40, 50, 75], "Fire": [35, 60, 75], "Sand": [30, 55, 75], "Archer": [35, 60, 80]}

COIN_SIZE_MENU = (40, 40)
COIN_SIZE = 25

HAMMER_SIZE = (80,70) # bottom bar hammer image used to construct towers

WAVE_TIMER = 60

# define some colors (R, G, B)
COLOURS = {"black":(0,0,0), "darkgray":(70,70,70), "gray":(128,128,128), "lightgray":(200,200,200), "white":(255,255,255), "red":(255,0,0),
          "darkred":(128,0,0),"green":(0,255,0),"darkgreen":(0,128,0), "blue":(0,0,255), "navy":(0,0,128), "darkblue":(0,0,128),
          "yellow":(255,255,0), "gold":(255,215,0), "orange":(255,165,0), "lilac":(229,204,255),"lightblue":(135,206,250),"teal":(0,128,128),
          "cyan":(0,255,255), "purple":(150,0,150), "pink":(238,130,238), "brown":(139,69,19), "lightbrown":(222,184,135),"lightgreen":(144,238,144),
          "turquoise":(64,224,208),"beige":(245,245,220),"honeydew":(240,255,240),"lavender":(230,230,250),"crimson":(220,20,60), "magenta": (255,0,255)}
