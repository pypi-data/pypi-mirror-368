import time
import numpy as np
import random
import operator
import gpopt_gpu

# target function is f(x0, x1) = x0 * x1 - x0 - x1
def target_func(x):
    return x[0] * x[1] - x[0] - x[1]

# 100 sample dataset with 2 features
np.random.seed(0)
X = np.random.rand(100, 2).astype(np.float32)
y = np.array([target_func(row) for row in X], dtype=np.float32)

X_flat = X.flatten().tolist()
y_list = y.tolist()

# Python naive GP
OPS = ['ADD', 'SUB', 'MUL']
VAR = ['VAR0', 'VAR1']

def eval_program(program, sample):
    """Evaluate a simple prefix program on a sample"""
    stack = []
    for token in program:
        if token == 'ADD':
            b = stack.pop()
            a = stack.pop()
            stack.append(a + b)
        elif token == 'SUB':
            b = stack.pop()
            a = stack.pop()
            stack.append(a - b)
        elif token == 'MUL':
            b = stack.pop()
            a = stack.pop()
            stack.append(a * b)
        elif token.startswith('VAR'):
            idx = int(token[3])
            stack.append(sample[idx])
        else:
            raise RuntimeError("Unknown token")
    return stack[0]

def random_program(length=15):
    """Generate a random prefix program of fixed length"""
    program = []
    for _ in range(length):
        if random.random() < 0.4:
            program.append(random.choice(VAR))
        else:
            program.append(random.choice(OPS))
    return program

def fitness(program):
    error = 0.0
    for i in range(len(X)):
        try:
            val = eval_program(program, X[i])
            error += (val - y[i]) ** 2
        except:
            error += 1e6
    return error / len(X)

def mutate(program):
    idx = random.randint(0, len(program)-1)
    if program[idx].startswith('VAR'):
        program[idx] = random.choice(VAR)
    else:
        program[idx] = random.choice(OPS)

def crossover(p1, p2):
    idx = random.randint(0, min(len(p1), len(p2))-1)
    return p1[:idx] + p2[idx:]

# GP Parameters
pop_size = 500
generations = 50

print("Starting Python GP...")

start_py = time.time()

population = [random_program() for _ in range(pop_size)]

for gen in range(generations):
    population = sorted(population, key=fitness)
    best_fit = fitness(population[0])
    if gen % 10 == 0:
        print(f"Python GP Generation {gen}, Best Fitness: {best_fit:.6f}")
    parents = population[:20]
    new_pop = parents[:]
    while len(new_pop) < pop_size:
        p1, p2 = random.sample(parents, 2)
        child = crossover(p1, p2)
        if random.random() < 0.3:
            mutate(child)
        new_pop.append(child)
    population = new_pop

best_program_py = population[0]
best_fitness_py = fitness(best_program_py)
end_py = time.time()

print(f"Python GP done in {end_py - start_py:.2f} seconds")
print(f"Best Python program fitness: {best_fitness_py:.6f}")
print("Best Python program (prefix):")
print(best_program_py)

# gpopt

print("\ngpopt")

config = gpopt.GpoptConfig()
config.population_size = pop_size
config.generations = generations
config.num_features = 2
config.num_samples = len(X)
config.function_set = [gpopt.Op.ADD, gpopt.Op.SUB, gpopt.Op.MUL]

runner = gpopt.GpoptRunner(config)

start_lib = time.time()
runner.initialize(X_flat, y_list)
runner.run()
end_lib = time.time()

best_ind = runner.get_best_individual()

print(f"gpopt GP done in {end_lib - start_lib:.2f} seconds")
print(f"Best gpopt fitness: {best_ind.fitness}")

print("Best gpopt program found:")
print(gpopt.format_program(best_ind))
