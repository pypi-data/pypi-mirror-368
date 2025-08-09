#!/usr/bin/env python3
"""
Simple test to diagnose NetMHCpan output parsing
"""

import subprocess
import tempfile
import os
import re

# Test 1: Check raw output structure
print("=== Test 1: Raw NetMHCpan Output Structure ===")
with tempfile.NamedTemporaryFile(mode='w', suffix='.pep', delete=False) as f:
    f.write("SIINFEKL\n")
    temp_file = f.name

try:
    cmd = [
        "/tamir2/nicolaslynn/tools/netMHCpan-4.1/netMHCpan",
        "-p", "-BA",
        "-a", "HLA-A02:01",
        temp_file
    ]
    
    output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
    
    # Count dash separators
    separators = re.findall(r'\n-{50,}\n', output)
    print(f"Found {len(separators)} dash separators (50+ dashes)")
    
    separators = re.findall(r'\n-{80,}\n', output)
    print(f"Found {len(separators)} dash separators (80+ dashes)")
    
    # Show line with dashes
    lines = output.split('\n')
    for i, line in enumerate(lines):
        if re.match(r'^-{50,}$', line):
            print(f"\nLine {i}: '{line}'")
            print(f"Length: {len(line)} dashes")
            if i > 0:
                print(f"Previous line: '{lines[i-1]}'")
            if i < len(lines) - 1:
                print(f"Next line: '{lines[i+1]}'")
    
    # Save output
    with open('netmhcpan_output.txt', 'w') as f:
        f.write(output)
    print("\nFull output saved to netmhcpan_output.txt")
    
finally:
    os.unlink(temp_file)

# Test 2: Check if the tool is actually running
print("\n=== Test 2: Import and Run NetMHCpanTool ===")
try:
    from immunoforge.tools.netmhcpan import NetMHCpanTool
    from immunoforge.utils import format_hla_codes
    
    tool = NetMHCpanTool(
        executable="/tamir2/nicolaslynn/tools/netMHCpan-4.1/netMHCpan",
        tmpdir="/tmp/test_netmhcpan"
    )
    
    # Enable debug logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    peptides = ["SIINFEKL"]
    alleles = ["A0201"]
    
    print(f"Formatted alleles: {format_hla_codes(alleles)}")
    
    df = tool.predict(peptides, alleles=alleles)
    print(f"\nResult shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"Data:\n{df}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()