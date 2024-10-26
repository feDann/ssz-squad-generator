import argparse
import random
import math
import copy
from enum import Enum
from typing import Dict, List, Tuple
from collections import defaultdict

#### Configs
MAX_RETRIES = 1000


#### Strategies

class GenerationStrategies(Enum):
    RANDOM = "random" 
    RANDOM_RANDOM = "rrandom"
    MAX_ATTACK = "max_attack"
    BALANCED = "balanced"

GENERATION_STRATEGIES = [strategy.value for strategy in GenerationStrategies]

##### Arguments  

parser = argparse.ArgumentParser("random-db-generator", description="Genetate a random squad for sparking zero PD battles. The program can generate the squad based on different strategies")

parser.add_argument("--characters-file", "-c", type=str, required=True, help="The CSV file storing the character names and the cost for each character")
parser.add_argument("--max-cost", "-m", type=int, required=False, default=15, help="The max cost for each squad")
parser.add_argument("--squad-size", "-n", type=int, required=False, default=5, help="The max number of character for each squad")
parser.add_argument("--num-squads", "-s", type=int, required=False, default=1, help="The number of squads to generate")
parser.add_argument("--strategy", "-t", type=str, choices=GENERATION_STRATEGIES , required=False, default="random", help="The strategy used to generate the squad")

##### Generation strategies

def random_generator(cost_characters_map: Dict[int, List[str]], cost_entries: List[int], max_cost: int, max_squad_size: int, squad_size: int, squad_cost: int) -> Tuple[int, str]:
    for _ in range(MAX_RETRIES):    
        cost_choice = min(random.choice(cost_entries), max_cost - squad_cost)
        if squad_size == max_squad_size - 1:
            cost_choice = max_cost - squad_cost
        
        available_choices = len(cost_characters_map[cost_choice])

        if available_choices == 0:
            continue
        
        return cost_choice, cost_characters_map[cost_choice].pop(random.randint(0, available_choices - 1))

    print(f"[WARN]: Max number of retries reached consider tweaking the algorithm, current cost choice {cost_choice}")
    exit(0)


def max_attack_generator(cost_characters_map: Dict[int, List[str]], cost_entries: List[int], max_cost: int, max_squad_size: int, squad_size: int, squad_cost: int)  -> Tuple[int, str]:
    cost_choice = min(max(cost_entries), max_cost - squad_cost)

    return default_strategy(cost_characters_map, cost_choice)


def balanced_generator(cost_characters_map: Dict[int, List[str]], cost_entries: List[int], max_cost: int, max_squad_size: int, squad_size: int, squad_cost: int)  -> Tuple[int, str]:
    average_cost = math.ceil((max_cost - squad_cost) / max_squad_size)
    closest_cost = min(cost_entries, key= lambda x: abs(x-average_cost))
    
    cost_choice = min(closest_cost, max_cost - squad_cost) if squad_size != max_squad_size - 1 else max_cost - squad_cost
    
    return default_strategy(cost_characters_map, cost_choice)

def default_strategy(cost_characters_map: Dict[int, List[str]], cost_choice: int) -> Tuple[int, str]:
    available_choices = len(cost_characters_map[cost_choice])

    if available_choices == 0:
        print(f"[WARN]: No available choices for chosen strategy, cost_choice {cost_choice}")

        exit(0)
    
    return cost_choice, cost_characters_map[cost_choice].pop(random.randint(0, available_choices - 1))

def rr_generator(cost_characters_map: Dict[int, List[str]], cost_entries: List[int], max_cost: int, max_squad_size: int, squad_size: int, squad_cost: int)  -> Tuple[int, str]:
    available_strategies = [strat for strat in GENERATION_STRATEGIES if strat != GenerationStrategies.RANDOM_RANDOM.value]
    chosen_strategy = GenerationStrategies(random.choice(available_strategies))

    return ROUTING_STRATEGY_TABLE[chosen_strategy](cost_characters_map, cost_entries, max_cost, max_squad_size, squad_size, squad_cost)



ROUTING_STRATEGY_TABLE = {
    GenerationStrategies.RANDOM: random_generator,
    GenerationStrategies.RANDOM_RANDOM: rr_generator,
    GenerationStrategies.MAX_ATTACK: max_attack_generator,
    GenerationStrategies.BALANCED: balanced_generator
}


####
    
def load_characters(characters_file: str) -> Dict[int, List[str]]:
    cost_characters_map = defaultdict(list)

    with open(characters_file, "r") as f:
        for line in f.readlines()[1:]: # skip csv header
            name, cost = line.split(",") 
            cost_characters_map[int(cost)].append(name)

    return cost_characters_map

def generate_squad(cost_characters_map: Dict[int, List[str]], strategy: GenerationStrategies, max_cost: int, max_squad_size: int) -> List[str]:
    squad: List[str] = list()
    squad_cost: int = 0

    cost_entries = list(cost_characters_map.keys())

    while squad_cost != max_cost:
        cost, character = ROUTING_STRATEGY_TABLE[strategy](cost_characters_map, cost_entries, max_cost, max_squad_size, len(squad), squad_cost)

        squad.append((character, cost))
        squad_cost += cost
    
    return squad_cost, squad
    

if __name__ == '__main__':

    args = parser.parse_args()
    cost_characters_map = load_characters(args.characters_file)
    strategy = GenerationStrategies(args.strategy)

    for i in range(args.num_squads):
        print(f"[INFO]: Generating squad {i + 1} ...")

        squad_cost, squad = generate_squad(copy.deepcopy(cost_characters_map), strategy, args.max_cost, args.squad_size)
        print(f"[INFO]: Squad generated: {squad} {squad_cost}")