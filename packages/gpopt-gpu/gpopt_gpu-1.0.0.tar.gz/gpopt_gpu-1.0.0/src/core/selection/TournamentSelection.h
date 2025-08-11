#pragma once

#include "SelectionMethod.h"
#include <stdexcept>

/**
 * @class TournamentSelection
 * @brief Implements tournament selection.
 *
 * Individuals are chosen at random, and the one with the best fitness from that
 * small group is selected.
 */
class TournamentSelection : public SelectionMethod {
public:
    explicit TournamentSelection(int tournament_size) : tournament_size_(tournament_size) {
        if (tournament_size < 1) {
            throw std::invalid_argument("Tournament size must be at least 1.");
        }
    }

    const Individual& select(const std::vector<Individual>& population, std::mt19937& generator) const override {
        std::uniform_int_distribution<int> dist(0, population.size() - 1);
        const Individual* best = &population[dist(generator)];

        for (int i = 1; i < tournament_size_; ++i) {
            const Individual& contender = population[dist(generator)];
            if (contender.fitness < best->fitness) {
                best = &contender;
            }
        }
        return *best;
    }

private:
    int tournament_size_;
};