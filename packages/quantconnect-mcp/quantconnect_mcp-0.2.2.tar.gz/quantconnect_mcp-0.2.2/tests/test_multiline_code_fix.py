#!/usr/bin/env python3
"""Test the fix for multi-line code formatting in execute_quantbook_code."""

import json

def format_code_for_notebook(code):
    """Format code for Jupyter notebook source field (the fixed version)."""
    if isinstance(code, str):
        lines = code.split('\n')
        # Add newline to each line except possibly the last
        source = [line + '\n' for line in lines[:-1]]
        if lines[-1]:  # If last line is not empty, add it
            source.append(lines[-1] + '\n')
        elif not source:  # If code was empty or just newlines
            source = ['']
    else:
        source = code
    return source

# Test cases
test_cases = [
    # Normal multi-line code
    """# This is a test
equity = qb.AddEquity("AAPL")
history = qb.History(equity.Symbol, 10, Resolution.Daily)
print(history)""",
    
    # Code with empty lines
    """# Test with empty lines
equity = qb.AddEquity("AAPL")

# Get history
history = qb.History(equity.Symbol, 10)

print(history)""",
    
    # Single line code
    "print('Hello, QuantBook!')",
    
    # Empty code
    "",
    
    # Code ending with newline
    "print('test')\n",
    
    # Complex code with indentation
    """def analyze_stock(symbol):
    equity = qb.AddEquity(symbol)
    history = qb.History(equity.Symbol, 30, Resolution.Daily)
    
    if len(history) > 0:
        print(f"Average close: {history['close'].mean()}")
    else:
        print("No data available")

analyze_stock("AAPL")"""
]

for i, code in enumerate(test_cases):
    print(f"\n=== Test Case {i+1} ===")
    print(f"Original code:\n{repr(code)}")
    
    formatted = format_code_for_notebook(code)
    print(f"\nFormatted source list:")
    print(repr(formatted))
    
    # Create a notebook cell
    cell = {
        "cell_type": "code",
        "metadata": {},
        "source": formatted,
        "outputs": []
    }
    
    # Convert to JSON and back to verify it works
    json_str = json.dumps(cell)
    parsed = json.loads(json_str)
    
    # Reconstruct the code from the parsed JSON
    reconstructed = ''.join(parsed['source'])
    print(f"\nReconstructed code:\n{repr(reconstructed)}")
    
    # Verify it matches (accounting for trailing newline)
    original_with_newline = code if code.endswith('\n') else code + '\n' if code else ''
    if reconstructed == original_with_newline:
        print("✓ Code preserved correctly!")
    else:
        print("✗ Code NOT preserved correctly!")
        print(f"  Expected: {repr(original_with_newline)}")
        print(f"  Got:      {repr(reconstructed)}")