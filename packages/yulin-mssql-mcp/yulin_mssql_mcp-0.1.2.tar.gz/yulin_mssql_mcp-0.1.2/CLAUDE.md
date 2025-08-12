# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server for Microsoft SQL Server, enabling secure database interactions through Claude Desktop. The project uses pymssql for database connectivity and supports multiple authentication methods (SQL, Windows, Azure AD).

## Key Architecture

### Core Components
- `src/yulin_mssql_mcp/server.py`: Main MCP server implementation with SQL query execution and table listing capabilities
- Database connection management with support for LocalDB, Azure SQL, and custom ports
- SQL injection prevention through parameterized queries and table name validation

### MCP Tools Exposed
- `query-database`: Execute SQL queries with parameterization support
- `list-tables`: List available database tables

## Common Development Commands

### Setup and Installation
```bash
# Create virtual environment and install dependencies
make install-dev

# Or manually:
python -m venv venv
./venv/bin/pip install -r requirements.txt -r requirements-dev.txt
./venv/bin/pip install -e .
```

### Running Tests
```bash
# Run all tests
make test

# Run specific test categories
./venv/bin/pytest tests/test_server.py -v  # Unit tests
./venv/bin/pytest tests/test_integration.py -v  # Integration tests
./venv/bin/pytest tests/test_security.py -v  # Security tests

# Run with coverage
./venv/bin/pytest --cov=src/yulin_mssql_mcp --cov-report=html

# Test database connection
make test-connection
```

### Code Quality
```bash
# Format code
make format

# Run linters
make lint

# Individual tools:
./venv/bin/black src tests
./venv/bin/isort src tests
./venv/bin/mypy src tests
./venv/bin/ruff check src tests
```

### Running the Server
```bash
# Run directly
make run

# Or with environment variables:
export MSSQL_SERVER=localhost
export MSSQL_DATABASE=your_database
export MSSQL_USER=your_username
export MSSQL_PASSWORD=your_password
./venv/bin/python -m yulin_mssql_mcp
```

## Environment Configuration

Required environment variables:
- `MSSQL_SERVER`: Database server (supports LocalDB format: `(localdb)\MSSQLLocalDB`)
- `MSSQL_DATABASE`: Target database name
- `MSSQL_USER`: Username (not required for Windows auth)
- `MSSQL_PASSWORD`: Password (not required for Windows auth)

Optional:
- `MSSQL_PORT`: Custom port (default: 1433)
- `MSSQL_WINDOWS_AUTH`: Set to "true" for Windows authentication
- `MSSQL_ENCRYPT`: Force encryption

## Testing Infrastructure

The project includes comprehensive test suites:
- Unit tests: Basic functionality testing
- Integration tests: Database connection and query execution
- Security tests: SQL injection prevention and authentication
- Performance tests: Query execution benchmarks

Tests use pytest with asyncio support. Docker Compose is available for isolated testing environments.

## Package Structure

- Package name on PyPI: `yulin-mssql-mcp`
- Python module name: `yulin_mssql_mcp`
- Entry point script: `yulin-mssql-mcp`

## Security Considerations

- All SQL queries use parameterization to prevent injection
- Table names are validated with regex patterns
- Connection strings sanitize passwords in logs
- Support for encrypted connections to Azure SQL