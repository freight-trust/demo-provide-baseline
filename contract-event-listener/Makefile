.PHONY: run
.ONESHELL:
run:
	python -m src.worker

.PHONY: run-debug
.ONESHELL:
run-debug:
	DEBUG=True python -m src.worker


.PHONY: test
.ONESHELL:
test:
	@ pytest tests -vv -x -c pytest.ini


.PHONY: coverage
.ONESHELL:
coverage:
		coverage run -m tests
		coverage report -m
		coverage html


.PHONY: lint
.ONESHELL:
lint:
	@ PYTHONDONTWRITEBYTECODE=1 flake8 --exit-zero --config=.flake8 src tests
