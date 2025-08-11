#pragma once

#include "../../include/gpopt/config.h"
#include "DeviceManager.h"
#include "Population.h"
#include "selection/SelectionMethod.h"
#include "selection/TournamentSelection.h"
#include "selection/RouletteWheelSelection.h"
#include <vector>
#include <memory>

class Evolution {
public:
    Evolution(const GpoptConfig& config);
    ~Evolution();

    void initialize(const std::vector<float>& X, const std::vector<float>& y);
    void run();
    void evaluate();
    const Individual& getBestIndividual() const;

private:
    GpoptConfig config_;
    Population population_;
    DeviceManager dm_;

    // Device pointers
    Node* d_population_;
    float* d_X_;
    float* d_y_;
    float* d_intermediate_results_;
    float* d_final_fitness_;
    Op* d_function_set_;
};