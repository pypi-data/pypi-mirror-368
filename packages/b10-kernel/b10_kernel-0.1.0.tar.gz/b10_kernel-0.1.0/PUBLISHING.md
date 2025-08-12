# Publishing b10-kernel to PyPI

This guide covers how to publish the `b10-kernel` package to PyPI. Since this package contains CUDA kernels, it requires a CUDA-enabled environment for building.

## Prerequisites

### 1. PyPI Account Setup
- Create an account at [pypi.org](https://pypi.org/account/register/)
- Set up API tokens:
  - Go to [Account Settings](https://pypi.org/manage/account/#api-tokens)
  - Create a new API token with appropriate scope
  - Save the token securely (format: `pypi-<token>`)

### 2. CUDA Environment
Since this package contains CUDA code, you need:
- NVIDIA GPU with CUDA support
- CUDA Toolkit (12.1+ recommended)
- PyTorch with CUDA support
- Linux environment (recommended)

## Build Environment Setup

```bash
# Install build dependencies
pip install --upgrade build twine

# Navigate to the package directory
cd /path/to/baseten/mp/kernels/b10-kernel

# Verify CUDA is available
nvidia-smi
nvcc --version
```

## Build the Package
```bash
# Clean previous builds
make clean

# Build wheel and source distribution
python -m build

# This creates:
# - dist/b10_kernel-0.1.0-py312-py312-linux_x86_64.whl
# - dist/b10-kernel-0.1.0.tar.gz
```

## 3. Test the Build
```bash
# Install the built wheel locally
pip install dist/b10_kernel-*.whl

# Test basic import
python -c "import b10_kernel; print(b10_kernel.__version__)"
```

### 4. Upload to Test PyPI (Recommended First Step)
```bash
# Configure TestPyPI credentials
pip install --upgrade twine

# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ b10-kernel
```

### 5. Upload to PyPI
```bash
# Configure PyPI credentials (use API token)
twine upload dist/*

# Or specify credentials explicitly
twine upload --username __token__ --password pypi-<your-token> dist/*
```
