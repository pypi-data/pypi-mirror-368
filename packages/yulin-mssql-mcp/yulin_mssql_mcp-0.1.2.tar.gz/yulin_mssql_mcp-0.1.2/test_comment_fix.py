#!/usr/bin/env python3
"""Test the fixed SQL query handling with comments"""

import os
import sys
import asyncio
import json

# Add src to path to import our server module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Test queries
test_queries = [
    {
        "name": "Simple SELECT",
        "query": "SELECT TOP 3 name FROM sys.tables"
    },
    {
        "name": "SELECT with single-line comment",
        "query": "-- Get system tables\nSELECT TOP 3 name FROM sys.tables"
    },
    {
        "name": "SELECT with multi-line comment", 
        "query": "/* This is a\n   multi-line comment */\nSELECT TOP 3 name FROM sys.tables"
    },
    {
        "name": "Complex query with Chinese comment",
        "query": """-- 查詢 PPDistribution 相關資料表結構
SELECT TOP 5 
    t.TABLE_NAME,
    t.TABLE_TYPE
FROM INFORMATION_SCHEMA.TABLES t
WHERE t.TABLE_NAME LIKE '%sys%'
ORDER BY t.TABLE_NAME;"""
    },
    {
        "name": "INSERT statement",
        "query": "-- This won't actually insert\nSELECT 'This is actually a SELECT, not INSERT' as test_column"
    }
]

async def test_query(query_info):
    """Test a single query using the MCP server"""
    from yulin_mssql_mcp.server import app, call_tool
    
    print(f"\n{'='*60}")
    print(f"Testing: {query_info['name']}")
    print(f"Query:\n{query_info['query']}")
    print("-" * 60)
    
    try:
        result = await call_tool("execute_sql", {"query": query_info["query"]})
        if result:
            print("Result:")
            print(result[0].text)
        else:
            print("No result returned")
    except Exception as e:
        print(f"Error: {e}")

async def main():
    """Run all tests"""
    from yulin_mssql_mcp.server import get_db_config
    
    try:
        config = get_db_config()
        print("Testing SQL query handling with comments")
        print(f"Database: {config.get('database', 'Not set')}")
        
        for query_info in test_queries:
            await test_query(query_info)
        
        print(f"\n{'='*60}")
        print("All tests completed!")
    except Exception as e:
        print(f"Failed to get database configuration: {e}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())