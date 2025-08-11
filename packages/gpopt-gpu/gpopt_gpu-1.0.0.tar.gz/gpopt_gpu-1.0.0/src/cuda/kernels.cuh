#pragma once

#include <cuda_runtime.h>
#include "core/Individual.h"

// kernel declarations
__global__ void evaluate_population_kernel(
    const Node* population,
    const float* X,
    float* intermediate_errors,
    const Op* function_set,
    int function_set_size,
    int max_program_len,
    int population_size,
    int num_features,
    int num_samples
);

__global__ void reduce_fitness_kernel(
    const float* intermediate_errors,
    const float* y,
    float* final_fitness,
    int population_size,
    int num_samples
);