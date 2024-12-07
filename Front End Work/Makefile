install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

test:
	python -m pytest -vv --cov=main --cov=mylib test_*.py

format:	
	black *.py 

lint:

	ruff check *.py --fix *.py

container-lint:
	docker run --rm -i hadolint/hadolint < Dockerfile

refactor: format lint

test:
	python -m pytest -vv --cov=main --cov=mylib

deploy:
	#deploy goes here
		
all: install lint test format deploy