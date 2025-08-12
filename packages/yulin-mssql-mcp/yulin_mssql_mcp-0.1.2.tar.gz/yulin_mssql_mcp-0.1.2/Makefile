.PHONY: install install-dev test lint format clean run docker-build docker-up docker-down docker-test docker-exec

install:
	uv pip install -r requirements.txt

install-dev:
	uv pip install -r requirements-dev.txt
	uv pip install -e .

test: install-dev
	uv run pytest -v

lint: install-dev
	uv run black --check src tests
	uv run isort --check src tests
	uv run mypy src tests

format: install-dev
	uv run black src tests
	uv run isort src tests

clean:
	rm -rf .venv __pycache__ .pytest_cache .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run: install
	uv run python -m yulin_mssql_mcp

# Docker commands
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-test:
	docker-compose exec mcp_server pytest -v

docker-exec:
	docker-compose exec mcp_server bash

# Test MSSQL connection
test-connection:
	$(PYTHON) test_connection.py --server $${MSSQL_SERVER:-localhost} --port $${HOST_SQL_PORT:-1434} --user $${MSSQL_USER:-sa} --password $${MSSQL_PASSWORD:-StrongPassword123!} --database $${MSSQL_DATABASE:-master}

# Set environment variables for testing
test-env:
	@echo "Export your database credentials before running tests:"
	@echo "export MSSQL_SERVER=your_server"
	@echo "export MSSQL_PORT=1433"
	@echo "export MSSQL_USER=your_username"
	@echo "export MSSQL_PASSWORD=your_password"
	@echo "export MSSQL_DATABASE=your_database"