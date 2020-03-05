from __future__ import print_function
import os
import neat
from dask import visualize
import random
from game import simulator
import pickle
import sys

if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    file = sys.argv[1]
    # population = neat.Checkpointer.restore_checkpoint(os.path.join(local_dir, 'neat-checkpoint-34'))
    population = neat.Checkpointer.restore_checkpoint(os.path.join(local_dir, file))
    config = population.config


    all_genomes = list(population.population.values())
    all_genomes = [x for x in all_genomes if x.fitness is not None]
    random.seed()
    random.shuffle(all_genomes)
    # all_genomes.sort(key = lambda x: x.fitness, reverse=True)
    print([x.fitness for x in all_genomes])
    # all_genomes.sort(key=lambda x: x.fitness, reverse=True)

    cur_simulator = simulator()
    print(all_genomes[0:3])
    cur_simulator.create_ai_fighters_from_gennomes(all_genomes[0:3], config)
    # cur_simulator.create_ai_fighters_from_gennomes([all_genomes[0]]*3, config)
    cur_simulator.run_full_simulation(45, display_sim=True)
