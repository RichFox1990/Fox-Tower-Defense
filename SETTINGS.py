import pygame as pg
import random

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
#WAVES = {1: [["Orc", 0], ["Scorpion", 10], ["Purple_Hippo", 0]], 2: [["Orc", 0], ["Scorpion", 1], ["Purple_Hippo", 0]]}
number_of_mobs = 15
NUMBER_OF_WAVES = 30
WAVES = {}

number_of_orcs = 0
number_of_scopions = 0
number_of_hippos = 0

MOB_CHANCE = {
        'Orc': 30,
        'Scorpion': 20,
        'Purple_Hippo': 10
    }

def random_choice_index(chances):
    random_chance = random.randint(1, sum(chances))

    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w

        if random_chance <= running_sum:
            return choice
        choice += 1

def random_choice_from_dict(choice_dict):
    choices = list(choice_dict.keys())
    chances = list(choice_dict.values())

    return choices[random_choice_index(chances)]

for j in range(1, NUMBER_OF_WAVES+1):
    number_of_orcs = 0
    number_of_scopions = 0
    number_of_hippos = 0

    for i in range(number_of_mobs):
        monster_choice = random_choice_from_dict(MOB_CHANCE)

        if monster_choice == 'Orc':
            number_of_orcs += 1
        elif monster_choice == 'Scorpion':
            number_of_scopions += 1
        elif monster_choice == 'Purple_Hippo':
            number_of_hippos += 1

    WAVES[j] = [['Orc', number_of_orcs], ['Scorpion', number_of_scopions], ['Purple_Hippo', number_of_hippos]]

    number_of_mobs += random.randint(5, 10)

STARTING_MONEY = 160

# Mob setting
MOBSIZE = 20
MOBSLIM = 26
MOBWIDE = 30
MOBSPEED_MULTIPLIER = .8
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

TOWER_COSTS = {"Stone": [40, 50, 75], "Fire": [35, 60, 75], "Sand": [30, 55, 75], "Archer": [35, 60, 80]}

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