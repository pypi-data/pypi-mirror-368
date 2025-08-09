#!/usr/bin/env python3
"""
Test script for UniProt epitope checking functionality
"""

import sys
import os
sys.path.append('/')

from immunoforge.tools.uniprot_blast import UniProtBLASTTool

def test_uniprot_check():
    """Test the UniProt check functionality"""
    
    # Example epitopes for testing
    test_epitopes = [
        "YLQPRTFLL",  # Known HIV epitope - should have matches
        "ILKEPVHGV",  # Another known epitope
        "XYZABC123",  # Random sequence - should have no matches
    ]
    
    print("Testing UniProt epitope checking functionality")
    print("=" * 50)
    
    try:
        # Initialize the tool (will use local BLAST by default)
        tool = UniProtBLASTTool()
        
        for epitope in test_epitopes:
            print(f"\nTesting epitope: {epitope}")
            print("-" * 30)
            
            # Test the new simplified method
            result = tool.check_epitope_uniqueness(epitope)
            
            if 'error' in result:
                print(f"Error: {result['error']}")
                continue
            
            print(f"Has identical match: {result['has_identical_match']}")
            print(f"Closest match percentage: {result['closest_match_percentage']:.1f}%")
            
            if result['closest_match_accession']:
                print(f"Closest match accession: {result['closest_match_accession']}")
            
            if result['closest_match_organism']:
                print(f"Closest match organism: {result['closest_match_organism']}")
            
            # Interpretation
            if result['has_identical_match']:
                print("RECOMMENDATION: EXCLUDE - Identical epitope found in database")
            elif result['closest_match_percentage'] >= 90:
                print("RECOMMENDATION: CAUTION - High similarity to known protein")
            elif result['closest_match_percentage'] >= 70:
                print("RECOMMENDATION: REVIEW - Moderate similarity detected")
            else:
                print("RECOMMENDATION: PROCEED - Novel epitope, low similarity")
    
    except Exception as e:
        print(f"Error initializing UniProt tool: {e}")
        print("\nPossible issues:")
        print("- BLAST executable not configured")
        print("- UniProt database not available")
        print("- Check your configuration in immunoforge/config.py")

if __name__ == "__main__":
    test_uniprot_check()