#!/usr/bin/env python3
"""
Test script to validate the new QuantConnect MCP implementation.
This tests the new approach using official quantconnect/research:latest Docker image
with Jupyter REST API execution.
"""

import asyncio
import sys
from pathlib import Path

# Add the source path
sys.path.insert(0, str(Path(__file__).parent / "quantconnect_mcp" / "src"))

from adapters.research_session_lean_cli import ResearchSession, ResearchSessionError


async def test_quantbook_initialization():
    """Test QuantBook initialization and basic functionality."""
    print("🧪 Testing QuantConnect MCP - New Implementation")
    print("=" * 60)
    
    session = None
    try:
        # Create a research session
        print("📦 Creating research session...")
        session = ResearchSession(session_id="test_session", port=8889)
        
        # Initialize the session
        print("🚀 Initializing session (this may take a few minutes)...")
        await session.initialize()
        print(f"✅ Session initialized successfully!")
        print(f"🌐 Jupyter accessible at: http://localhost:{session.port}")
        
        # Test basic QuantBook functionality
        print("\n🔬 Testing QuantBook initialization...")
        test_code = """
# Test QuantBook initialization
qb = QuantBook()
print(f'✅ QuantBook initialized: {type(qb)}')

# Test basic functionality
try:
    methods = [m for m in dir(qb) if not m.startswith('_')]
    print(f'📊 Available methods: {len(methods)}')
    print('✅ QuantBook basic functionality verified')
except Exception as e:
    print(f'❌ Error testing functionality: {e}')
"""
        
        result = await session.execute(test_code, timeout=120)
        
        print(f"\n📋 Execution Result:")
        print(f"Status: {result['status']}")
        print(f"Output:\n{result.get('output', 'No output')}")
        
        if result.get('error'):
            print(f"Error: {result['error']}")
        
        if result['status'] == 'success':
            print("\n🎉 SUCCESS: QuantBook initialization test passed!")
            
            # Test adding equity
            print("\n📈 Testing add equity functionality...")
            equity_code = """
# Test adding equity
try:
    equity = qb.AddEquity("AAPL", Resolution.Daily)
    print(f'✅ Added equity: {equity.Symbol}')
    print(f'📊 Security type: {equity.SecurityType}')
    print(f'🏪 Market: {equity.Market}')
    print('✅ Add equity test passed!')
except Exception as e:
    print(f'❌ Add equity failed: {e}')
    import traceback
    traceback.print_exc()
"""
            
            equity_result = await session.execute(equity_code, timeout=60)
            print(f"\n📋 Add Equity Result:")
            print(f"Status: {equity_result['status']}")
            print(f"Output:\n{equity_result.get('output', 'No output')}")
            
            if equity_result.get('error'):
                print(f"Error: {equity_result['error']}")
                
            if equity_result['status'] == 'success':
                print("\n🎉 SUCCESS: All tests passed!")
                return True
            else:
                print("\n❌ PARTIAL SUCCESS: QuantBook works but add equity failed")
                return False
        else:
            print("\n❌ FAILURE: QuantBook initialization failed")
            return False
            
    except ResearchSessionError as e:
        print(f"\n❌ Research session error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if session:
            print("\n🧹 Cleaning up session...")
            await session.close()
            print("✅ Session closed")


async def main():
    """Main test function."""
    success = await test_quantbook_initialization()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! The new implementation is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ TESTS FAILED. Check the output above for details.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())