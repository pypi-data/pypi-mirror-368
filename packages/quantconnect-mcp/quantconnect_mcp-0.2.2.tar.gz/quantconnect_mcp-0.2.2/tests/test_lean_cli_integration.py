#!/usr/bin/env python3
"""Test the lean-cli based QuantBook integration."""

import asyncio
import os
import sys
from pathlib import Path

# Add the package to the path
sys.path.insert(0, str(Path(__file__).parent))

from quantconnect_mcp.src.adapters.research_session_lean_cli import ResearchSession


async def test_lean_cli_integration():
    """Test the lean-cli based research session."""
    print("Testing lean-cli integration for QuantBook...")
    
    # Check environment variables
    print("\nEnvironment check:")
    for var in ["QUANTCONNECT_USER_ID", "QUANTCONNECT_API_TOKEN", "QUANTCONNECT_ORGANIZATION_ID"]:
        value = os.environ.get(var, "NOT SET")
        print(f"  {var}: {'SET' if value != 'NOT SET' else 'NOT SET'}")
    
    session = ResearchSession(
        session_id="test_lean_cli",
        port=8890  # Different port to avoid conflicts
    )
    
    try:
        print(f"\nInitializing session on port {session.port}...")
        await session.initialize()
        print("✓ Session initialized successfully!")
        
        print(f"\nJupyter Lab should be accessible at: http://localhost:{session.port}")
        
        # Test code execution
        print("\nTesting code execution...")
        test_code = """
print("Hello from lean-cli managed container!")
import sys
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
"""
        
        result = await session.execute(test_code)
        print(f"Execution result: {result['status']}")
        if result['output']:
            print("Output:")
            print(result['output'])
        if result.get('error'):
            print("Error:")
            print(result['error'])
        
        print("\nContainer is running. Press Ctrl+C to stop...")
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        print("\n\nStopping session...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await session.close()
        print("Session closed.")


if __name__ == "__main__":
    asyncio.run(test_lean_cli_integration())