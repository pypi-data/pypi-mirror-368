#include <iostream>
#include <vector>
#include <cmath>
#include <cuda_runtime.h>
#include "core/DeviceManager.h"
#include "cuda/kernels.cuh"

// Test 1: Matrix Addition Sanity Check
__global__ void matrixAdd(const float* a, const float* b, float* c, int width, int height) {
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    if (col < width && row < height) {
        int idx = row * width + col;
        c[idx] = a[idx] + b[idx];
    }
}

extern "C" bool test_matrix_addition() {
    const int WIDTH = 256, HEIGHT = 256;
    const size_t matrix_elements = WIDTH * HEIGHT;
    DeviceManager deviceManager;
    std::vector<float> h_A(matrix_elements), h_B(matrix_elements), h_C(matrix_elements);
    for (size_t i = 0; i < matrix_elements; ++i) { h_A[i] = static_cast<float>(i); h_B[i] = static_cast<float>(i); }
    float* d_A = deviceManager.allocate<float>(matrix_elements);
    float* d_B = deviceManager.allocate<float>(matrix_elements);
    float* d_C = deviceManager.allocate<float>(matrix_elements);
    deviceManager.copyHostToDeviceAsync(d_A, h_A.data(), matrix_elements);
    deviceManager.copyHostToDeviceAsync(d_B, h_B.data(), matrix_elements);
    dim3 threadsPerBlock(16, 16);
    dim3 numBlocks((WIDTH + threadsPerBlock.x - 1) / threadsPerBlock.x, (HEIGHT + threadsPerBlock.y - 1) / threadsPerBlock.y);
    matrixAdd<<<numBlocks, threadsPerBlock, 0, deviceManager.getStream()>>>(d_A, d_B, d_C, WIDTH, HEIGHT);
    deviceManager.copyDeviceToHostAsync(h_C.data(), d_C, matrix_elements);
    deviceManager.synchronize();
    bool success = true;
    for (size_t i = 0; i < matrix_elements; ++i) {
        if (std::abs(h_C[i] - (h_A[i] + h_B[i])) > 1e-5) { success = false; break; }
    }
    deviceManager.free(d_A); deviceManager.free(d_B); deviceManager.free(d_C);
    return success;
}

// Test 2: GP Kernel Evaluation
extern "C" bool test_gp_kernels() {
    DeviceManager dm;
    const int POP_SIZE = 2;
    const int MAX_PROG_LEN = 5;
    const int NUM_SAMPLES = 4;
    const int NUM_FEATURES = 2;

    std::vector<Node> h_population(POP_SIZE * MAX_PROG_LEN);
    // Program 1: (x0 * 2.0) + x1  -> RPN: x0, 2.0, *, x1, +
    h_population[0] = {Op::VAR, 0.0f};
    h_population[1] = {Op::CONST, 2.0f};
    h_population[2] = {Op::MUL, 0.0f};
    h_population[3] = {Op::VAR, 1.0f};
    h_population[4] = {Op::ADD, 0.0f};
    // Program 2: (x1 - x0) -> RPN: x1, x0, -
    h_population[5] = {Op::VAR, 1.0f};
    h_population[6] = {Op::VAR, 0.0f};
    h_population[7] = {Op::SUB, 0.0f};

    std::vector<float> h_X = {1, 1,  2, 2,  3, 3,  4, 4};
    std::vector<float> h_y = {3,    4,    9,    12};

    Node* d_population = dm.allocate<Node>(POP_SIZE * MAX_PROG_LEN);
    float* d_X = dm.allocate<float>(NUM_SAMPLES * NUM_FEATURES);
    float* d_y = dm.allocate<float>(NUM_SAMPLES);
    float* d_intermediate_errors = dm.allocate<float>(POP_SIZE * NUM_SAMPLES);
    float* d_final_fitness = dm.allocate<float>(POP_SIZE);

    dm.copyHostToDeviceAsync(d_population, h_population.data(), POP_SIZE * MAX_PROG_LEN);
    dm.copyHostToDeviceAsync(d_X, h_X.data(), NUM_SAMPLES * NUM_FEATURES);
    dm.copyHostToDeviceAsync(d_y, h_y.data(), NUM_SAMPLES);

    dim3 eval_blocks(POP_SIZE, 1, 1);
    dim3 eval_threads(256, 1, 1);
    size_t shared_mem_size = MAX_PROG_LEN * sizeof(Node);
    evaluate_population_kernel<<<eval_blocks, eval_threads, shared_mem_size, dm.getStream()>>>(
        d_population, d_X, d_intermediate_errors, MAX_PROG_LEN, POP_SIZE, NUM_FEATURES, NUM_SAMPLES);

    dim3 reduce_blocks((POP_SIZE + 255) / 256, 1, 1);
    dim3 reduce_threads(256, 1, 1);
    reduce_fitness_kernel<<<reduce_blocks, reduce_threads, 0, dm.getStream()>>>(
        d_intermediate_errors, d_y, d_final_fitness, POP_SIZE, NUM_SAMPLES);

    std::vector<float> h_final_fitness(POP_SIZE);
    dm.copyDeviceToHostAsync(h_final_fitness.data(), d_final_fitness, POP_SIZE);
    dm.synchronize();

    float expected_fitness1 = 1.0f;
    float expected_fitness2 = 62.5f;
    bool success = true;
    if (std::abs(h_final_fitness[0] - expected_fitness1) > 1e-5) success = false;
    if (std::abs(h_final_fitness[1] - expected_fitness2) > 1e-5) success = false;

    dm.free(d_population);
    dm.free(d_X);
    dm.free(d_y);
    dm.free(d_intermediate_errors);
    dm.free(d_final_fitness);

    return success;
}