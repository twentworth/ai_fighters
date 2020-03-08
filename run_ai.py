from __future__ import print_function
import os
import neat
from dask import visualize
import random
import game
# game.FRAMERATE = 30
from game import simulator
import pickle
import sys
from ai import challenger

if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    todo = sys.argv[1]
    file = sys.argv[2]
    # population = neat.Checkpointer.restore_checkpoint(os.path.join(local_dir, 'neat-checkpoint-34'))
    # population = neat.Checkpointer.restore_checkpoint(os.path.join(local_dir, 'neat-checkpoint-'+file))
    with open(os.path.join(local_dir, 'challengers_'+file), 'rb') as f:
        D = pickle.load(f)

    challengers = D['challengers']
    all_genomes = D['genomes']
    config = challengers[-1].config


    # all_genomes = [x for x in all_genomes if x.fitness is not None and x.fitness > 0]
    random.seed()
    random.shuffle(all_genomes)
    all_genomes.sort(key = lambda x: x.fitness, reverse=True)
    if todo == 'run':
        print([x.fitness for x in all_genomes])
        all_genomes.sort(key=lambda x: x.fitness, reverse=True)
        print(all_genomes[0].fitness)
        all_genomes[0].fitness = 0
        k = 0
        for c in challengers:
            cur_simulator = simulator()

            cur_simulator.create_ai_fighters_from_gennomes([all_genomes[k]], config, challenger=c)
            # cur_simulator.create_ai_fighters_from_gennomes([all_genomes[0]]*3, config)
            didwin = cur_simulator.run_full_simulation(c.sim_time, display_sim=True)
            if didwin: all_genomes[k].fitness = all_genomes[k].fitness + 100
            print([x.damage_dealt for x in cur_simulator.all_fighters_dead_and_alive], all_genomes[0].fitness)
    else:
        import visualize
        visualize.draw_net(config, all_genomes[0])