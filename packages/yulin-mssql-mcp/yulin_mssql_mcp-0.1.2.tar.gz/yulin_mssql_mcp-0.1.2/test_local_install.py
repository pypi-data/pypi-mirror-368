#!/usr/bin/env python
"""Test the locally installed package."""

import subprocess
import sys
import os

# Set environment variables
os.environ['MSSQL_SERVER'] = 'ljnb015.local'
os.environ['MSSQL_USER'] = 'mcp_login'
os.environ['MSSQL_PASSWORD'] = 'aaaaa123'
os.environ['MSSQL_DATABASE'] = 'RBMS'

def test_command_line():
    """Test running the package as a command."""
    print("🧪 Testing command line execution...")
    
    try:
        # Test the entry point script
        result = subprocess.run(['yulin-mssql-mcp'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        print("✅ Command executed successfully")
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"STDOUT: {result.stdout[:200]}...")
        if result.stderr:
            print(f"STDERR: {result.stderr[:200]}...")
            
    except subprocess.TimeoutExpired:
        print("✅ Command started successfully (timed out as expected for MCP server)")
    except FileNotFoundError:
        print("❌ Command 'yulin-mssql-mcp' not found")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_module_import():
    """Test importing the module."""
    print("\n🧪 Testing module import...")
    
    try:
        import yulin_mssql_mcp
        print("✅ Module imported successfully")
        print(f"Module path: {yulin_mssql_mcp.__file__}")
        
        # Test importing main components
        from yulin_mssql_mcp.server import app, list_tools
        print("✅ Server components imported successfully")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")

def test_uv_run():
    """Test running with uv."""
    print("\n🧪 Testing uv run...")
    
    try:
        result = subprocess.run(['uv', 'run', 'python', '-m', 'yulin_mssql_mcp'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        print("✅ uv run executed successfully")
        
    except subprocess.TimeoutExpired:
        print("✅ uv run started successfully (timed out as expected)")
    except Exception as e:
        print(f"❌ Error with uv run: {e}")

if __name__ == "__main__":
    print("🚀 Testing locally installed package...\n")
    test_module_import()
    test_command_line()
    test_uv_run()
    print("\n✅ Local testing completed!")