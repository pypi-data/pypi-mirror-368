#include <torch/extension.h>
#include "balinski-and-gomory-cuda/src/solver.h"

// Declare your CUDA function
// extern "C" void solve(float* d_C, int* d_X, float* d_U, float* d_V, int n);
// void solve(float* d_C, int* d_X, float* d_U, float* d_V, int n);

torch::Tensor solve_binding(torch::Tensor C, torch::Tensor X, torch::Tensor U, torch::Tensor V) {
    // TORCH_CHECK(C.is_cuda(), "C must be a CUDA tensor");
    // TORCH_CHECK(X.is_cuda(), "X must be a CUDA tensor");
    // TORCH_CHECK(U.is_cuda(), "U must be a CUDA tensor");
    // TORCH_CHECK(V.is_cuda(), "V must be a CUDA tensor");

    // TORCH_CHECK(C.is_contiguous(), "C must be contiguous");
    // TORCH_CHECK(X.is_contiguous(), "X must be contiguous");
    // TORCH_CHECK(U.is_contiguous(), "U must be contiguous");
    // TORCH_CHECK(V.is_contiguous(), "V must be contiguous");

    int n = C.size(0);
    solve(C.data_ptr<float>(), X.data_ptr<int>(), U.data_ptr<float>(), V.data_ptr<float>(), n);
    // cudaDeviceSynchronize(); // optional

    return X;
}

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
    m.def("solve", &solve_binding, "Custom CUDA solve");
}
