import pygame as pg

pg.init() 
vec = pg.math.Vector2

# BASIC SETTINGS TO TWEAK CERTAIN GAMEPLAY AND OTHER SETTINGS TO HELP WHEN CODING

# Screen and tile info
SCREENWIDTH = 1024
SCREENHEIGHT = 768
FPS = 60
TILESIZE = 32
HUD_IMAGE_SIZE = (30,30)

# Mob wave for the game - dictionary of a nested list of mobs and the number to spawn - Edit and add to your liking
WAVES = {1: [["Orc", 15], ["Scorpion", 0], ["Purple_Hippo", 0]], 2: [["Orc", 10], ["Scorpion", 15], ["Purple_Hippo", 0]], 3: [["Orc", 15], ["Scorpion", 15], ["Purple_Hippo", 10]], 4: [["Orc", 20], ["Scorpion", 25], ["Purple_Hippo", 20]]}

# Mob setting
MOBSIZE = 20
MOBSLIM = 26
MOBWIDE = 30
MOBSPEED_MULTIPLIER = .6
MOB_START_POS = -40
APPROACH_RADIUS = 2 # how close in pixels mob has to get before the speed scales to ensure it doesnt overshoot its target (making sure it turns effectively)

# Tower settings
TOWERLEVELS = 3
TOWER_MULTIPLIER = 2 # size
TOWER_RADIUS_MULTIPLIER = 1.1
TOWERSIZE = (int(30*TOWER_MULTIPLIER), int(60*(TOWER_MULTIPLIER*0.7)))
TOWER_SPACE = (TILESIZE*TOWER_MULTIPLIER - TOWERSIZE[0])
PROJECTILE_SPEED = FPS/2
PARTICLE_ANIMATION_SPEED = 0.05 # in seconds for projectile animation upon hit

COINSIZE_MENU = (40, 40)
COINSIZE = 25

HAMMERSIZE = (80,70) # bottom bar hammer image used to construct towers

WAVETIMER = 60

#PATHWIDTH = 96
#MAX_SPEED = 60
#MAX_FORCE = 0.1



# define some colors (R, G, B)
colours = {"black":(0,0,0), "darkgray":(70,70,70), "gray":(128,128,128), "lightgray":(200,200,200), "white":(255,255,255), "red":(255,0,0),
          "darkred":(128,0,0),"green":(0,255,0),"darkgreen":(0,128,0), "blue":(0,0,255), "navy":(0,0,128), "darkblue":(0,0,128),
          "yellow":(255,255,0), "gold":(255,215,0), "orange":(255,165,0), "lilac":(229,204,255),"lightblue":(135,206,250),"teal":(0,128,128),
          "cyan":(0,255,255), "purple":(150,0,150), "pink":(238,130,238), "brown":(139,69,19), "lightbrown":(222,184,135),"lightgreen":(144,238,144),
          "turquoise":(64,224,208),"beige":(245,245,220),"honeydew":(240,255,240),"lavender":(230,230,250),"crimson":(220,20,60), "magenta": (255,0,255)}