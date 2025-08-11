#include "../src/core/Evolution.h"
#include "../include/gpopt/config.h"
#include <cassert>
#include <cmath>
#include <iostream>
#include <vector>
#include <string>

bool run_test(const std::string& test_name, GpoptConfig config) {
    std::cout << "\n--- Running Test: " << test_name << " ---\n";
    std::cout << "Selection Strategy: " << (config.selection_strategy == SelectionStrategy::TOURNAMENT ? "Tournament" : "Roulette Wheel") << std::endl;

    std::vector<float> X = {1, 1, 2, 2, 3, 3, 4, 4};
    std::vector<float> y = {2, 4, 6, 8};
    config.num_features = 2;
    config.num_samples = 4;

    Evolution evolution(config);
    evolution.initialize(X, y);

    evolution.evaluate();
    const float initial_best_fitness = evolution.getBestIndividual().fitness;
    std::cout << "Initial Best Fitness: " << initial_best_fitness << std::endl;

    evolution.run();

    const float final_best_fitness = evolution.getBestIndividual().fitness;
    std::cout << "Final Best Fitness: " << final_best_fitness << std::endl;

    if (initial_best_fitness > 1e-5) {
        assert(final_best_fitness < initial_best_fitness);
    }
    assert(final_best_fitness < 1e-5);

    std::cout << "Test '" << test_name << "' passed.\n";
    return true;
}

bool test_evolution_strategies() {
    bool all_tests_passed = true;

    // Test 1: Standard Tournament Selection
    GpoptConfig tournament_config;
    tournament_config.selection_strategy = SelectionStrategy::TOURNAMENT;
    tournament_config.tournament_size = 3;
    all_tests_passed &= run_test("Tournament Selection (Size 3)", tournament_config);

    // Test 2: Roulette Wheel Selection
    GpoptConfig roulette_config;
    roulette_config.selection_strategy = SelectionStrategy::ROULETTE_WHEEL;
    all_tests_passed &= run_test("Roulette Wheel Selection", roulette_config);

    // Test 3: Custom Function Set
    GpoptConfig custom_func_config;
    custom_func_config.function_set = {Op::ADD, Op::MUL};
    all_tests_passed &= run_test("Custom Function Set (ADD, MUL)", custom_func_config);

    return all_tests_passed;
}