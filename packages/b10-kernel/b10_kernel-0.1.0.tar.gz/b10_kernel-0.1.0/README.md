# b10-kernel

Baseten Kernel Library - High-performance CUDA kernels for machine learning workloads.

## Installation

### From PyPI
```bash
pip install b10-kernel
```

**Requirements:**
- Python >= 3.12
- CUDA-compatible GPU and drivers
- PyTorch >= 2.8.0 with CUDA support

### From Source
```bash
git clone <repository>
cd mp/kernels/b10-kernel
pip install -e .
```

## Development guide
- Build the library from source
```bash
make build
make rebuild
```
- Run unit tests
```bash
make test
```
- Format code
```bash
make format
```

## Kernel Development Workflow
Steps to add a new kernel:
- Implement the kernel in `csrc`
- Expose the interface in `include/b10_kernel_ops.h`
- Create torch extension in `csrc/common_extension.cc`
- Update `CMakeLists.txt` to include new CUDA source
- Expose Python interface in `python/b10_kernel/xxx.py` and `python/b10_kernel/__init__.py`
- Add unit test for the kernel in `test/test_xxx.py`
- Add benchmark script for the kernel in `benchmark/bench_xxx.py`
- Format code with `make format`

