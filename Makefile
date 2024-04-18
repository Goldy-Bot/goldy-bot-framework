.PHONY: build

pip = pip
python = python

build:
	${python} -m build

install:
	${pip} install . -U

install-dev:
	${pip} install .[dev] -U

install-editable:
	${pip} install -e . --config-settings editable_mode=compat

test:
	ruff check .
	cd tests && pytest -v

test-v:
	cd tests && pytest -vv

docker-build:
	${python} scripts/docker_build.py

build-clean-docs:
	cd docs && make clean && make html

build-docs:
	cd docs && make html

pull-submodules:
	git submodule update --init --recursive

pip-update:
	${python} -m pip install --upgrade pip