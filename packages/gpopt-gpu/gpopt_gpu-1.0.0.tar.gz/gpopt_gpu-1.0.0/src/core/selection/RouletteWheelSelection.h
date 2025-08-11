#pragma once

#include "SelectionMethod.h"
#include <numeric>
#include <stdexcept>

/**
 * @class RouletteWheelSelection
 * @brief Implements roulette wheel (fitness proportionate) selection.
 *
 * The chance for an individual to be selected is proportional to its fitness.
 * Assumes that lower fitness values are better.
 */
class RouletteWheelSelection : public SelectionMethod {
public:
    const Individual& select(const std::vector<Individual>& population, std::mt19937& generator) const override {
        double total_inverse_fitness = 0.0;
        for (const auto& ind : population) {
            // add a small epsilon to avoid division by zero for perfect fitness
            total_inverse_fitness += 1.0 / (ind.fitness + 1e-6);
        }

        std::uniform_real_distribution<double> dist(0.0, total_inverse_fitness);
        double slice = dist(generator);

        double current_sum = 0.0;
        for (const auto& ind : population) {
            current_sum += 1.0 / (ind.fitness + 1e-6);
            if (current_sum >= slice) {
                return ind;
            }
        }
        return population.back();
    }
};