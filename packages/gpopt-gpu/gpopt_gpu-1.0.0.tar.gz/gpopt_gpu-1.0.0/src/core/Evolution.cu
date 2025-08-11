#include "Evolution.h"
#include <algorithm>
#include <iostream>
#include <stdexcept>

std::unique_ptr<SelectionMethod> create_selection_method(const GpoptConfig& config);

__global__ void evaluate_population_kernel(const Node* d_population, const float* d_X, float* d_intermediate_results, const Op* d_function_set, int function_set_size, int max_prog_len, int pop_size, int num_features, int num_samples);
__global__ void reduce_fitness_kernel(const float* d_intermediate_results, const float* d_y, float* d_final_fitness, int pop_size, int num_samples);


Evolution::Evolution(const GpoptConfig& config)
    : config_(config),
      population_(config, create_selection_method(config)) {
    d_population_ = dm_.allocate<Node>(config.population_size * config.max_program_length);
    d_X_ = dm_.allocate<float>(config.num_samples * config.num_features);
    d_y_ = dm_.allocate<float>(config.num_samples);
    d_intermediate_results_ = dm_.allocate<float>(config.population_size * config.num_samples);
    d_final_fitness_ = dm_.allocate<float>(config.population_size);
    d_function_set_ = dm_.allocate<Op>(config.function_set.size());

    dm_.copyHostToDeviceAsync(d_function_set_, config.function_set.data(), config.function_set.size());
    dm_.synchronize();
}

Evolution::~Evolution() {
    dm_.free(d_population_);
    dm_.free(d_X_);
    dm_.free(d_y_);
    dm_.free(d_intermediate_results_);
    dm_.free(d_final_fitness_);
    dm_.free(d_function_set_);
}

void Evolution::initialize(const std::vector<float>& X, const std::vector<float>& y) {
    dm_.copyHostToDeviceAsync(d_X_, X.data(), X.size());
    dm_.copyHostToDeviceAsync(d_y_, y.data(), y.size());
    dm_.synchronize();
}

void Evolution::run() {
    for (int gen = 0; gen < config_.generations; ++gen) {
        evaluate();
        if ((gen % 10 == 0) || gen == config_.generations - 1) {
            std::cout << "Generation " << gen << ", Best Fitness: " << getBestIndividual().fitness << std::endl;
        }
        population_.evolve();
    }
}

void Evolution::evaluate() {
    std::vector<Node> h_population_flat;
    h_population_flat.reserve(config_.population_size * config_.max_program_length);
    for(const auto& ind : population_.getIndividuals()) {
        h_population_flat.insert(h_population_flat.end(), ind.program.begin(), ind.program.end());
    }
    dm_.copyHostToDeviceAsync(d_population_, h_population_flat.data(), h_population_flat.size());

    dim3 eval_blocks(config_.population_size, 1, 1);
    dim3 eval_threads(256, 1, 1);
    size_t shared_mem_size = config_.max_program_length * sizeof(Node);

    evaluate_population_kernel<<<eval_blocks, eval_threads, shared_mem_size, dm_.getStream()>>>(
        d_population_, d_X_, d_intermediate_results_, d_function_set_, config_.function_set.size(), config_.max_program_length, config_.population_size, config_.num_features, config_.num_samples);

    dim3 reduce_blocks((config_.population_size + 255) / 256, 1, 1);
    dim3 reduce_threads(256, 1, 1);

    reduce_fitness_kernel<<<reduce_blocks, reduce_threads, 0, dm_.getStream()>>>(
        d_intermediate_results_, d_y_, d_final_fitness_, config_.population_size, config_.num_samples);

    std::vector<float> h_fitness(config_.population_size);
    dm_.copyDeviceToHostAsync(h_fitness.data(), d_final_fitness_, config_.population_size);
    dm_.synchronize();

    auto& individuals = population_.getIndividuals();
    for(int i = 0; i < config_.population_size; ++i) {
        individuals[i].fitness = h_fitness[i];
    }
}

const Individual& Evolution::getBestIndividual() const {
    const auto& individuals = population_.getIndividuals();
    auto it = std::min_element(individuals.cbegin(), individuals.cend(),
        [](const Individual& a, const Individual& b){ return a.fitness < b.fitness; });
    return *it;
}

std::unique_ptr<SelectionMethod> create_selection_method(const GpoptConfig& config) {
    switch (config.selection_strategy) {
        case SelectionStrategy::TOURNAMENT:
            return std::make_unique<TournamentSelection>(config.tournament_size);
        case SelectionStrategy::ROULETTE_WHEEL:
            return std::make_unique<RouletteWheelSelection>();
        default:
            throw std::runtime_error("Unknown selection strategy specified in configuration.");
    }
}