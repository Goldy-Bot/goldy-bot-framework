.PHONY: build

PIP = pip
PYTHON = python

build:
	${PYTHON} -m build

install:
	${PIP} install . -U

install-dev:
	${PIP} install .[dev] -U

install-editable:
	${PIP} install -e .[dev] --config-settings editable_mode=compat

test:
	ruff check .
	cd tests && pytest -v

test-v:
	cd tests && pytest -vv

docker-build:
	${PYTHON} scripts/docker_build.py

build-clean-docs:
	cd docs && make clean && make html

build-docs:
	cd docs && make html

pull-submodules:
	git submodule update --init --recursive

pip-update:
	${PYTHON} -m pip install --upgrade pip