.PHONY: run-api
.ONESHELL:
run-api:
	python -m src.api


.PHONY: run-callback-server
.ONESHELL:
run-callback-server:
	python -m tests.utils.servers.callback


.PHONY: run-callback-delivery-processor
.ONESHELL:
run-callback-delivery-processor:
	python -m src.processors.callback_delivery


.PHONY: run-callback-spreader-processor
.ONESHELL:
run-callback-spreader-processor:
	python -m src.processors.callback_spreader


.PHONY: run-new-messages-observer-processor
.ONESHELL:
run-new-messages-observer-processor:
	python -m src.processors.new_messages_observer


.PHONY: test
.ONESHELL:
test:
	pytest tests -vv -x -c pytest.ini


.PHONY: coverage
.ONESHELL:
coverage:
	coverage run -m tests
	coverage report -m
	coverage html


.PHONY: lint
.ONESHELL:
lint:
	flake8 --exit-zero --config=.flake8 src tests
