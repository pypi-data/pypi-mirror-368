#include <ATen/core/dispatch/Dispatcher.h>
#include <torch/all.h>
#include <torch/library.h>

#include "b10_kernel_ops.h"

TORCH_LIBRARY_FRAGMENT(b10_kernel, m) {
  m.def("rmsnorm(Tensor! output, Tensor input, Tensor weight, float eps, bool enable_pdl) -> ()");
  m.impl("rmsnorm", torch::kCUDA, &rmsnorm);
}

REGISTER_EXTENSION(common_ops)
