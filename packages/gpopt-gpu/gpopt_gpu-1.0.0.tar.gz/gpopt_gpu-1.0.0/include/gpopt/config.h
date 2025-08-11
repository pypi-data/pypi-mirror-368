#pragma once

#include "operators.h"
#include <vector>
#include <memory>

class SelectionMethod;

enum class SelectionStrategy {
    TOURNAMENT,
    ROULETTE_WHEEL
};

/**
 * @struct GpoptConfig
 * @brief Holds all configuration parameters for a genetic programming run.
 */
struct GpoptConfig {
    // Dataset and Problem Definition
    int num_features = 0;
    int num_samples = 0;

    // Core Evolution Parameters
    int population_size = 100;
    int generations = 50;
    int max_program_length = 15;
    unsigned int random_seed = 42;

    // Genetic Operator Settings
    bool elitism = true;
    SelectionStrategy selection_strategy = SelectionStrategy::TOURNAMENT;
    int tournament_size = 2; // Only used if strategy is TOURNAMENT
    float crossover_probability = 0.8f;
    float mutation_probability = 0.15f;

    // Function Set
    // The set of operations the GP can use to build programs.
    std::vector<Op> function_set = {
        Op::ADD, Op::SUB, Op::MUL, Op::DIV
    };
};