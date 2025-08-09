#!/usr/bin/env python3
"""
Test NetMHCpan parsing with mock output to identify column name issues
"""

import pandas as pd
import re
from io import StringIO
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Mock NetMHCpan output based on typical format
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

# Alternative format with Affinity(nM) column name
MOCK_NETMHCPAN_OUTPUT_ALT = """# NetMHCpan version 4.1

--------------------------------------------------------------------------------
 Pos  Peptide      HLA         Icore       Score  Affinity(nM)  %Rank BindLevel
--------------------------------------------------------------------------------
   1  SIINFEKL  HLA-A*02:01  SIINFEKL      0.6543        0.25   0.01        SB
   2  GLCTLVAML HLA-A*02:01  GLCTLVAML     0.1234       45.67   0.98        WB
   3  AAAWYLWEV HLA-A*02:01  AAAWYLWEV     0.0123      123.45   2.34           
--------------------------------------------------------------------------------
Protein HLA-A*02:01. Length 3. Number of high binders 1. Number of weak binders 1. Number of peptides 3
--------------------------------------------------------------------------------
"""

def test_current_parsing_method(output):
    """Test the current parsing method from NetMHCpanTool"""
    print("\n--- Testing Current Parsing Method ---")
    
    try:
        # Split on dashed separator (80+ dashes)
        parts = re.split(r"\n[-]{80,}\n", output)
        print(f"Number of parts after splitting: {len(parts)}")
        
        if len(parts) < 3:
            print("ERROR: Could not find results - unexpected format")
            return pd.DataFrame()
        
        # Show what we're parsing
        print(f"\nPart 1 (before first separator):\n{repr(parts[0][:200])}")
        print(f"\nPart 2 (main results):\n{repr(parts[1])}")
        print(f"\nPart 3 (after second separator):\n{repr(parts[2])}")
        
        # Combine the main result sections
        body = parts[1] + "\n" + parts[2]
        print(f"\nCombined body:\n{repr(body)}")
        
        # Normalize spacing to commas for CSV parsing
        body = re.sub(r"[ ]+", ",", body)
        body = body.replace("\n,", "\n")
        print(f"\nAfter normalization:\n{repr(body)}")
        
        # Read into DataFrame
        df = pd.read_csv(StringIO(body))
        
        print(f"\nParsed columns: {list(df.columns)}")
        print(f"Data shape: {df.shape}")
        print(f"\nDataFrame:\n{df}")
        
        # Log columns for debugging
        logger.debug(f"NetMHCpan parsed columns: {list(df.columns)}")
        
        # Drop unnamed index column if present
        unnamed = [c for c in df.columns if c.startswith("Unnamed")]
        if unnamed:
            df = df.drop(columns=unnamed)
            print(f"\nAfter dropping unnamed columns: {list(df.columns)}")
        
        # Convert numeric columns - check various possible column names
        possible_numeric_cols = [
            'Affinity(nM)', '%Rank', 'Score_EL', '%Rank_EL',
            'Aff(nM)', 'Rank', 'Core', 'H_Avg_Ranks', 'N_Binders'
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
        
        return df
        
    except Exception as e:
        print(f"ERROR: Parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

def test_improved_parsing_method(output):
    """Test an improved parsing method"""
    print("\n--- Testing Improved Parsing Method ---")
    
    try:
        lines = output.split('\n')
        
        # Find the data section between dash lines
        data_start = None
        data_end = None
        header_line = None
        
        for i, line in enumerate(lines):
            # Look for dash separator lines
            if re.match(r'^-{50,}$', line.strip()):
                # Check if next line has headers
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if 'Peptide' in next_line and ('Aff' in next_line or 'Score' in next_line):
                        header_line = next_line
                        data_start = i + 2
                    elif data_start is not None:
                        # Found end separator
                        data_end = i
                        break
        
        if data_start is None or header_line is None:
            print("ERROR: Could not find header line")
            return pd.DataFrame()
        
        print(f"Header line: {repr(header_line)}")
        print(f"Data starts at line {data_start}, ends at line {data_end}")
        
        # Extract data lines
        data_lines = lines[data_start:data_end] if data_end else lines[data_start:]
        data_lines = [line.strip() for line in data_lines if line.strip() and not line.strip().startswith('#')]
        
        # Remove summary lines (contain "Protein", "Length", etc.)
        data_lines = [line for line in data_lines if not re.search(r'Protein.*Length.*Number', line)]
        
        print(f"Data lines: {data_lines}")
        
        if not data_lines:
            print("ERROR: No data lines found")
            return pd.DataFrame()
        
        # Split header and data by whitespace, but be careful with multiple spaces
        headers = re.split(r'\s+', header_line)
        print(f"Headers: {headers}")
        
        data = []
        for line in data_lines:
            parts = re.split(r'\s+', line)
            if len(parts) >= len(headers):
                data.append(parts[:len(headers)])
            else:
                print(f"Warning: Line has fewer columns than expected: {line}")
        
        if not data:
            print("ERROR: No valid data found")
            return pd.DataFrame()
        
        # Create DataFrame
        df = pd.DataFrame(data, columns=headers)
        print(f"\nDataFrame before conversion:\n{df}")
        
        # Convert numeric columns
        possible_numeric_cols = [
            'Affinity(nM)', '%Rank', 'Score', 'Aff(nM)', 'Rank'
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
        
        return df
        
    except Exception as e:
        print(f"ERROR: Improved parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

if __name__ == "__main__":
    print("NetMHCpan Parsing Test")
    print("=" * 50)
    
    print("\n=== Testing Mock Output with Aff(nM) ===")
    df1 = test_current_parsing_method(MOCK_NETMHCPAN_OUTPUT)
    df2 = test_improved_parsing_method(MOCK_NETMHCPAN_OUTPUT)
    
    print("\n=== Testing Mock Output with Affinity(nM) ===")
    df3 = test_current_parsing_method(MOCK_NETMHCPAN_OUTPUT_ALT)
    df4 = test_improved_parsing_method(MOCK_NETMHCPAN_OUTPUT_ALT)