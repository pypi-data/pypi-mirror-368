#include "../src/core/Evolution.h"
#include "../include/gpopt/config.h"
#include <cassert>
#include <cmath>
#include <iostream>
#include <vector>
#include <string>

bool run_test(const std::string& test_name, GpoptConfig config) {
    std::cout << "\n Running Test: " << test_name << "\n";

    std::vector<float> X = {1, 1, 2, 2, 3, 3, 4, 4};
    std::vector<float> y = {2, 4, 6, 8}; // target is x0 + x1
    config.num_features = 2;
    config.num_samples = 4;

    Evolution evolution(config);
    evolution.initialize(X, y);

    evolution.evaluate();
    const float initial_best_fitness = evolution.getBestIndividual().fitness;
    std::cout << "Initial Best Fitness: " << initial_best_fitness << std::endl;

    evolution.run();

    const auto& final_best_individual = evolution.getBestIndividual();
    const float final_best_fitness = final_best_individual.fitness;
    std::cout << "Final Best Fitness: " << final_best_fitness << std::endl;

    assert(final_best_fitness <= initial_best_fitness + 1e-6); // tolerance for float precision

    if (initial_best_fitness > 1e-5) {
        if (config.elitism || config.crossover_probability > 0 || config.mutation_probability > 0) {
            assert(final_best_fitness < initial_best_fitness);
        }
    }

    if (config.crossover_probability > 0.5 && config.mutation_probability > 0.1) {
         assert(final_best_fitness < 1e-5);
    }

    std::cout << "Test '" << test_name << "' passed.\n";
    return true;
}

bool test_evolution_run() {
    bool all_tests_passed = true;

    // Test 1: Standard configuration; converges to a perfect solution
    GpoptConfig standard_config;
    all_tests_passed &= run_test("Standard Converging Run", standard_config);

    // Test 2: No elitism.
    GpoptConfig no_elitism_config;
    no_elitism_config.elitism = false;
    all_tests_passed &= run_test("No Elitism", no_elitism_config);

    // Test 3: Higher tournament size.
    GpoptConfig high_pressure_config;
    high_pressure_config.tournament_size = 5;
    all_tests_passed &= run_test("High Selection Pressure (Tournament Size 5)", high_pressure_config);

    // Test 4: No crossover, only mutation.
    GpoptConfig mutation_only_config;
    mutation_only_config.crossover_probability = 0.0f;
    mutation_only_config.mutation_probability = 0.2f;
    all_tests_passed &= run_test("Mutation-Only Evolution", mutation_only_config);

    // Test 5: No mutation, only crossover.
    GpoptConfig crossover_only_config;
    crossover_only_config.mutation_probability = 0.0f;
    all_tests_passed &= run_test("Crossover-Only Evolution", crossover_only_config);

    return all_tests_passed;
}