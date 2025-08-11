#pragma once

#include <iostream>
#include <cuda_runtime.h>

// Helper to check for CUDA errors
#define CUDA_CHECK(err) { \
    if (err != cudaSuccess) { \
        std::cerr << "CUDA Error: " << cudaGetErrorString(err) << " in " << __FILE__ << " at line " << __LINE__ << std::endl; \
        exit(EXIT_FAILURE); \
    } \
}

class DeviceManager {
public:
    DeviceManager() {
        CUDA_CHECK(cudaStreamCreate(&stream));
    }

    ~DeviceManager() {
        CUDA_CHECK(cudaStreamDestroy(stream));
    }
    
    DeviceManager(const DeviceManager&) = delete;
    DeviceManager& operator=(const DeviceManager&) = delete;

    template<typename T>
    T* allocate(size_t num_elements) {
        T* d_ptr = nullptr;
        CUDA_CHECK(cudaMalloc(&d_ptr, num_elements * sizeof(T)));
        return d_ptr;
    }

    template<typename T>
    void free(T* d_ptr) {
        if (d_ptr) {
            CUDA_CHECK(cudaFree(d_ptr));
        }
    }

    template<typename T>
    void copyHostToDeviceAsync(T* d_ptr, const T* h_ptr, size_t num_elements) {
        CUDA_CHECK(cudaMemcpyAsync(d_ptr, h_ptr, num_elements * sizeof(T), cudaMemcpyHostToDevice, stream));
    }

    template<typename T>
    void copyDeviceToHostAsync(T* h_ptr, const T* d_ptr, size_t num_elements) {
        CUDA_CHECK(cudaMemcpyAsync(h_ptr, d_ptr, num_elements * sizeof(T), cudaMemcpyDeviceToHost, stream));
    }

    void synchronize() {
        CUDA_CHECK(cudaStreamSynchronize(stream));
    }

    cudaStream_t getStream() const {
        return stream;
    }

private:
    cudaStream_t stream;
};
