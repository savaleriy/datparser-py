# Makefile for datparser project

.PHONY: clean test update build install all

# Remove built artifacts and cached files (dist, build, egg-info, and Python __pycache__ directories)
clean:
	@echo "Cleaning build artifacts and __pycache__ directories..."
	@rm -rf build dist *.egg-info
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type d -name "*.c" -exec rm {} +

# Run the tests using poetry (update the pytest command options as needed)
test:
	@echo "Running tests with pytest..."
	@poetry run pytest --maxfail=1 --disable-warnings -q

# Update all libraries via poetry
update:
	@echo "Updating libraries using poetry..."
	@poetry update

# Build the package (wheel and sdist will be in the dist/ directory)
build:
	@echo "Building package..."
	@poetry build

# Optionally, install the built package from the wheel file
install:
	@echo "Installing package..."
	@pip install dist/*.whl

# The "all" target will clean artifacts, update libraries, build the package, and run tests sequentially.
all: clean update build test

