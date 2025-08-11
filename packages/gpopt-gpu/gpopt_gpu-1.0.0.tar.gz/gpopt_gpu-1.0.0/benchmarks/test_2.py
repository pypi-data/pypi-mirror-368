import gpopt_gpu
import numpy as np

# configure the GP run
config = gpopt.GpoptConfig()
config.population_size = 150
config.generations = 100
config.num_features = 2
config.num_samples = 6
config.function_set = [gpopt.Op.ADD, gpopt.Op.SUB, gpopt.Op.MUL]

# create the runner with the configuration
runner = gpopt.GpoptRunner(config)

# define the problem data; y = x0 * x1 - (x0 + x1)

X = [
    1.0, 1.0,
    2.0, 3.0,
    3.0, 2.0,
    4.0, 5.0,
    5.0, 4.0,
    6.0, 6.0
]

y = [
    1*1 - (1+1), # -1
    2*3 - (2+3), # 1
    3*2 - (3+2), # 1
    4*5 - (4+5), # 11
    5*4 - (5+4), # 11
    6*6 - (6+6), # 24
]

# initialize and run the evolution
runner.initialize(X, y)
runner.run()

# get the best individual
best_individual = runner.get_best_individual()

print(f"Final Fitness: {best_individual.fitness}")
print(f"Best Program Found: {gpopt.format_program(best_individual)}")