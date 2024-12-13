install:
	pip install --upgrade pip && pip install -r requirements.txt

format:
	black *.py

lint:
	# pylint --disable=R,C --ignore-patterns=test_.*?py *.py
	ruff check *.py test_*.py

test:
	python -m pytest -vv -cov=main test_*.py

container-lint:
	docker run --rm -i hadolint/hadolint < Dockerfile

refactor: format lint


all: install format lint test container-lint refactor generate_and_push