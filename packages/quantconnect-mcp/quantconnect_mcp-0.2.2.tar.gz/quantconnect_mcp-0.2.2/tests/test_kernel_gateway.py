#!/usr/bin/env python3
"""
Test executing QuantBook code by interacting with the Jupyter kernel directly.
This approach bypasses nbconvert and might preserve the kernel state better.
"""

import asyncio
import json
import sys
from pathlib import Path
import tempfile

# Add the source directory to the path
sys.path.insert(0, str(Path(__file__).parent / "quantconnect_mcp" / "src"))

from adapters.research_session_lean_cli import ResearchSession

async def test_kernel_gateway_approach():
    """Test executing code through kernel gateway pattern."""
    print("=" * 60)
    print("Kernel Gateway Approach Test")
    print("=" * 60)
    
    session = ResearchSession(session_id="kernel_gateway_test")
    
    try:
        # Initialize the session
        print("\n1. Initializing research session...")
        await session.initialize()
        print(f"✓ Session initialized")
        
        # Wait for container to be ready
        await asyncio.sleep(3)
        
        # First, let's check what kernels are available
        print("\n2. Checking available kernels...")
        kernel_list_cmd = "jupyter kernelspec list --json"
        
        result = await session.container.exec_run(
            ['/bin/sh', '-c', kernel_list_cmd],
            demux=False
        )
        
        if result.exit_code == 0:
            kernel_output = result.output.decode('utf-8', errors='replace')
            print(f"Available kernels: {kernel_output}")
            
            # Parse kernel info
            try:
                kernel_info = json.loads(kernel_output)
                kernelspecs = kernel_info.get('kernelspecs', {})
                
                # Look for Foundation kernel
                foundation_kernel = None
                for kernel_name, spec in kernelspecs.items():
                    if 'foundation' in kernel_name.lower():
                        foundation_kernel = kernel_name
                        print(f"✓ Found Foundation kernel: {kernel_name}")
                        break
                
                if not foundation_kernel:
                    print("✗ No Foundation kernel found, using python3")
                    foundation_kernel = "python3"
                    
            except json.JSONDecodeError:
                print("Failed to parse kernel list, using python3")
                foundation_kernel = "python3"
        else:
            print("Failed to list kernels, using python3")
            foundation_kernel = "python3"
        
        # Try using ipython directly with the kernel
        print("\n3. Testing direct IPython kernel execution...")
        
        # Create a temporary script that uses IPython's kernel client
        kernel_script = """
import sys
import time
from jupyter_client import KernelManager

# Create kernel manager
km = KernelManager(kernel_name='@KERNEL_NAME@')
km.start_kernel()

# Get kernel client
kc = km.client()
kc.start_channels()

# Wait for kernel to be ready
kc.wait_for_ready(timeout=10)

print("Kernel started successfully")

# Execute code to check QuantBook
msg_id = kc.execute('''
# Check if qb is available
try:
    qb
    print(f"✓ QuantBook is available as 'qb'!")
    print(f"Type: {type(qb)}")
    print(f"Dir: {[m for m in dir(qb) if not m.startswith('_')][:10]}")
except NameError:
    print("✗ qb not found, trying to import...")
    try:
        from QuantConnect.Research import QuantBook
        qb = QuantBook()
        print("✓ Successfully created QuantBook instance")
    except Exception as e:
        print(f"✗ Failed to create QuantBook: {e}")
        
# Try to use it
try:
    if 'qb' in locals():
        equity = qb.AddEquity("AAPL")
        print(f"✓ Added AAPL: {equity}")
except Exception as e:
    print(f"Error using QuantBook: {e}")
''')

# Get results
while True:
    try:
        msg = kc.get_iopub_msg(timeout=1)
        msg_type = msg['header']['msg_type']
        
        if msg_type == 'stream':
            print(msg['content']['text'], end='')
        elif msg_type == 'execute_result':
            print(msg['content']['data'].get('text/plain', ''))
        elif msg_type == 'error':
            print(f"Error: {msg['content']['ename']}: {msg['content']['evalue']}")
            for line in msg['content']['traceback']:
                print(line)
        elif msg_type == 'status' and msg['content']['execution_state'] == 'idle':
            break
    except:
        break

# Shutdown
kc.stop_channels()
km.shutdown_kernel()
print("\\nKernel shutdown complete")
""".replace('@KERNEL_NAME@', foundation_kernel)
        
        # Write script to container
        script_path = "/tmp/kernel_test.py"
        write_cmd = f"cat > {script_path} << 'EOF'\n{kernel_script}\nEOF"
        
        result = await session.container.exec_run(
            ['/bin/sh', '-c', write_cmd],
            demux=False
        )
        
        if result.exit_code == 0:
            print("✓ Script written to container")
            
            # Execute the script
            print("\n4. Executing kernel test script...")
            exec_cmd = f"cd /Lean && python {script_path}"
            
            result = await session.container.exec_run(
                ['/bin/sh', '-c', exec_cmd],
                demux=False
            )
            
            output = result.output.decode('utf-8', errors='replace') if result.output else ""
            print("Kernel execution output:")
            print("-" * 50)
            print(output)
            print("-" * 50)
            
        # Alternative approach: Use jupyter console
        print("\n5. Testing jupyter console approach...")
        
        # Create a simple test script
        test_code = """
print("Testing QuantBook availability...")
try:
    print(f"qb type: {type(qb)}")
    print("✓ qb is available!")
except NameError:
    print("✗ qb is not available")
"""
        
        # Write test code to a file
        test_file = "/tmp/qb_test.py"
        write_test_cmd = f"cat > {test_file} << 'EOF'\n{test_code}\nEOF"
        
        result = await session.container.exec_run(
            ['/bin/sh', '-c', write_test_cmd],
            demux=False
        )
        
        # Try executing with jupyter console
        console_cmd = f"cd /Lean && echo 'exec(open(\"{test_file}\").read())' | jupyter console --kernel={foundation_kernel} --simple-prompt"
        
        result = await session.container.exec_run(
            ['/bin/sh', '-c', console_cmd],
            demux=False,
            stdin=True
        )
        
        output = result.output.decode('utf-8', errors='replace') if result.output else ""
        print("Jupyter console output:")
        print("-" * 50)
        print(output)
        
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
    success = asyncio.run(test_kernel_gateway_approach())
    sys.exit(0 if success else 1)