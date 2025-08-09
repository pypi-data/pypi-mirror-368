#!/usr/bin/env python3
"""
Test NetMHCpan tool standalone to verify it works correctly
"""

import pandas as pd
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Import and test our tool
from immunoforge.tools.netmhcpan import NetMHCpanTool
from immunoforge.utils import format_hla_codes

print("=== Testing NetMHCpan Tool Standalone ===\n")

# Initialize tool
tool = NetMHCpanTool(
    executable="/tamir2/nicolaslynn/tools/netMHCpan-4.1/netMHCpan",
    tmpdir="/tmp/test_netmhcpan"
)

# Test peptides and alleles
peptides = ["SIINFEKL", "GLCTLVAML", "AAAWYLWEV"]
alleles = ["A0201", "B0702"]

print(f"Input peptides: {peptides}")
print(f"Input alleles: {alleles}")
print(f"Formatted alleles: {format_hla_codes(alleles)}\n")

try:
    # Run prediction
    results = tool.predict(peptides, alleles=alleles)
    
    print(f"\nResults shape: {results.shape}")
    print(f"Columns: {list(results.columns)}")
    print(f"\nData types:")
    print(results.dtypes)
    print(f"\nFirst few rows:")
    print(results.head(10))
    
    # Check for NaN values
    print(f"\nNaN counts per column:")
    print(results.isna().sum())
    
    # Save results for inspection
    results.to_csv('netmhcpan_results.csv', index=False)
    print("\nResults saved to netmhcpan_results.csv")
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()

# Also test the pipeline integration
print("\n\n=== Testing Pipeline Integration ===\n")

from immunoforge.pipeline import EpitopePipeline, PipelineConfig

# Create a minimal test DataFrame
test_data = pd.DataFrame({
    'mut_id': ['TEST1'],
    'transcript_id': ['TRANS1'],
    'isoform_id': ['ISO1'],
    'variant_protein': ['MSIINFEKLGLCTLVAMLAAAWYLWEV'],  # Contains our test peptides
    'reference_protein': ['MAAAAAAAAAAAAAAAAAAAAAAAAAA']  # Add required reference_protein column
})

# Configure pipeline with only NetMHCpan
config = PipelineConfig(
    tools={'netmhcpan': {}},
    alleles=['A0201', 'B0702'],
    nmer_length=9,
    debug=True
)

pipeline = EpitopePipeline(config=config)

try:
    results = pipeline.process(test_data, progress_bar=False)
    
    print(f"Pipeline results shape: {results.shape}")
    print(f"Pipeline columns: {list(results.columns)}")
    
    # Check MHC-related columns
    mhc_cols = [col for col in results.columns if 'mhc' in col.lower() or 'netmhc' in col.lower()]
    print(f"\nMHC-related columns: {mhc_cols}")
    
    if mhc_cols:
        print(f"\nMHC column data:")
        print(results[mhc_cols].head())
        
        print(f"\nNaN counts in MHC columns:")
        print(results[mhc_cols].isna().sum())
    
    # Save pipeline results
    results.to_csv('pipeline_results.csv', index=False)
    print("\nPipeline results saved to pipeline_results.csv")
    
except Exception as e:
    print(f"\nPipeline error: {e}")
    import traceback
    traceback.print_exc()