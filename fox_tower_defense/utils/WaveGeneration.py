from utils.SETTINGS import *
import random as rand


def create_all_waves():
    wave_dict = {}

    mobs_in_wave = WAVE_1_MOB_COUNT

    mob_chance = {
        'Orc': 30,
        'Scorpion': 20,
        'Purple_Hippo': 10
    }

    for j in range(1, NUMBER_OF_WAVES + 1):
        number_of_orcs = 0
        number_of_scorpions = 0
        number_of_hippos = 0

        for i in range(mobs_in_wave):
            monster_choice = random_choice_from_dict(mob_chance)

            if monster_choice == 'Orc':
                number_of_orcs += 1
            elif monster_choice == 'Scorpion':
                number_of_scorpions += 1
            elif monster_choice == 'Purple_Hippo':
                number_of_hippos += 1

        wave_dict[j] = [['Orc', number_of_orcs], ['Scorpion', number_of_scorpions], ['Purple_Hippo', number_of_hippos]]

        mobs_in_wave += rand.randint(3, 8)

    return wave_dict


def random_choice_index(chances):
    random_chance = rand.randint(1, sum(chances))

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
