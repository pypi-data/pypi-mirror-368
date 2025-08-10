#!/usr/bin/env python3
"""
Test script to verify Jupyter port configuration works properly.
"""

import os
import sys
from pathlib import Path

# Add the source directory to the path
sys.path.insert(0, str(Path(__file__).parent / "quantconnect_mcp" / "src"))

from adapters.research_session import ResearchSession

def test_port_configuration():
    """Test different port configuration methods."""
    print("Testing Jupyter Port Configuration")
    print("=" * 50)
    
    # Test 1: Default port (8888)
    print("\n1. Testing default port (8888)...")
    session1 = ResearchSession(session_id="test_default_port")
    print(f"   Port: {session1.port}")
    assert session1.port == 8888
    print("   ✓ Default port test passed")
    
    # Test 2: Environment variable
    print("\n2. Testing environment variable...")
    os.environ["QUANTBOOK_DOCKER_PORT"] = "9999"
    session2 = ResearchSession(session_id="test_env_port")
    print(f"   Port: {session2.port}")
    assert session2.port == 9999
    print("   ✓ Environment variable test passed")
    
    # Test 3: Direct parameter (overrides env var)
    print("\n3. Testing direct parameter...")
    session3 = ResearchSession(session_id="test_param_port", port=7777)
    print(f"   Port: {session3.port}")
    assert session3.port == 7777
    print("   ✓ Direct parameter test passed")
    
    # Clean up env var
    del os.environ["QUANTBOOK_DOCKER_PORT"]
    
    print("\n✅ All port configuration tests passed!")
    print("\nPort priority: parameter > env var > default (8888)")

if __name__ == "__main__":
    test_port_configuration()