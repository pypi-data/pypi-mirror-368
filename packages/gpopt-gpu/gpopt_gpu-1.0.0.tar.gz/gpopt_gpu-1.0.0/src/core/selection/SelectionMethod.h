#pragma once

#include "../Individual.h"
#include <vector>
#include <random>

/**
 * @class SelectionMethod
 * @brief Abstract base class for all selection strategy implementations.
 *
 * This class defines the interface for selection methods, allowing different
 * strategies (like Tournament, Roulette Wheel, etc.) to be used interchangeably.
 */
class SelectionMethod {
public:
    virtual ~SelectionMethod() = default;

    /**
     * @brief Selects a single individual from the population.
     * @param population The current population of individuals.
     * @param generator A random number generator.
     * @return A const reference to the selected individual.
     */
    virtual const Individual& select(const std::vector<Individual>& population, std::mt19937& generator) const = 0;
};