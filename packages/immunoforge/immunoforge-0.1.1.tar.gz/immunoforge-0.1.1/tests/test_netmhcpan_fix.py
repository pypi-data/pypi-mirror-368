#!/usr/bin/env python3
"""
Test improved NetMHCpan parsing to fix the column misalignment issue
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

def parse_netmhcpan_output_fixed(output: str) -> pd.DataFrame:
    """Fixed parsing method that properly aligns columns"""
    try:
        lines = output.split('\n')
        
        # Find the data section between dash lines
        data_start = None
        data_end = None
        header_line = None
        
        for i, line in enumerate(lines):
            # Look for dash separator lines
            if re.match(r'^-{50,}$', line.strip()):
                # Check if previous line has headers
                if i > 0:
                    prev_line = lines[i - 1].strip()
                    if 'Peptide' in prev_line and ('Aff' in prev_line or 'Score' in prev_line):
                        header_line = prev_line
                        data_start = i + 1
                # Check if this is end separator
                elif data_start is not None:
                    data_end = i
                    break
        
        if data_start is None or header_line is None:
            logger.warning("Could not find header line in NetMHCpan output")
            return pd.DataFrame()
        
        print(f"Header line: {repr(header_line)}")
        print(f"Data starts at line {data_start}, ends at line {data_end}")
        
        # Extract data lines
        data_lines = lines[data_start:data_end] if data_end else lines[data_start:]
        data_lines = [line for line in data_lines if line.strip() and not line.strip().startswith('#')]
        
        # Remove summary lines (contain "Protein", "Length", etc.)
        data_lines = [line for line in data_lines if not re.search(r'Protein.*Length.*Number', line)]
        
        print(f"Data lines ({len(data_lines)}):")
        for line in data_lines:
            print(f"  {repr(line)}")
        
        if not data_lines:
            logger.warning("No data lines found in NetMHCpan output")
            return pd.DataFrame()
        
        # Parse header to find column positions
        header_cols = re.split(r'\s+', header_line.strip())
        print(f"Headers: {header_cols}")
        
        # Use fixed-width parsing approach
        # First, let's analyze column positions from the header
        col_positions = []
        start_pos = 0
        for col in header_cols:
            pos = header_line.find(col, start_pos)
            if pos != -1:
                col_positions.append(pos)
                start_pos = pos + len(col)
        
        print(f"Column positions: {list(zip(header_cols, col_positions))}")
        
        # Parse each data line using column positions
        data = []
        for line in data_lines:
            row = []
            for i, col_name in enumerate(header_cols):
                if i < len(col_positions):
                    start = col_positions[i]
                    # Find end position (start of next column or end of line)
                    if i + 1 < len(col_positions):
                        end = col_positions[i + 1]
                        value = line[start:end].strip()
                    else:
                        value = line[start:].strip()
                    row.append(value)
                else:
                    row.append('')
            data.append(row)
        
        print(f"Parsed data:")
        for row in data:
            print(f"  {row}")
        
        if not data:
            logger.warning("No valid data found in NetMHCpan output")
            return pd.DataFrame()
        
        # Create DataFrame
        df = pd.DataFrame(data, columns=header_cols)
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
        nan_counts = df.isna().sum()
        print(nan_counts)
        
        # Check if affinity column has valid values
        aff_col = None
        if 'Aff(nM)' in df.columns:
            aff_col = 'Aff(nM)'
        elif 'Affinity(nM)' in df.columns:
            aff_col = 'Affinity(nM)'
        
        if aff_col:
            print(f"\n{aff_col} column values: {df[aff_col].tolist()}")
            print(f"{aff_col} NaN count: {df[aff_col].isna().sum()}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error parsing NetMHCpan output: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

def parse_netmhcpan_output_regex_based(output: str) -> pd.DataFrame:
    """Alternative parsing using regex to extract structured data"""
    try:
        # Split on dashed separator
        parts = re.split(r"\n[-]{50,}\n", output)
        if len(parts) < 3:
            logger.warning("Could not find results in NetMHCpan output - unexpected format")
            return pd.DataFrame()
        
        # Find the section with headers and data
        header_line = None
        data_section = None
        
        for part in parts[1:]:  # Skip first part (header info)
            lines = part.strip().split('\n')
            for line in lines:
                if 'Peptide' in line and ('Aff' in line or 'Score' in line):
                    header_line = line.strip()
                    # Get remaining lines as data
                    idx = lines.index(line)
                    data_lines = lines[idx + 1:]
                    data_section = '\n'.join(data_lines)
                    break
            if header_line:
                break
        
        if not header_line or not data_section:
            logger.warning("Could not find header or data section")
            return pd.DataFrame()
        
        print(f"Header: {repr(header_line)}")
        print(f"Data section: {repr(data_section)}")
        
        # Clean up data section
        data_lines = [line.strip() for line in data_section.split('\n') 
                     if line.strip() and not re.search(r'Protein.*Length.*Number', line)]
        
        print(f"Clean data lines: {data_lines}")
        
        # Use a more sophisticated regex to parse each line
        # This pattern captures: number, peptide, HLA allele, core, score, affinity, rank, bind level
        pattern = r'^\s*(\d+)\s+(\w+)\s+(HLA-\w+\*\d+:\d+)\s+(\w+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*(\w*)\s*$'
        
        data = []
        headers = re.split(r'\s+', header_line)
        print(f"Headers from line: {headers}")
        
        for line in data_lines:
            match = re.match(pattern, line)
            if match:
                data.append(list(match.groups()))
            else:
                # Fall back to simple split if regex doesn't match
                parts = re.split(r'\s+', line.strip())
                if len(parts) >= 6:  # At least the core columns
                    data.append(parts[:len(headers)] if len(parts) >= len(headers) else parts + [''] * (len(headers) - len(parts)))
        
        print(f"Extracted data: {data}")
        
        if not data:
            logger.warning("No data extracted from NetMHCpan output")
            return pd.DataFrame()
        
        # Create DataFrame
        df = pd.DataFrame(data, columns=headers[:len(data[0])] if data else headers)
        
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
        
        return df
        
    except Exception as e:
        logger.error(f"Error in regex-based parsing: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

if __name__ == "__main__":
    print("NetMHCpan Parsing Fix Test")
    print("=" * 50)
    
    print("\n=== Testing Fixed Parsing Method ===")
    df1 = parse_netmhcpan_output_fixed(MOCK_NETMHCPAN_OUTPUT)
    
    print("\n=== Testing Regex-Based Parsing Method ===")
    df2 = parse_netmhcpan_output_regex_based(MOCK_NETMHCPAN_OUTPUT)