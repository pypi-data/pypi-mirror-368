// Adapted from
// https://github.com/flashinfer-ai/flashinfer/blob/main/include/flashinfer/norm.cuh
#include <numeric>

#include "math.cuh"
#include "utils.cuh"
#include "vec_dtype.cuh"

template <uint32_t VEC_SIZE, typename T>
__global__ void rmsnorm_kernel(
    T* __restrict__ input,
    T* __restrict__ weight,
    T* __restrict__ output,
    const uint32_t d,
    const uint32_t stride_input,
    const uint32_t stride_output,
    float weight_bias,
    float eps) {
  const uint32_t bx = blockIdx.x;
  const uint32_t tx = threadIdx.x, ty = threadIdx.y;
  constexpr uint32_t warp_size = 32;
  const uint32_t num_warps = blockDim.y;
  const uint32_t thread_id = tx + ty * warp_size;
  const uint32_t num_threads = num_warps * warp_size;
  const uint32_t rounds = math_util::ceil_div(d, VEC_SIZE * num_threads);
  extern __shared__ float smem[];

  float sum_sq = 0.f;

#if (__CUDACC_VER_MAJOR__ >= 12 && defined(__CUDA_ARCH__) && (__CUDA_ARCH__ >= 900))
  asm volatile("griddepcontrol.wait;");
#endif

  for (uint32_t i = 0; i < rounds; i++) {
    vec_t<T, VEC_SIZE> input_vec;
    input_vec.fill(0.f);
    if ((i * num_threads + thread_id) * VEC_SIZE < d) {
      input_vec.load(input + bx * stride_input + i * num_threads * VEC_SIZE + thread_id * VEC_SIZE);
    }
#pragma unroll
    for (uint32_t j = 0; j < VEC_SIZE; j++) {
      sum_sq += float(input_vec[j]) * float(input_vec[j]);
    }
  }

  // first, warp reduce sum
#pragma unroll
  for (uint32_t offset = warp_size / 2; offset > 0; offset /= 2) {
    sum_sq += math_util::shfl_xor_sync(sum_sq, offset);
  }

  smem[ty] = sum_sq;
  __syncthreads();
  // then, cross warp reduce sum using only the first warp
  if (ty == 0) {
    sum_sq = (tx < num_warps) ? smem[tx] : 0.f;
#pragma unroll
    for (uint32_t offset = warp_size / 2; offset > 0; offset /= 2) {
      sum_sq += math_util::shfl_xor_sync(sum_sq, offset);
    }
    smem[0] = sum_sq;
  }
  __syncthreads();

  float rms_rcp = math_util::rsqrt(smem[0] / float(d) + eps);

  for (uint32_t i = 0; i < rounds; i++) {
    vec_t<T, VEC_SIZE> input_vec;
    vec_t<T, VEC_SIZE> weight_vec;
    vec_t<T, VEC_SIZE> output_vec;
    input_vec.fill(0.f);
    weight_vec.fill(0.f);
    if ((i * num_threads + thread_id) * VEC_SIZE < d) {
      input_vec.load(input + bx * stride_input + i * num_threads * VEC_SIZE + thread_id * VEC_SIZE);
      weight_vec.load(weight + i * num_threads * VEC_SIZE + thread_id * VEC_SIZE);
    }
#pragma unroll
    for (uint32_t j = 0; j < VEC_SIZE; j++) {
      output_vec[j] = float(input_vec[j]) * rms_rcp * (weight_bias + float(weight_vec[j]));
    }
    if ((i * num_threads + thread_id) * VEC_SIZE < d) {
      output_vec.store(output + bx * stride_output + i * num_threads * VEC_SIZE + thread_id * VEC_SIZE);
    }
  }
#if (__CUDACC_VER_MAJOR__ >= 12 && defined(__CUDA_ARCH__) && (__CUDA_ARCH__ >= 900))
  asm volatile("griddepcontrol.launch_dependents;");
#endif
}

template <typename T>
cudaError_t rmsnorm_kernel_launcher(
    T* input,
    T* weight,
    T* output,
    uint32_t batch_size,
    uint32_t d,
    uint32_t stride_input,
    uint32_t stride_output,
    float eps = 1e-5,
    bool enable_pdl = false,
    cudaStream_t stream = 0) {
  const uint32_t vec_size = std::gcd(16 / sizeof(T), d);

  const uint32_t block_size = std::min<uint32_t>(1024, d / vec_size);
  const uint32_t num_warps = math_util::ceil_div(block_size, 32);
  dim3 nblks(batch_size);
  dim3 nthrs(32, num_warps);
  const uint32_t smem_size = num_warps * sizeof(float);
  float weight_bias = 0.f;
  void* args[] = {&input, &weight, &output, &d, &stride_input, &stride_output, &weight_bias, &eps};

  cudaLaunchConfig_t config;
  config.gridDim = nblks;
  config.blockDim = nthrs;
  config.dynamicSmemBytes = smem_size;
  config.stream = stream;
  cudaLaunchAttribute attrs[1];
  attrs[0].id = cudaLaunchAttributeProgrammaticStreamSerialization;
  attrs[0].val.programmaticStreamSerializationAllowed = enable_pdl;
  config.numAttrs = 1;
  config.attrs = attrs;

  DISPATCH_ALIGNED_VEC_SIZE(vec_size, VEC_SIZE, {
    auto kernel = rmsnorm_kernel<VEC_SIZE, T>;
    cudaFuncSetAttribute(kernel, cudaFuncAttributeMaxDynamicSharedMemorySize, smem_size);
    cudaLaunchKernelEx(&config, kernel, input, weight, output, d, stride_input, stride_output, weight_bias, eps);
  });
  return cudaSuccess;
}

void rmsnorm(at::Tensor& output, at::Tensor& input, at::Tensor& weight, double eps, bool enable_pdl) {
  CHECK_LAST_DIM_CONTIGUOUS_INPUT(input);
  CHECK_LAST_DIM_CONTIGUOUS_INPUT(weight);
  auto device = input.device();
  CHECK_EQ(weight.device(), device);
  CHECK_DIM(2, input);   // input: (batch_size, hidden_size)
  CHECK_DIM(1, weight);  // weight: (hidden_size)
  CHECK_EQ(input.size(1), weight.size(0));
  unsigned int batch_size = input.size(0);
  unsigned int hidden_size = input.size(1);
  CHECK_EQ(output.size(0), batch_size);
  CHECK_EQ(output.size(1), hidden_size);

  const cudaStream_t stream = c10::cuda::getCurrentCUDAStream();
  DISPATCH_PYTORCH_DTYPE_TO_CTYPE_FP16(input.scalar_type(), c_type, [&] {
    cudaError_t status = rmsnorm_kernel_launcher(
        static_cast<c_type*>(input.data_ptr()),
        static_cast<c_type*>(weight.data_ptr()),
        static_cast<c_type*>(output.data_ptr()),
        batch_size,
        hidden_size,
        input.stride(0),
        output.stride(0),
        eps,
        enable_pdl,
        stream);
    TORCH_CHECK(status == cudaSuccess, "RMSNorm failed with error code " + std::string(cudaGetErrorString(status)));
    return true;
  });
}
