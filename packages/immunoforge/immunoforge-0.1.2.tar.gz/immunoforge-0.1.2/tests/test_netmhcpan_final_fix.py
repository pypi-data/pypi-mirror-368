#!/usr/bin/env python3
"""
Final fix for NetMHCpan parsing that preserves column alignment
"""

import pandas as pd
import re
from io import StringIO
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Mock NetMHCpan output
MOCK_NETMHCPAN_OUTPUT = """# NetMHCpan version 4.1

# Input is in FASTA format

# Peptide length 9

# Temporary directory made /tmp/netMHCpan_15825
# Command: /usr/local/bin/netMHCpan -p -BA -a HLA-A02:01 /tmp/tmp.pep

# Strong binder threshold  50 nM
# Weak binder threshold  500 nM

HLA-A*02:01 : Distance to training data  0.000 (using nearest neighbor HLA-A*02:01)

# Rank Threshold for Strong binding peptides   0.500
# Rank Threshold for Weak binding peptides   2.000

--------------------------------------------------------------------------------
    Pos  Peptide      HLA   Icore      Score   Aff(nM)  %Rank BindLevel
--------------------------------------------------------------------------------
      1  SIINFEKL  HLA-A*02:01  SIINFEKL   0.6543    0.25   0.01        SB
      2  GLCTLVAML HLA-A*02:01  GLCTLVAML  0.1234   45.67   0.98        WB
      3  AAAWYLWEV HLA-A*02:01  AAAWYLWEV  0.0123  123.45   2.34           
--------------------------------------------------------------------------------
Protein HLA-A*02:01. Length 3. Number of high binders 1. Number of weak binders 1. Number of peptides 3
--------------------------------------------------------------------------------

# NetMHCpan version 4.1 run finished at Sat Jul 12 10:00:00 2025
"""

def parse_netmhcpan_output_improved(output: str) -> pd.DataFrame:
    """Improved parsing that handles column alignment correctly"""
    try:
        # Split on dashed separator (80+ dashes)
        parts = re.split(r"\n[-]{80,}\n", output)
        if len(parts) < 3:
            logger.warning("Could not find results in NetMHCpan output - unexpected format")
            return pd.DataFrame()
        
        # Get the header and data sections
        header_and_data = parts[1] + "\n" + parts[2]
        lines = header_and_data.strip().split('\n')
        
        print(f"Header and data section lines:")
        for i, line in enumerate(lines):
            print(f"  {i}: {repr(line)}")
        
        # Find header line and data lines
        header_line = None
        data_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a header line
            if 'Peptide' in line and ('Aff' in line or 'Score' in line):
                header_line = line
                print(f"Found header line: {repr(header_line)}")
                # All subsequent non-empty lines are data (until summary)
                for j in range(i + 1, len(lines)):
                    data_line = lines[j].strip()
                    if data_line and not re.search(r'Protein.*Length.*Number', data_line):
                        data_lines.append(data_line)
                break
        
        if not header_line:
            logger.warning("Could not find header line in NetMHCpan output")
            return pd.DataFrame()
        
        if not data_lines:
            logger.warning("Could not find data lines in NetMHCpan output")
            return pd.DataFrame()
        
        print(f"Data lines:")
        for line in data_lines:
            print(f"  {repr(line)}")
        
        # Parse header to get column names
        headers = re.split(r'\s+', header_line)
        print(f"Headers: {headers}")
        
        # Parse each data line more carefully
        data = []
        for line in data_lines:
            # Split by whitespace but be careful about the HLA column which contains ':'
            parts = re.split(r'\s+', line)
            print(f"Raw parts: {parts}")
            
            # Handle the case where HLA-A*02:01 might be split
            if len(parts) > len(headers):
                # Look for HLA pattern and merge if needed
                merged_parts = []
                i = 0
                while i < len(parts):
                    if i < len(parts) - 1 and parts[i].startswith('HLA-') and ':' in parts[i + 1]:
                        # Merge HLA parts
                        merged_parts.append(parts[i] + parts[i + 1])
                        i += 2
                    else:
                        merged_parts.append(parts[i])
                        i += 1
                parts = merged_parts
            
            print(f"Processed parts: {parts}")
            
            # Ensure we have the right number of columns
            if len(parts) >= len(headers):
                data.append(parts[:len(headers)])
            elif len(parts) < len(headers):
                # Pad with empty strings
                data.append(parts + [''] * (len(headers) - len(parts)))
        
        print(f"Final data:")
        for row in data:
            print(f"  {row}")
        
        if not data:
            logger.warning("No valid data found in NetMHCpan output")
            return pd.DataFrame()
        
        # Create DataFrame
        df = pd.DataFrame(data, columns=headers)
        print(f"\nDataFrame before conversion:\n{df}")
        
        # Convert numeric columns
        possible_numeric_cols = [
            'Pos', 'Score', 'Affinity(nM)', '%Rank', 'Aff(nM)', 'Rank'
        ]
        for col in possible_numeric_cols:
            if col in df.columns:
                print(f"Converting column '{col}' to numeric")
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        print(f"\nFinal DataFrame:\n{df}")
        print(f"\nData types:\n{df.dtypes}")
        
        # Check for NaN values
        print(f"\nNaN counts:")
        print(df.isna().sum())
        
        # Check affinity column specifically
        aff_col = None
        if 'Aff(nM)' in df.columns:
            aff_col = 'Aff(nM)'
        elif 'Affinity(nM)' in df.columns:
            aff_col = 'Affinity(nM)'
        
        if aff_col:
            print(f"\nAffinity values in {aff_col}: {df[aff_col].tolist()}")
            non_nan_values = df[aff_col].dropna()
            print(f"Non-NaN affinity values: {non_nan_values.tolist()}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error parsing NetMHCpan output: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

if __name__ == "__main__":
    print("NetMHCpan Final Fix Test")
    print("=" * 50)
    
    df = parse_netmhcpan_output_improved(MOCK_NETMHCPAN_OUTPUT)