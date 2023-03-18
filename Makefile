run:
	cd env/Scripts && activate && cd ../../
	cd demo && python run.py

test:
	cd tests
	pytest

docker-build:
	docker build -t devgoldy/goldybot .

docker-compose:
	docker compose --env-file ./demo/.env up