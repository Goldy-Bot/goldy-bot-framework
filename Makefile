run:
	cd env/Scripts
	activate
	cd ../../
	cd demo && python run.py

create-env:
	python -m venv env
	cd env/Scripts
	activate
	cd ../../
	pip install .

test:
	cd tests
	pytest