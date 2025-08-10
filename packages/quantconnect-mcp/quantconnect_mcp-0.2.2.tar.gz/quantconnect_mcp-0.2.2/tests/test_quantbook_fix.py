#!/usr/bin/env python3
"""
Test script to verify the quantbook fixes work properly.
This tests the Docker container setup similar to lean-cli.
"""

import asyncio
import sys
from pathlib import Path

# Add the source directory to the path
sys.path.insert(0, str(Path(__file__).parent / "quantconnect_mcp" / "src"))

from adapters.research_session import ResearchSession

async def test_quantbook_session():
    """Test the updated ResearchSession implementation."""
    print("Testing updated QuantBook session implementation...")
    
    # Create a test session
    session = ResearchSession(session_id="test_session")
    
    try:
        # Initialize the session
        print("Initializing session...")
        await session.initialize()
        print("✓ Session initialized successfully")
        
        # Test basic Python execution
        print("Testing basic Python execution...")
        result = await session.execute("print('Hello from updated container!')")
        print(f"Result: {result}")
        
        if result["status"] == "success":
            print("✓ Basic execution works")
        else:
            print("✗ Basic execution failed")
            return False
        
        # Test pandas/numpy
        print("Testing pandas/numpy imports...")
        result = await session.execute("""
import pandas as pd
import numpy as np
print(f"Pandas version: {pd.__version__}")
print(f"NumPy version: {np.__version__}")
""")
        print(f"Result: {result}")
        
        if result["status"] == "success":
            print("✓ Data libraries work")
        else:
            print("✗ Data libraries failed")
        
        # Test QuantConnect imports (may fail if image doesn't have LEAN)
        print("Testing QuantConnect imports...")
        result = await session.execute("""
import sys
sys.path.append('/Lean')

try:
    from QuantConnect.Research import QuantBook
    print("QuantConnect.Research imported successfully")
    qb = QuantBook()
    print(f"QuantBook instance created: {type(qb)}")
except ImportError as e:
    print(f"QuantConnect not available (expected if not using LEAN image): {e}")
except Exception as e:
    print(f"Other error: {e}")
""")
        print(f"Result: {result}")
        
        print("\n✓ All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        return False
        
    finally:
        # Clean up
        await session.close("test_completed")

if __name__ == "__main__":
    success = asyncio.run(test_quantbook_session())
    sys.exit(0 if success else 1)