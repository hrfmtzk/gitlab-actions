SRC_DIR := src
TEST_DIR := tests

full-test: test-coding test-unittest test-quality

test-coding: pep8 typing format

pep8:
	poetry run flake8 ${SRC_DIR} ${TEST_DIR}

typing:
	poetry run mypy $(SRC_DIR) ${TEST_DIR}

format:
	poetry run black --check $(SRC_DIR) ${TEST_DIR}
	poetry run isort --check $(SRC_DIR) ${TEST_DIR}

test-unittest: unittest

unittest:
	poetry run pytest -v --cov=$(SRC_DIR) --cov-report=term-missing

test-quality: security complexity

security:
	poetry run bandit -r ${SRC_DIR}

complexity:
	poetry run xenon --max-absolute B --max-modules A --max-average A ${SRC_DIR} ${TEST_DIR}
