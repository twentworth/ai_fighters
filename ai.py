from __future__ import print_function
import os
import neat
from dask import visualize
import random
from game import simulator
import pickle
import gzip


def eval_genomes(genomes, config):
    cur_simulator = simulator()

    cur_simulator.create_ai_fighters_from_gennomes(genomes, config)

    cur_simulator.run_full_simulation(10)



def population_run(self, fitness_function, num_genomes_per_run, n=None):
    """
    Runs NEAT's genetic algorithm for at most n generations.  If n
    is None, run until solution is found or extinction occurs.

    The user-provided fitness_function must take only two arguments:
        1. The population as a list of (genome id, genome) tuples.
        2. The current configuration object.

    The return value of the fitness function is ignored, but it must assign
    a Python float to the `fitness` member of each genome.

    The fitness function is free to maintain external state, perform
    evaluations in parallel, etc.

    It is assumed that fitness_function does not modify the list of genomes,
    the genomes themselves (apart from updating the fitness member),
    or the configuration object.
    """

    if self.config.no_fitness_termination and (n is None):
        raise RuntimeError("Cannot have no generational limit with no fitness termination")

    k = 0
    while n is None or k < n:
        k += 1

        self.reporters.start_generation(self.generation)

        # Evaluate all genomes using the user-provided function.
        all_genomes = list(self.population.values())
        random.shuffle(all_genomes)

        # assert len(all_genomes) % num_genomes_per_run == 0
        for i in range(0, len(all_genomes), num_genomes_per_run):
            cur_genomes = all_genomes[i:i+num_genomes_per_run]
            fitness_function(cur_genomes, self.config)
            assert all(x.fitness is not None for x in all_genomes[i:i+num_genomes_per_run])
        if not len(all_genomes) % num_genomes_per_run == 0:
            cur_genomes = all_genomes[-num_genomes_per_run:]
            fitness_function(cur_genomes, self.config)
            assert all(x.fitness is not None for x in all_genomes[i:i + num_genomes_per_run])
        fitness_scores = [x.fitness for x in all_genomes]
        print('fit range:: ',round(min(fitness_scores),3), '-',round(max(fitness_scores),3))
        # Gather and report statistics.
        best = None
        for g in self.population.values():
            if best is None or g.fitness > best.fitness:
                best = g
        self.reporters.post_evaluate(self.config, self.population, self.species, best)

        # Track the best genome ever seen.
        if self.best_genome is None or best.fitness > self.best_genome.fitness:
            self.best_genome = best

        if not self.config.no_fitness_termination:
            # End if the fitness threshold is reached.
            fv = self.fitness_criterion(g.fitness for g in self.population.values())
            if fv >= self.config.fitness_threshold:
                self.reporters.found_solution(self.config, self.generation, best)
                break

        # Create the next generation from the current generation.
        self.population = self.reproduction.reproduce(self.config, self.species,
                                                      self.config.pop_size, self.generation)

        # Check for complete extinction.
        if not self.species.species:
            self.reporters.complete_extinction()

            # If requested by the user, create a completely new population,
            # otherwise raise an exception.
            if self.config.reset_on_extinction:
                self.population = self.reproduction.create_new(self.config.genome_type,
                                                               self.config.genome_config,
                                                               self.config.pop_size)
            else:
                raise CompleteExtinctionException()

        # Divide the new population into species.
        self.species.speciate(self.config, self.population, self.generation)

        self.reporters.end_generation(self.config, self.population, self.species)

        self.generation += 1

    if self.config.no_fitness_termination:
        self.reporters.found_solution(self.config, self.generation, self.best_genome)

    return self

def run(config_file, load_p = None, n=30):
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    if load_p is not None:
        p = load_p
    else:
        p = neat.Population(config)
    # p.run = population_run

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))

    # Run for up to 300 generations.
    population = population_run(p, eval_genomes, 3, n)


    return population




if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat_config.ini')
    # population = neat.Checkpointer.restore_checkpoint(os.path.join(local_dir, 'neat-checkpoint-59'))
    population = run(config_path, load_p= None, n=400)
    config = population.config


    print("Saving output to out_file")

    with gzip.open('out_file', 'w', compresslevel=5) as f:
        data = population
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    all_genomes = list(population.values())
    all_genomes.sort(key=lambda x: x.fitness, reverse=True)

    cur_simulator = simulator()
    cur_simulator.create_ai_fighters_from_gennomes(all_genomes[:3], config)
    cur_simulator.run_full_simulation(15, display_sim=True)


