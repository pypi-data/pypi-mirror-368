#pragma once

#include "../../include/gpopt/config.h"
#include "Individual.h"
#include "selection/SelectionMethod.h"
#include <vector>
#include <random>
#include <algorithm>
#include <numeric>
#include <memory>
#include <stdexcept>

class Population {
public:
    Population(const GpoptConfig& config, std::unique_ptr<SelectionMethod> selection_method)
        : config_(config),
          individuals_(config.population_size),
          generator_(config.random_seed),
          selection_method_(std::move(selection_method)) {
        initialize_population();
    }

    std::vector<Individual>& getIndividuals() { return individuals_; }
    const std::vector<Individual>& getIndividuals() const { return individuals_; }

    void evolve() {
        std::vector<Individual> next_generation;
        next_generation.reserve(config_.population_size);

        if (config_.elitism) {
            auto best_it = std::min_element(individuals_.cbegin(), individuals_.cend(),
                [](const Individual& a, const Individual& b) { return a.fitness < b.fitness; });
            next_generation.push_back(*best_it);
        }

        std::uniform_real_distribution<float> prob_dist(0.0f, 1.0f);
        while (next_generation.size() < config_.population_size) {
            const Individual& parent1 = selection_method_->select(individuals_, generator_);
            const Individual& parent2 = selection_method_->select(individuals_, generator_);

            Individual child1 = parent1;
            Individual child2 = parent2;

            if (prob_dist(generator_) < config_.crossover_probability) {
                subtree_crossover(child1, child2);
            }

            if (prob_dist(generator_) < config_.mutation_probability) {
                subtree_mutation(child1);
            }
            if (prob_dist(generator_) < config_.mutation_probability) {
                subtree_mutation(child2);
            }

            next_generation.push_back(child1);
            if (next_generation.size() < config_.population_size) {
                next_generation.push_back(child2);
            }
        }

        individuals_ = std::move(next_generation);
    }

private:
    int get_arity(Op op) const {
        switch(op) {
            case Op::ADD: case Op::SUB: case Op::MUL: case Op::DIV:
                return 2;
            case Op::VAR: case Op::CONST:
                return 0;
            default: return 2;
        }
    }
    
    std::pair<int, int> find_subtree_range(const std::vector<Node>& program, int end_idx) const {
        int required = 1;
        for (int i = end_idx; i >= 0; --i) {
            required += get_arity(program[i].op) - 1;
            if (required == 0) {
                return {i, end_idx};
            }
        }
        return {end_idx, end_idx};
    }

    void subtree_crossover(Individual& ind1, Individual& ind2) {
        if (ind1.program.empty() || ind2.program.empty()) return;

        std::uniform_int_distribution<int> dist1(0, ind1.program.size() - 1);
        std::uniform_int_distribution<int> dist2(0, ind2.program.size() - 1);

        auto range1 = find_subtree_range(ind1.program, dist1(generator_));
        auto range2 = find_subtree_range(ind2.program, dist2(generator_));

        std::vector<Node> subtree1(ind1.program.begin() + range1.first, ind1.program.begin() + range1.second + 1);
        std::vector<Node> subtree2(ind2.program.begin() + range2.first, ind2.program.begin() + range2.second + 1);
        
        if (ind1.program.size() - subtree1.size() + subtree2.size() > config_.max_program_length ||
            ind2.program.size() - subtree2.size() + subtree1.size() > config_.max_program_length) {
            return; 
        }

        std::vector<Node> new_prog1;
        new_prog1.reserve(ind1.program.size() - subtree1.size() + subtree2.size());
        new_prog1.insert(new_prog1.end(), ind1.program.begin(), ind1.program.begin() + range1.first);
        new_prog1.insert(new_prog1.end(), subtree2.begin(), subtree2.end());
        new_prog1.insert(new_prog1.end(), ind1.program.begin() + range1.second + 1, ind1.program.end());

        std::vector<Node> new_prog2;
        new_prog2.reserve(ind2.program.size() - subtree2.size() + subtree1.size());
        new_prog2.insert(new_prog2.end(), ind2.program.begin(), ind2.program.begin() + range2.first);
        new_prog2.insert(new_prog2.end(), subtree1.begin(), subtree1.end());
        new_prog2.insert(new_prog2.end(), ind2.program.begin() + range2.second + 1, ind2.program.end());

        ind1.program = std::move(new_prog1);
        ind2.program = std::move(new_prog2);
    }

    void subtree_mutation(Individual& ind) {
        if (ind.program.empty()) return;

        std::uniform_int_distribution<int> dist(0, ind.program.size() - 1);
        auto range = find_subtree_range(ind.program, dist(generator_));
        
        int subtree_len = range.second - range.first + 1;
        auto new_subtree = generate_valid_program(subtree_len); 

        ind.program.erase(ind.program.begin() + range.first, ind.program.begin() + range.second + 1);
        ind.program.insert(ind.program.begin() + range.first, new_subtree.begin(), new_subtree.end());
    }

    void initialize_population() {
        for (auto& ind : individuals_) {
            ind.program = generate_valid_program(config_.max_program_length);
        }
    }
    
    std::vector<Node> generate_valid_program(int length) {
        if (length <= 0) return {};
        std::vector<Node> program;
        program.reserve(length);
        std::uniform_int_distribution<int> func_dist(0, config_.function_set.size() - 1);
        std::uniform_int_distribution<int> var_dist(0, config_.num_features - 1);
        
        int stack = 0;
        for (int i = 0; i < length; ++i) {
            bool must_add_terminal = (stack < 2);
            bool can_add_operator = (stack >= 2);

            if (must_add_terminal || (can_add_operator && std::uniform_int_distribution<>(0, 1)(generator_) == 0)) {
                program.push_back({Op::VAR, static_cast<float>(var_dist(generator_))});
                stack++;
            } else {
                program.push_back({config_.function_set[func_dist(generator_)], 0.0f});
                stack--; // a binary operator consumes 2 and produces 1, a net change of -1.
            }
        }

        // ensure the program is valid by fixing the stack from the end.
        stack = 0;
        for (int i = program.size() - 1; i >= 0; --i) {
            int arity = get_arity(program[i].op);
            if (stack < arity) {
                // mot enough operands for this operator, so turn it into a terminal.
                program[i] = {Op::VAR, static_cast<float>(var_dist(generator_))};
                stack++;
            } else {
                stack = stack - arity + 1;
            }
        }
        return program;
    }

    GpoptConfig config_;
    std::vector<Individual> individuals_;
    std::mt19937 generator_;
    std::unique_ptr<SelectionMethod> selection_method_;
};