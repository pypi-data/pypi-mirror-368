import asyncio
import logging
import os
import re
import sys

import pymssql
from mcp.server import Server
from mcp.types import Resource, TextContent, Tool
from pydantic import AnyUrl

# Configure logging - MUST output to stderr for MCP stdio transport
# Debug mode can be enabled via MCP_DEBUG environment variable
debug_mode = os.getenv("MCP_DEBUG", "0") == "1"
log_level = logging.DEBUG if debug_mode else logging.INFO

logging.basicConfig(
    stream=sys.stderr,  # Explicitly output to stderr, not stdout
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("mssql_mcp_server")

if debug_mode:
    logger.debug("Debug mode enabled via MCP_DEBUG environment variable")


def validate_table_name(table_name: str) -> str:
    """Validate and escape table name to prevent SQL injection."""
    # Allow only alphanumeric, underscore, and dot (for schema.table)
    if not re.match(r"^[a-zA-Z0-9_]+(\.[a-zA-Z0-9_]+)?$", table_name):
        raise ValueError(f"Invalid table name: {table_name}")

    # Split schema and table if present
    parts = table_name.split(".")
    if len(parts) == 2:
        # Escape both schema and table name
        return f"[{parts[0]}].[{parts[1]}]"
    else:
        # Just table name
        return f"[{table_name}]"


def get_db_config():
    """Get database configuration from environment variables."""
    # Basic configuration
    server = os.getenv("MSSQL_SERVER", "localhost")
    logger.info(
        f"MSSQL_SERVER environment variable: {os.getenv('MSSQL_SERVER', 'NOT SET')}"
    )
    logger.info(f"Using server: {server}")

    # Handle LocalDB connections (Issue #6)
    # LocalDB format: (localdb)\instancename
    if server.startswith("(localdb)\\"):
        # For LocalDB, pymssql needs special formatting
        # Convert (localdb)\MSSQLLocalDB to localhost\MSSQLLocalDB with dynamic port
        instance_name = server.replace("(localdb)\\", "")
        server = f".\\{instance_name}"
        logger.info(f"Detected LocalDB connection, converted to: {server}")

    config = {
        "server": server,
        "user": os.getenv("MSSQL_USER"),
        "password": os.getenv("MSSQL_PASSWORD"),
        "database": os.getenv("MSSQL_DATABASE"),
        "port": os.getenv("MSSQL_PORT", "1433"),  # Default MSSQL port
    }
    # Port support (Issue #8)
    port = os.getenv("MSSQL_PORT")
    if port:
        try:
            config["port"] = int(port)
        except ValueError:
            logger.warning(f"Invalid MSSQL_PORT value: {port}. Using default port.")

    # TDS version settings for Azure SQL (Issue #11)
    # Check if we're connecting to Azure SQL
    if config["server"] and ".database.windows.net" in config["server"]:
        config["tds_version"] = "7.4"  # Required for Azure SQL
        logger.info("Detected Azure SQL connection, using TDS version 7.4")

    # Note: pymssql doesn't support encrypt parameter directly
    # For encryption, you need to configure it at the server level or use other drivers

    # Windows Authentication support (Issue #7)
    use_windows_auth = os.getenv("MSSQL_WINDOWS_AUTH", "false").lower() == "true"

    if use_windows_auth:
        # For Windows authentication, user and password are not required
        if not config["database"]:
            logger.error("MSSQL_DATABASE is required")
            raise ValueError("Missing required database configuration")
        # Remove user and password for Windows auth
        config.pop("user", None)
        config.pop("password", None)
        logger.info("Using Windows Authentication")
    else:
        # SQL Authentication - user and password are required
        if not all([config["user"], config["password"], config["database"]]):
            logger.error(
                "Missing required database configuration. Please check environment variables:"
            )
            logger.error("MSSQL_USER, MSSQL_PASSWORD, and MSSQL_DATABASE are required")
            raise ValueError("Missing required database configuration")

    return config


def get_command():
    """Get the command to execute SQL queries."""
    return os.getenv("MSSQL_COMMAND", "execute_sql")


# Initialize server
app = Server("mssql_mcp_server")


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List SQL Server tables as resources."""
    config = get_db_config()
    try:
        conn = pymssql.connect(**config)
        cursor = conn.cursor()
        # Query to get user tables from the current database
        cursor.execute(
            """
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
        """
        )
        tables = cursor.fetchall()
        logger.info(f"Found tables: {tables}")

        resources = []
        for table in tables:
            resources.append(
                Resource(
                    uri=f"mssql://{table[0]}/data",
                    name=f"Table: {table[0]}",
                    mimeType="text/plain",
                    description=f"Data in table: {table[0]}",
                )
            )
        cursor.close()
        conn.close()
        return resources
    except Exception as e:
        logger.error(f"Failed to list resources: {str(e)}")
        return []


@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """Read table contents."""
    config = get_db_config()
    uri_str = str(uri)
    logger.info(f"Reading resource: {uri_str}")

    if not uri_str.startswith("mssql://"):
        raise ValueError(f"Invalid URI scheme: {uri_str}")

    parts = uri_str[8:].split("/")
    table = parts[0]

    try:
        # Validate table name to prevent SQL injection
        safe_table = validate_table_name(table)

        conn = pymssql.connect(**config)
        cursor = conn.cursor()
        # Use TOP 100 for MSSQL (equivalent to LIMIT in MySQL)
        cursor.execute(f"SELECT TOP 100 * FROM {safe_table}")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        result = [",".join(map(str, row)) for row in rows]
        cursor.close()
        conn.close()
        return "\n".join([",".join(columns)] + result)

    except Exception as e:
        logger.error(f"Database error reading resource {uri}: {str(e)}")
        raise RuntimeError(f"Database error: {str(e)}")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available SQL Server tools."""
    command = get_command()
    logger.info("Listing tools...")
    logger.debug("→ Received request: tools/list")
    return [
        Tool(
            name=command,
            description="Execute an SQL query on the SQL Server",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The SQL query to execute",
                    }
                },
                "required": ["query"],
            },
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute SQL commands."""
    config = get_db_config()
    command = get_command()
    logger.info(f"Calling tool: {name} with arguments: {arguments}")
    logger.debug(f"→ Received request: tools/call {name}")

    if name != command:
        raise ValueError(f"Unknown tool: {name}")

    query = arguments.get("query")
    if not query:
        raise ValueError("Query is required")

    conn = None
    cursor = None
    try:
        conn = pymssql.connect(**config)
        cursor = conn.cursor()
        cursor.execute(query)

        # Check if the query returned a result set by examining cursor.description
        # cursor.description is None for queries that don't return data (INSERT, UPDATE, DELETE, etc.)
        if cursor.description is not None:
            # This query returns data (SELECT, WITH, stored procedures that return data, etc.)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            # Handle empty result set
            if not rows:
                return [
                    TextContent(
                        type="text",
                        text=f"Query returned 0 rows.\nColumns: {', '.join(columns)}",
                    )
                ]

            # Format results as CSV-like output
            result = [",".join(columns)]  # Header row
            for row in rows:
                # Handle NULL values and convert all values to strings
                row_values = []
                for value in row:
                    if value is None:
                        row_values.append("NULL")
                    else:
                        row_values.append(str(value))
                result.append(",".join(row_values))

            result_text = "\n".join(result)
            logger.debug(f"← Sending response: {len(rows)} rows returned")
            return [TextContent(type="text", text=result_text)]
        else:
            # This is a query that doesn't return data (INSERT, UPDATE, DELETE, DDL, etc.)
            # Commit the transaction for DML operations
            conn.commit()
            affected_rows = cursor.rowcount

            # Provide more informative message based on affected rows
            if affected_rows == -1:
                # Some operations don't report affected rows (like DDL statements)
                logger.debug("← Sending response: Query executed (DDL statement)")
                return [TextContent(type="text", text="Query executed successfully.")]
            else:
                logger.debug(f"← Sending response: {affected_rows} rows affected")
                return [
                    TextContent(
                        type="text",
                        text=f"Query executed successfully. Rows affected: {affected_rows}",
                    )
                ]

    except pymssql.DatabaseError as e:
        logger.error(f"Database error executing SQL '{query}': {e}")
        # Rollback transaction on error
        if conn:
            conn.rollback()
        return [TextContent(type="text", text=f"Database error: {str(e)}")]
    except Exception as e:
        logger.error(f"Unexpected error executing SQL '{query}': {e}")
        return [TextContent(type="text", text=f"Error executing query: {str(e)}")]
    finally:
        # Ensure resources are properly cleaned up
        if cursor:
            cursor.close()
        if conn:
            conn.close()


async def main():
    """Main entry point to run the MCP server."""
    from mcp.server.stdio import stdio_server

    logger.info("Starting MSSQL MCP server...")
    config = get_db_config()
    # Log connection info without exposing sensitive data
    server_info = config["server"]
    if "port" in config:
        server_info += f":{config['port']}"
    user_info = config.get("user", "Windows Auth")
    logger.info(f"Database config: {server_info}/{config['database']} as {user_info}")

    async with stdio_server() as (read_stream, write_stream):
        try:
            await app.run(
                read_stream, write_stream, app.create_initialization_options()
            )
        except Exception as e:
            logger.error(f"Server error: {str(e)}", exc_info=True)
            raise


if __name__ == "__main__":
    asyncio.run(main())
