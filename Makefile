.PHONY: install lint format test validate run leaderboard

install:
	pip install -e ".[dev]"

lint:
	ruff check src tests
	ruff format --check src tests

format:
	ruff format src tests
	ruff check --fix src tests

test:
	pytest

validate:
	pashtobench validate data

run:
	pashtobench --help

leaderboard:
	@echo "leaderboard arrives in sprint 2"
