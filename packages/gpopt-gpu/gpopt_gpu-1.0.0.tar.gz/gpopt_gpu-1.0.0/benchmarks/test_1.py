import gpopt_gpu
import numpy as np

# configure the GP run
config = gpopt.GpoptConfig()
config.population_size = 100
config.generations = 50
config.num_features = 2
config.num_samples = 4
config.function_set = [gpopt.Op.ADD, gpopt.Op.SUB, gpopt.Op.MUL]

# create the runner with the configuration
runner = gpopt.GpoptRunner(config)

# define the problem data (y = x0 + x1)
X = [1.0, 1.0, 2.0, 2.0, 3.0, 3.0, 4.0, 4.0]
y = [2.0, 4.0, 6.0, 8.0]

# initialize and run the evolution
runner.initialize(X, y)
runner.run()

# get the best individual
best_individual = runner.get_best_individual()

print(f"Final Fitness: {best_individual.fitness}")
print(f"Best Program Found: {gpopt.format_program(best_individual)}")