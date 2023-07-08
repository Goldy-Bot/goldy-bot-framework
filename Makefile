run:
	cd demo && python run.py

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

update-pip:
	python -m pip install --upgrade pip