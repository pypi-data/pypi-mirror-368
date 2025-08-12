import torch
import triton.testing
from b10_kernel import rmsnorm as b10_rmsnorm
from b10_kernel.cute import rmsnorm as cute_rmsnorm


def rmsnorm_torch(x, w, eps=1e-6):
    """PyTorch reference implementation of RMSNorm."""
    orig_dtype = x.dtype
    x = x.float()
    variance = x.pow(2).mean(dim=-1, keepdim=True)
    x = x * torch.rsqrt(variance + eps)
    x = x * w.float()
    x = x.to(orig_dtype)
    return x


# Compile the function for optimization
rmsnorm_torch_compile = torch.compile(rmsnorm_torch, mode="max-autotune")


@triton.testing.perf_report(
    triton.testing.Benchmark(
        x_names=["batch_size"],  # argument names to use as an x-axis for the plot
        x_vals=[
            1,
            32,
            64,
            128,
            256,
            512,
            1024,
            2048,
            3072,
            4096,
            8192,
            12288,
            16384,
        ],  # different possible values for `x_name`
        line_arg="provider",  # argument name whose value corresponds to a different line in the plot
        line_vals=[
            "b10_kernel",
            "torch_ref",
            "torch_compile",
            "cute_rmsnorm",
        ],  # possible values for `line_arg`
        line_names=[
            "B10 Kernel",
            "Torch Reference",
            "Torch Compile",
            "Cute",
        ],  # label name for the lines
        styles=[
            ("green", "-"),
            ("red", "--"),
            ("blue", ":"),
            ("purple", "-."),
        ],  # line styles
        ylabel="GB/s",  # label name for the y-axis
        plot_name="RMSNorm memory bandwidth (higher is better)",  # name for the plot, used also as a file name for saving the plot.
        args={
            "hidden_size": 2048,
            "dtype": torch.float16,
            "eps": 1e-6,
        },  # values for function arguments not in `x_names` and `y_name`
    )
)
def benchmark_rmsnorm(hidden_size, batch_size, dtype, eps, provider):
    """Benchmark RMSNorm throughput across different implementations."""
    device = torch.device("cuda")

    # Create input tensors
    x = torch.randn(batch_size, hidden_size, device=device, dtype=dtype)
    w = torch.randn(hidden_size, device=device, dtype=dtype)

    # Calculate memory bandwidth
    # Each operation reads input (batch_size * hidden_size) and weight (hidden_size)
    # and writes output (batch_size * hidden_size)
    element_size = x.element_size()
    memory_ops = (2 * batch_size * hidden_size + hidden_size) * element_size

    def run_b10_kernel():
        return b10_rmsnorm(x, w, eps=eps)

    def run_torch_ref():
        return rmsnorm_torch(x, w, eps=eps)

    def run_torch_compile():
        return rmsnorm_torch_compile(x, w, eps=eps)

    def run_cute_rmsnorm():
        return cute_rmsnorm(x, w, eps=eps)

    if provider == "b10_kernel":
        ms = triton.testing.do_bench(run_b10_kernel)
    elif provider == "torch_ref":
        ms = triton.testing.do_bench(run_torch_ref)
    elif provider == "torch_compile":
        ms = triton.testing.do_bench(run_torch_compile)
    elif provider == "cute_rmsnorm":
        ms = triton.testing.do_bench(run_cute_rmsnorm)
    else:
        raise ValueError(f"Unknown provider: {provider}")

    # Convert to GB/s
    gbps = memory_ops / (ms * 1e-3) / 1e9
    return gbps


def verify_correctness():
    """Verify correctness across different configurations."""
    print("Running correctness tests...")

    test_configs = [
        (32, 4096, torch.float16),
        (64, 8192, torch.float16),
        (128, 2048, torch.float16),
        (1, 16384, torch.float16),
    ]

    for batch_size, hidden_size, dtype in test_configs:
        print(
            f"Testing batch_size={batch_size}, hidden_size={hidden_size}, dtype={dtype}"
        )

        device = torch.device("cuda")
        x = torch.randn(batch_size, hidden_size, device=device, dtype=dtype)
        w = torch.randn(hidden_size, device=device, dtype=dtype)

        # Compute outputs
        y_torch = rmsnorm_torch(x, w)
        y_b10 = b10_rmsnorm(x, w)
        y_compile = rmsnorm_torch_compile(x, w)
        y_cute = cute_rmsnorm(x, w)

        # Check correctness
        try:
            torch.testing.assert_close(y_torch, y_b10, rtol=1e-3, atol=1e-3)
            print("  ✓ B10 vs Torch: PASSED")
        except AssertionError as e:
            print(f"  ✗ B10 vs Torch: FAILED: {e}")

        try:
            torch.testing.assert_close(y_torch, y_compile, rtol=1e-3, atol=1e-3)
            print("  ✓ Compile vs Torch: PASSED")
        except AssertionError as e:
            print(f"  ✗ Compile vs Torch: FAILED: {e}")

        try:
            torch.testing.assert_close(y_torch, y_cute, rtol=1e-3, atol=1e-3)
            print("  ✓ Cute vs Torch: PASSED")
        except AssertionError as e:
            print(f"  ✗ Cute vs Torch: FAILED: {e}")

        # Compute relative errors
        rel_error_b10 = torch.abs(y_torch - y_b10) / (torch.abs(y_torch) + 1e-8)
        rel_error_compile = torch.abs(y_torch - y_compile) / (torch.abs(y_torch) + 1e-8)
        rel_error_cute = torch.abs(y_torch - y_cute) / (torch.abs(y_torch) + 1e-8)
        print(
            f"  B10 - Max rel error: {rel_error_b10.max().item():.2e}, Mean: {rel_error_b10.mean().item():.2e}"
        )
        print(
            f"  Compile - Max rel error: {rel_error_compile.max().item():.2e}, Mean: {rel_error_compile.mean().item():.2e}"
        )
        print(
            f"  Cute - Max rel error: {rel_error_cute.max().item():.2e}, Mean: {rel_error_cute.mean().item():.2e}"
        )
        print()


if __name__ == "__main__":
    # Check CUDA availability
    if not torch.cuda.is_available():
        print("CUDA is not available. Benchmarks require GPU.")
        exit(1)

    print("B10 Kernel RMSNorm Benchmark")
    print("=" * 40)

    # Warm up torch.compile
    print("Warming up torch.compile...")
    device = torch.device("cuda")
    x_warmup = torch.randn(32, 4096, device=device, dtype=torch.float16)
    w_warmup = torch.randn(4096, device=device, dtype=torch.float16)
    _ = rmsnorm_torch_compile(x_warmup, w_warmup)  # Trigger compilation
    print("Warmup completed.")
    print()

    # Run correctness check first
    verify_correctness()

    print("Running benchmarks...")
    benchmark_rmsnorm.run(print_data=True)
