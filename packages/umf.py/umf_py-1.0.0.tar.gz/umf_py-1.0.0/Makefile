.PHONY: test install dev-install clean build upload help setup

help:
	@echo "Available commands:"
	@echo "  setup       - Install build dependencies"
	@echo "  test        - Run tests"
	@echo "  install     - Install the package"
	@echo "  dev-install - Install the package in development mode"
	@echo "  clean       - Clean build artifacts"
	@echo "  build       - Build the package (requires setup first)"
	@echo "  upload      - Upload to PyPI (requires setup first)"

setup:
	pip install build twine

test:
	python3 -m unittest tests.test_umf -v

install:
	pip install .

dev-install:
	pip install -e .

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf src/*.egg-info/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: clean
	python3 -m build

upload: build
	python3 -m twine upload dist/*
