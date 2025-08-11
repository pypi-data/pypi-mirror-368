#include "kernels.cuh"
#include <cuda_runtime.h>

__global__ void evaluate_population_kernel(const Node* d_population, const float* d_X, float* d_intermediate_results, const Op* d_function_set, int function_set_size, int max_prog_len, int pop_size, int num_features, int num_samples) {
    extern __shared__ Node shared_prog[];
    int ind_idx = blockIdx.x;
    int sample_idx = threadIdx.x;

    if (sample_idx < max_prog_len) {
        shared_prog[sample_idx] = d_population[ind_idx * max_prog_len + sample_idx];
    }
    __syncthreads();

    if (sample_idx < num_samples) {
        float stack[16];
        int sp = 0;

        for (int i = 0; i < max_prog_len; ++i) {
            Node node = shared_prog[i];
            if (node.op == Op::VAR) {
                if (sp < 16) stack[sp++] = d_X[sample_idx * num_features + static_cast<int>(node.value)];
            } else {
                if (sp >= 2) {
                    float op2 = stack[--sp];
                    float op1 = stack[--sp];
                    float result;
                    switch (node.op) {
                        case Op::ADD: result = op1 + op2; break;
                        case Op::SUB: result = op1 - op2; break;
                        case Op::MUL: result = op1 * op2; break;
                        case Op::DIV: result = (op2 == 0) ? 1.0f : op1 / op2; break;
                        default: result = 0.0f; break;
                    }
                    stack[sp++] = result;
                } else {
                    stack[sp++] = 0.0f; 
                }
            }
        }
        if (sp > 0) {
            d_intermediate_results[ind_idx * num_samples + sample_idx] = stack[0];
        } else {
            d_intermediate_results[ind_idx * num_samples + sample_idx] = 0.0f;
        }
    }
}

__global__ void reduce_fitness_kernel(const float* d_intermediate_results, const float* d_y, float* d_final_fitness, int pop_size, int num_samples) {
    int ind_idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (ind_idx < pop_size) {
        float mse = 0.0f;
        for (int i = 0; i < num_samples; ++i) {
            float diff = d_intermediate_results[ind_idx * num_samples + i] - d_y[i];
            mse += diff * diff;
        }
        d_final_fitness[ind_idx] = mse / num_samples;
    }
}