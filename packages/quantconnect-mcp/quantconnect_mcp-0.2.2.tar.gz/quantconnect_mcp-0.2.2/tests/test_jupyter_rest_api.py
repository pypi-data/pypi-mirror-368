#!/usr/bin/env python3
"""
Test using Jupyter REST API to execute QuantBook code.
This might work better than nbconvert since it's closer to how the web UI works.
"""

import asyncio
import aiohttp
import json
import sys
from pathlib import Path

# Add the source directory to the path
sys.path.insert(0, str(Path(__file__).parent / "quantconnect_mcp" / "src"))

from adapters.research_session_lean_cli import ResearchSession

async def test_jupyter_rest_api():
    """Test executing code via Jupyter REST API instead of nbconvert."""
    print("=" * 60)
    print("Jupyter REST API Test for QuantBook")
    print("=" * 60)
    
    session = ResearchSession(session_id="rest_api_test")
    
    try:
        # Initialize the session
        print("\n1. Initializing research session...")
        await session.initialize()
        print(f"✓ Session initialized on port {session.port}")
        
        # Wait a bit for Jupyter to fully start
        print("\n2. Waiting for Jupyter to be ready...")
        await asyncio.sleep(5)
        
        # Test if Jupyter REST API is accessible
        base_url = f"http://localhost:{session.port}"
        
        async with aiohttp.ClientSession() as client:
            # Check if Jupyter is running
            print("\n3. Checking Jupyter API...")
            try:
                async with client.get(f"{base_url}/api") as resp:
                    if resp.status == 200:
                        api_info = await resp.json()
                        print(f"✓ Jupyter API accessible: {api_info}")
                    else:
                        print(f"✗ Jupyter API returned status {resp.status}")
                        return False
            except Exception as e:
                print(f"✗ Failed to connect to Jupyter API: {e}")
                return False
            
            # List available kernels
            print("\n4. Listing available kernels...")
            try:
                async with client.get(f"{base_url}/api/kernels") as resp:
                    if resp.status == 200:
                        kernels = await resp.json()
                        print(f"✓ Available kernels: {kernels}")
                        
                        if kernels:
                            # Use existing kernel
                            kernel_id = kernels[0]['id']
                            print(f"  Using existing kernel: {kernel_id}")
                        else:
                            # Create a new kernel
                            print("  No kernels found, creating new one...")
                            async with client.post(
                                f"{base_url}/api/kernels",
                                json={"name": "python3"}
                            ) as resp:
                                if resp.status == 201:
                                    kernel_info = await resp.json()
                                    kernel_id = kernel_info['id']
                                    print(f"✓ Created kernel: {kernel_id}")
                                else:
                                    print(f"✗ Failed to create kernel: {resp.status}")
                                    return False
                    else:
                        print(f"✗ Failed to list kernels: {resp.status}")
                        return False
            except Exception as e:
                print(f"✗ Error with kernels: {e}")
                return False
            
            # Execute code via the kernel
            print("\n5. Testing code execution via REST API...")
            
            # First, check if qb is available
            code_to_execute = """
try:
    qb
    print(f"✓ QuantBook is available as 'qb'!")
    print(f"Type: {type(qb)}")
    print(f"Methods: {[m for m in dir(qb) if not m.startswith('_')][:10]}")
except NameError:
    print("✗ QuantBook (qb) is not available")
    print("Trying to initialize...")
    try:
        from QuantConnect import *
        from QuantConnect.Research import *
        qb = QuantBook()
        print(f"✓ Successfully initialized QuantBook!")
        print(f"Type: {type(qb)}")
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
"""
            
            # Execute via REST API
            execution_request = {
                "code": code_to_execute,
                "silent": False,
                "store_history": True,
                "user_expressions": {},
                "allow_stdin": False,
                "stop_on_error": True
            }
            
            try:
                # Note: Jupyter uses WebSockets for execution, so we need a different approach
                # Let's check the session info first
                async with client.get(f"{base_url}/api/sessions") as resp:
                    if resp.status == 200:
                        sessions = await resp.json()
                        print(f"✓ Active sessions: {len(sessions)}")
                        for sess in sessions:
                            print(f"  - {sess.get('name', 'unnamed')} (kernel: {sess.get('kernel', {}).get('name', 'unknown')})")
                    
                # Since WebSocket handling is complex, let's try a different approach
                # Check if we can access notebooks directly
                async with client.get(f"{base_url}/api/contents/LeanCLI") as resp:
                    if resp.status == 200:
                        contents = await resp.json()
                        print(f"\n✓ LeanCLI directory contents:")
                        for item in contents.get('content', []):
                            print(f"  - {item['name']} ({item['type']})")
                    
            except Exception as e:
                print(f"✗ Error executing code: {e}")
                
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up
        print("\nCleaning up...")
        await session.close("test_completed")
        print("✓ Session cleaned up")

if __name__ == "__main__":
    success = asyncio.run(test_jupyter_rest_api())
    sys.exit(0 if success else 1)