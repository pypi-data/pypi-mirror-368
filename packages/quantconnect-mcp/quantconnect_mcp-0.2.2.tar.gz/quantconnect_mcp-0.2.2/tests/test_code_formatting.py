#!/usr/bin/env python3
"""Test script to diagnose the code formatting issue."""

import json

# Test case - multi-line Python code
test_code = """# This is a test
equity = qb.AddEquity("AAPL")
history = qb.History(equity.Symbol, 10, Resolution.Daily)
print(history)"""

# Current implementation (problematic)
current_split = test_code.split('\n') if isinstance(test_code, str) else test_code
print("Current split result:")
print(current_split)
print()

# When put in notebook JSON
notebook_cell = {
    "cell_type": "code",
    "metadata": {},
    "source": current_split,
    "outputs": []
}

print("Notebook cell JSON:")
print(json.dumps(notebook_cell, indent=2))
print()

# Proper format for Jupyter notebooks
proper_format = [line + '\n' for line in test_code.split('\n')]
# Don't add newline to last line
if proper_format and proper_format[-1].endswith('\n\n'):
    proper_format[-1] = proper_format[-1][:-1]

notebook_cell_proper = {
    "cell_type": "code",
    "metadata": {},
    "source": proper_format,
    "outputs": []
}

print("Proper notebook cell JSON:")
print(json.dumps(notebook_cell_proper, indent=2))