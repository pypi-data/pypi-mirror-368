.PHONY: help install-deps submodule install build clean rebuild test check-deps format 

export CMAKE_PREFIX_PATH=$(python -c "import torch; print(torch.utils.cmake_prefix_path)")

# Show help for each target
help:
	@echo "Available targets:"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup:
	@[ -d .venv ] || uv venv .venv

install-deps: setup
	uv pip install scikit-build-core ruff

submodule:
	@git submodule update --init --recursive

install: submodule
	@uv pip install -e .

# Build and install the wheel package
build: install-deps submodule
	@rm -rf dist/* || true && export MAX_JOBS=$(nproc) && CMAKE_POLICY_VERSION_MINIMUM=3.5 CMAKE_BUILD_PARALLEL_LEVEL=$(nproc) uv build --wheel -Cbuild-dir=build . --verbose --color=always --no-build-isolation && pip3 install dist/*whl --force-reinstall --no-deps

clean:
	@rm -rf build dist *.egg-info

rebuild: clean submodule build
	@echo "Succeed to rebuild"

# Run all unit tests
test:
	@find test -name "test_*.py" | xargs -n 1 python3

check-deps:
	@command -v ruff >/dev/null 2>&1 || (echo "Installing ruff..." && uv pip install ruff)

bench:
	uv pip install matplotlib pandas && uv run python3 benchmark/bench_norm.py

# Format all source files
format: check-deps 
	@echo "Formatting source files..."
	@find csrc -name '*.cc' -o -name '*.cu' -o -name '*.cuh' -o -name '*.h' -o -name '*.hpp' | xargs clang-format -i
	@ruff format && ruff check --fix .