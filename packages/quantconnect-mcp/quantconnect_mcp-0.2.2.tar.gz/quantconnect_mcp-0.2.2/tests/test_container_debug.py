#!/usr/bin/env python3
"""
Debug script to test different QuantConnect container configurations.
"""

import asyncio
import docker
import sys
from pathlib import Path

# Images to test
IMAGES_TO_TEST = [
    "quantconnect/research:latest",
    "quantconnect/lean:latest",
    "quantconnect/lean:foundation",
]

async def test_container_image(image_name):
    """Test a specific container image for QuantConnect module availability."""
    print(f"\n{'='*60}")
    print(f"Testing image: {image_name}")
    print(f"{'='*60}")
    
    client = docker.from_env()
    container = None
    
    try:
        # Pull image if needed
        try:
            client.images.get(image_name)
            print(f"✓ Image {image_name} already available")
        except docker.errors.ImageNotFound:
            print(f"Pulling image {image_name}...")
            client.images.pull(image_name)
        
        # Start container
        print("Starting container...")
        container = client.containers.run(
            image_name,
            command=["sleep", "infinity"],
            detach=True,
            environment={
                "PYTHONPATH": "/Lean:/Lean/Library",
                "COMPOSER_DLL_DIRECTORY": "/Lean",
            },
            remove=True,
            name=f"qc_test_{image_name.replace('/', '_').replace(':', '_')}"
        )
        
        # Wait for container to start
        await asyncio.sleep(3)
        
        # Run diagnostic commands
        commands = [
            ("ls -la /Lean/", "Check /Lean directory"),
            ("ls -la /Lean/Library/ | head -10", "Check /Lean/Library"),
            ("find /Lean -name '*.dll' | grep -i quantconnect | head -5", "Find QuantConnect DLLs"),
            ("find / -name 'QuantConnect.py' 2>/dev/null | head -5", "Find QuantConnect Python files"),
            ("python3 --version", "Python version"),
            ("pip list | grep -i quant || echo 'No QuantConnect in pip'", "Check pip packages"),
            ("python3 -c \"import sys; print('\\n'.join(sys.path[:10]))\"", "Python paths"),
        ]
        
        for cmd, description in commands:
            print(f"\n{description}:")
            result = container.exec_run(cmd, stdout=True, stderr=True)
            output = result.output.decode() if result.output else "No output"
            print(f"  Exit code: {result.exit_code}")
            print(f"  Output: {output[:500]}...")
        
        # Test QuantConnect imports
        print("\nTesting QuantConnect imports:")
        test_script = """
import sys
sys.path.insert(0, '/Lean')
sys.path.insert(0, '/Lean/Library')
sys.path.insert(0, '/Lean/Research')

# Try CLR approach
try:
    from clr import AddReference
    print("✓ CLR available")
    AddReference("QuantConnect.Common")
    AddReference("QuantConnect.Research")
    from QuantConnect import *
    from QuantConnect.Research import QuantBook
    print("✓ QuantConnect imported via CLR")
    qb = QuantBook()
    print(f"✓ QuantBook created: {type(qb)}")
except Exception as e:
    print(f"✗ CLR approach failed: {e}")

# Try direct Python import
try:
    import QuantConnect
    print("✓ QuantConnect module found")
    from QuantConnect.Research import QuantBook
    print("✓ QuantBook imported directly")
except Exception as e:
    print(f"✗ Direct import failed: {e}")

# Check for Jupyter kernel
import os
if os.path.exists('/opt/miniconda3/share/jupyter/kernels'):
    print("✓ Jupyter kernels directory exists")
    os.system('ls -la /opt/miniconda3/share/jupyter/kernels/')
"""
        
        # Write and execute test script
        container.exec_run("mkdir -p /tmp", workdir="/")
        write_cmd = f"cat > /tmp/test_qc.py << 'EOF'\n{test_script}\nEOF"
        container.exec_run(['/bin/sh', '-c', write_cmd])
        
        result = container.exec_run("python3 /tmp/test_qc.py", stdout=True, stderr=True)
        print(f"Exit code: {result.exit_code}")
        print(f"Output:\n{result.output.decode() if result.output else 'No output'}")
        
    except Exception as e:
        print(f"✗ Error testing {image_name}: {e}")
    finally:
        if container:
            print(f"\nStopping container...")
            container.stop()
    
    return container is not None

async def main():
    """Test all container images."""
    print("QuantConnect Container Module Availability Test")
    print("=" * 60)
    
    for image in IMAGES_TO_TEST:
        await test_container_image(image)
    
    print("\n" + "=" * 60)
    print("Test complete!")

if __name__ == "__main__":
    asyncio.run(main())