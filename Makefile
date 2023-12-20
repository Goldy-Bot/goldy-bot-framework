build:
	python -m build

install:
	pip install . -U

install-dev:
	pip install . -U

install-editable:
	pip install -e . --config-settings editable_mode=compat

test:
	ruff .
	cd tests && pytest -v

test-v:
	cd tests && pytest -vv

docker-build:
	python scripts/docker_build.py

docker-compose:
	docker compose --env-file ./demo/.env up

build-clean-docs:
	cd docs && make clean && make html

build-docs:
	cd docs && make html

pull-submodules:
	git submodule update --init --recursive

pip-update:
	python -m pip install --upgrade pip