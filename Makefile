PYTHON ?= python3.12

install:
	$(PYTHON) -m pip install -U pip
	$(PYTHON) -m pip install -e .[dev]

test:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m mypy deploy_guard
	$(PYTHON) -m pytest -q

demo:
	$(PYTHON) -m deploy_guard scan --path demo --format md --no-llm

docker-build:
	docker build -t deploy-guard:local .

docker-run-demo:
	docker run --rm -v $(PWD):/app deploy-guard:local scan --path /app/demo --format md --no-llm
