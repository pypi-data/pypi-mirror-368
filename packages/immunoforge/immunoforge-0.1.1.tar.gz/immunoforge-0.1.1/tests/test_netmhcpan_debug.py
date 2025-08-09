#!/usr/bin/env python3
"""
Debug script to test NetMHCpan parsing issues
"""

import pandas as pd
import subprocess
import tempfile
import os
import re
from io import StringIO
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import the working template
class NetMHCpanRunner:
    """Working template from user"""
    def __init__(self, program, alleles, tmpdir):
        self.program = program
        self.alleles = alleles or []
        self.tmpdir = tmpdir
        if self.tmpdir:
            os.makedirs(self.tmpdir, exist_ok=True)

    def predict(self, peptides):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".pep", dir=self.tmpdir, delete=True
        ) as pep_file:
            for p in peptides:
                pep_file.write(p + "\n")
            pep_file.flush()

            dfs = []
            for allele in self.alleles:
                cmd = [self.program, "-p", "-BA", "-a", allele.replace("*", ""), pep_file.name]
                try:
                    raw = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as e:
                    raise RuntimeError(f"netMHCpan failed for allele {allele}: {e.output.decode()}")
                
                df = self._parse_output(raw)
                if allele:
                    df["Allele"] = allele
                dfs.append(df)

        return pd.concat(dfs, ignore_index=True)

    def _parse_output(self, raw):
        text = raw.decode('utf-8')
        parts = re.split(r"\n[-]{80,}\n", text)
        if len(parts) < 3:
            raise ValueError("Unexpected netMHCpan output format")
        body = parts[1] + "\n" + parts[2]
        body = re.sub(r"[ ]+", ",", body)
        body = body.replace("\n,", "\n")
        df = pd.read_csv(StringIO(body))
        unnamed = [c for c in df.columns if c.startswith("Unnamed")]
        if unnamed:
            df = df.drop(columns=unnamed)
        return df


# Import our implementation
from immunoforge.tools.netmhcpan import NetMHCpanTool
from immunoforge.utils import format_hla_codes

def test_raw_netmhcpan_output():
    """Test raw NetMHCpan output to see what we're getting"""
    print("\n=== Testing Raw NetMHCpan Output ===")
    
    # Create test peptides file
    test_peptides = ["SIINFEKL", "GLCTLVAML", "AAAWYLWEV"]
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pep', delete=False) as f:
        for p in test_peptides:
            f.write(f"{p}\n")
        temp_file = f.name
    
    try:
        # Run NetMHCpan directly
        cmd = [
            "/tamir2/nicolaslynn/tools/netMHCpan-4.1/netMHCpan",
            "-p", "-BA",
            "-a", "HLA-A02:01",
            temp_file
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print(f"\nReturn code: {result.returncode}")
        print(f"\nSTDOUT length: {len(result.stdout)} characters")
        print("\nFirst 500 chars of STDOUT:")
        print(result.stdout[:500])
        
        if result.stderr:
            print(f"\nSTDERR:\n{result.stderr}")
        
        # Save full output for inspection
        with open('netmhcpan_raw_output.txt', 'w') as f:
            f.write(result.stdout)
        print("\nFull output saved to: netmhcpan_raw_output.txt")
        
        # Look for dash separators
        dash_pattern = r"\n[-]{80,}\n"
        matches = re.findall(dash_pattern, result.stdout)
        print(f"\nFound {len(matches)} dash separator(s)")
        
        # Split and show parts
        parts = re.split(dash_pattern, result.stdout)
        print(f"\nNumber of parts after splitting: {len(parts)}")
        for i, part in enumerate(parts[:4]):  # Show first 4 parts
            print(f"\n--- Part {i} (first 200 chars) ---")
            print(part[:200])
            
    finally:
        os.unlink(temp_file)


def test_template_parsing():
    """Test the working template"""
    print("\n=== Testing Template NetMHCpanRunner ===")
    
    alleles = ["HLA-A*02:01", "HLA-B*07:02"]
    runner = NetMHCpanRunner(
        program="/tamir2/nicolaslynn/tools/netMHCpan-4.1/netMHCpan",
        alleles=alleles,
        tmpdir="/tmp/test_netmhcpan"
    )
    
    peptides = ["SIINFEKL", "GLCTLVAML"]
    
    try:
        df = runner.predict(peptides)
        print(f"\nTemplate result shape: {df.shape}")
        print(f"Template columns: {list(df.columns)}")
        print("\nFirst few rows:")
        print(df.head())
    except Exception as e:
        print(f"Template failed: {e}")
        import traceback
        traceback.print_exc()


def test_our_implementation():
    """Test our NetMHCpanTool implementation"""
    print("\n=== Testing Our NetMHCpanTool ===")
    
    tool = NetMHCpanTool(
        executable="/tamir2/nicolaslynn/tools/netMHCpan-4.1/netMHCpan",
        tmpdir="/tmp/test_netmhcpan",
        extra_flags=["-p", "-BA"]
    )
    
    peptides = ["SIINFEKL", "GLCTLVAML"]
    alleles = ["A0201", "B0702"]  # Note: our format_hla_codes should handle this
    
    try:
        df = tool.predict(peptides, alleles=alleles)
        print(f"\nOur tool result shape: {df.shape}")
        print(f"Our tool columns: {list(df.columns)}")
        print("\nFirst few rows:")
        print(df.head())
    except Exception as e:
        print(f"Our tool failed: {e}")
        import traceback
        traceback.print_exc()


def test_parsing_methods():
    """Test both parsing methods on the same output"""
    print("\n=== Testing Parsing Methods ===")
    
    # Get raw output
    test_peptides = ["SIINFEKL"]
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
        
        raw_output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        
        # Test template parsing
        print("\n--- Template Parsing ---")
        try:
            runner = NetMHCpanRunner("dummy", ["dummy"], "/tmp")
            df_template = runner._parse_output(raw_output)
            print(f"Success! Shape: {df_template.shape}, Columns: {list(df_template.columns)}")
        except Exception as e:
            print(f"Failed: {e}")
        
        # Test our parsing
        print("\n--- Our Parsing ---")
        try:
            tool = NetMHCpanTool()
            df_ours = tool._parse_output(raw_output.decode('utf-8'))
            print(f"Success! Shape: {df_ours.shape}, Columns: {list(df_ours.columns)}")
        except Exception as e:
            print(f"Failed: {e}")
            
    finally:
        os.unlink(temp_file)


if __name__ == "__main__":
    print("NetMHCpan Debug Script")
    print("=" * 50)
    
    # Run all tests
    test_raw_netmhcpan_output()
    print("\n" + "=" * 50)
    test_template_parsing()
    print("\n" + "=" * 50)
    test_our_implementation()
    print("\n" + "=" * 50)
    test_parsing_methods()