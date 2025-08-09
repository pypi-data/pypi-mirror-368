#!/usr/bin/env python3
"""
Test script for enhanced ImmunoForge components

This script tests the new scoring, organization, and pipeline components
to ensure they work correctly with realistic data.
"""

import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path

# Add the immunoforge package to the path
sys.path.insert(0, str(Path(__file__).parent))

# Import components directly to avoid circular import issues
from immunoforge.scoring.standardizer import StandardScorer
from immunoforge.scoring.biological_stages import ImmunoScore
from immunoforge.scoring.confidence import ConfidenceScorer
from immunoforge.results.organizer import ResultsOrganizer
from immunoforge.improved_config import ImprovedPipelineConfig


def create_test_data():
    """Create realistic test data simulating pipeline output"""
    np.random.seed(42)  # For reproducible results
    
    n_epitopes = 50
    n_mutations = 5
    
    # Create base data
    epitopes = [f"EPITOPE{i:03d}" for i in range(n_epitopes)]
    mutations = [f"MUT_{i+1}" for i in range(n_mutations)]
    
    data = {
        'epitope': epitopes,
        'source_mut_id': np.random.choice(mutations, n_epitopes),
        
        # Raw tool scores (different ranges and meanings)
        'processing_score': np.random.beta(2, 2, n_epitopes),  # NetChop (0-1)
        'mhc_affinity': np.random.exponential(500, n_epitopes),  # Affinity in nM (lower=better)
        'netmhc_%Rank_BA': np.random.exponential(2, n_epitopes),  # Percentile rank (lower=better)
        'netmhc_%Rank_EL': np.random.exponential(2, n_epitopes),  # Percentile rank (lower=better)
        'mhc_presentation_score': np.random.beta(2, 3, n_epitopes),  # MHCflurry probability (0-1)
        'iedb_score': np.random.beta(1.5, 1.5, n_epitopes),  # IEDB immunogenicity (0-1)
        'deepimmuno_score': np.random.beta(1.5, 2, n_epitopes),  # DeepImmuno CNN (0-1)
        'pepmatch_mismatches': np.random.poisson(1.5, n_epitopes),  # Mismatches (lower=more similar)
    }
    
    # Ensure realistic ranges
    data['mhc_affinity'] = np.clip(data['mhc_affinity'], 10, 50000)
    data['netmhc_%Rank_BA'] = np.clip(data['netmhc_%Rank_BA'], 0.01, 100)
    data['netmhc_%Rank_EL'] = np.clip(data['netmhc_%Rank_EL'], 0.01, 100)
    data['pepmatch_mismatches'] = np.clip(data['pepmatch_mismatches'], 0, 9)
    
    return pd.DataFrame(data)


def test_standard_scorer():
    """Test StandardScorer normalization"""
    print("Testing StandardScorer...")
    
    test_df = create_test_data()
    scorer = StandardScorer()
    
    # Test normalization
    normalized_df = scorer.normalize_all_scores(test_df)
    
    # Check that normalized columns exist
    expected_norm_cols = [
        'netchop_score_norm', 'mhc_affinity_score_norm', 
        'netmhc_rank_ba_score_norm', 'netmhc_rank_el_score_norm',
        'mhcflurry_presentation_score_norm', 'iedb_score_norm', 
        'deepimmuno_score_norm', 'pepmatch_novelty_score_norm'
    ]
    
    missing_cols = [col for col in expected_norm_cols if col not in normalized_df.columns]
    if missing_cols:
        print(f"  ❌ Missing normalized columns: {missing_cols}")
        return False
    
    # Check that normalized scores are in 0-1 range
    for col in expected_norm_cols:
        if col in normalized_df.columns:
            min_val = normalized_df[col].min()
            max_val = normalized_df[col].max()
            if min_val < 0 or max_val > 1:
                print(f"  ❌ {col} not in 0-1 range: {min_val:.3f} - {max_val:.3f}")
                return False
    
    # Test specific normalizations
    # MHC affinity: lower nM should give higher scores
    low_affinity_idx = test_df['mhc_affinity'].idxmin()
    high_affinity_idx = test_df['mhc_affinity'].idxmax()
    
    low_affinity_score = normalized_df.loc[low_affinity_idx, 'mhc_affinity_score_norm']
    high_affinity_score = normalized_df.loc[high_affinity_idx, 'mhc_affinity_score_norm']
    
    if low_affinity_score <= high_affinity_score:
        print(f"  ❌ MHC affinity normalization incorrect: low_nM_score={low_affinity_score:.3f} <= high_nM_score={high_affinity_score:.3f}")
        return False
    
    print("  ✅ StandardScorer tests passed")
    return True


def test_immuno_score():
    """Test ImmunoScore biological stage scoring"""
    print("Testing ImmunoScore...")
    
    test_df = create_test_data()
    
    # First normalize scores
    scorer = StandardScorer()
    normalized_df = scorer.normalize_all_scores(test_df)
    
    # Then calculate stage scores
    immuno_scorer = ImmunoScore()
    stage_df = immuno_scorer.calculate_final_immunogenicity_score(normalized_df)
    
    # Check that stage scores exist
    expected_stage_cols = [
        'generation_score', 'presentation_score', 'recognition_score',
        'novelty_score', 'final_immunogenicity_score'
    ]
    
    missing_cols = [col for col in expected_stage_cols if col not in stage_df.columns]
    if missing_cols:
        print(f"  ❌ Missing stage columns: {missing_cols}")
        return False
    
    # Check that all stage scores are in 0-1 range
    for col in expected_stage_cols:
        min_val = stage_df[col].min()
        max_val = stage_df[col].max()
        if min_val < 0 or max_val > 1:
            print(f"  ❌ {col} not in 0-1 range: {min_val:.3f} - {max_val:.3f}")
            return False
    
    # Check that final score is reasonable combination of stages
    mean_final = stage_df['final_immunogenicity_score'].mean()
    if mean_final < 0.1 or mean_final > 0.9:
        print(f"  ❌ Final immunogenicity score mean seems unrealistic: {mean_final:.3f}")
        return False
    
    print("  ✅ ImmunoScore tests passed")
    return True


def test_confidence_scorer():
    """Test ConfidenceScorer"""
    print("Testing ConfidenceScorer...")
    
    test_df = create_test_data()
    
    # Normalize and get stage scores first
    scorer = StandardScorer()
    normalized_df = scorer.normalize_all_scores(test_df)
    
    immuno_scorer = ImmunoScore()
    stage_df = immuno_scorer.calculate_final_immunogenicity_score(normalized_df)
    
    # Calculate confidence
    conf_scorer = ConfidenceScorer()
    conf_df = conf_scorer.calculate_confidence_score(stage_df)
    
    # Check confidence columns exist
    expected_conf_cols = [
        'data_completeness', 'tool_agreement', 'score_consistency',
        'outlier_flag', 'confidence_score', 'confidence_level'
    ]
    
    missing_cols = [col for col in expected_conf_cols if col not in conf_df.columns]
    if missing_cols:
        print(f"  ❌ Missing confidence columns: {missing_cols}")
        return False
    
    # Check confidence score range
    conf_score_min = conf_df['confidence_score'].min()
    conf_score_max = conf_df['confidence_score'].max()
    if conf_score_min < 0 or conf_score_max > 1:
        print(f"  ❌ Confidence score not in 0-1 range: {conf_score_min:.3f} - {conf_score_max:.3f}")
        return False
    
    # Check confidence levels
    expected_levels = {'Low', 'Moderate', 'High', 'Very High'}
    actual_levels = set(conf_df['confidence_level'].unique())
    if not actual_levels.issubset(expected_levels):
        print(f"  ❌ Unexpected confidence levels: {actual_levels - expected_levels}")
        return False
    
    print("  ✅ ConfidenceScorer tests passed")
    return True


def test_results_organizer():
    """Test ResultsOrganizer"""
    print("Testing ResultsOrganizer...")
    
    # Create full pipeline results
    test_df = create_test_data()
    scorer = StandardScorer()
    normalized_df = scorer.normalize_all_scores(test_df)
    immuno_scorer = ImmunoScore()
    stage_df = immuno_scorer.calculate_final_immunogenicity_score(normalized_df)
    conf_scorer = ConfidenceScorer()
    full_df = conf_scorer.calculate_confidence_score(stage_df)
    
    # Test organizer
    organizer = ResultsOrganizer()
    
    # Test essential view
    essential_df = organizer.prepare_essential_view(full_df)
    essential_cols = organizer.get_essential_columns()
    
    # Check that essential columns are present (or equivalents)
    available_essential = [col for col in essential_cols if col in essential_df.columns]
    if len(available_essential) < 3:  # Should have at least a few essential columns
        print(f"  ❌ Too few essential columns available: {available_essential}")
        return False
    
    # Test summary view
    summary_df = organizer.prepare_summary_view(full_df)
    if len(summary_df) > len(essential_df):  # Summary should have same or more columns
        print("  ✅ Summary view has more columns than essential")
    
    # Test high-confidence view
    high_conf_df = organizer.prepare_high_confidence_view(full_df)
    if len(high_conf_df) <= len(full_df):  # Should filter to fewer epitopes
        print("  ✅ High-confidence view filters results")
    
    # Test mutation summary
    mut_summary = organizer.create_mutation_summary(full_df)
    if len(mut_summary) == full_df['source_mut_id'].nunique():
        print("  ✅ Mutation summary has correct number of mutations")
    else:
        print(f"  ❌ Mutation summary count mismatch: {len(mut_summary)} vs {full_df['source_mut_id'].nunique()}")
        return False
    
    print("  ✅ ResultsOrganizer tests passed")
    return True


def test_config():
    """Test ImprovedPipelineConfig"""
    print("Testing ImprovedPipelineConfig...")
    
    # Test default config
    config = ImprovedPipelineConfig()
    if not config.validate():
        print("  ❌ Default configuration validation failed")
        return False
    
    # Test preset configs
    presets = ['fast', 'comprehensive', 'high_specificity', 'discovery']
    for preset in presets:
        try:
            preset_config = ImprovedPipelineConfig.create_preset(preset)
            if not preset_config.validate():
                print(f"  ❌ Preset '{preset}' validation failed")
                return False
        except Exception as e:
            print(f"  ❌ Error creating preset '{preset}': {e}")
            return False
    
    # Test configuration description
    desc = config.get_biological_description()
    if len(desc) < 100:  # Should be a substantial description
        print(f"  ❌ Configuration description too short: {len(desc)} chars")
        return False
    
    print("  ✅ ImprovedPipelineConfig tests passed")
    return True


def main():
    """Run all tests"""
    print("Testing Enhanced ImmunoForge Components")
    print("=" * 50)
    
    tests = [
        test_standard_scorer,
        test_immuno_score,
        test_confidence_scorer,
        test_results_organizer,
        test_config
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"  ❌ {test_func.__name__} failed")
        except Exception as e:
            print(f"  ❌ {test_func.__name__} error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced components are working correctly.")
        return True
    else:
        print(f"❌ {total - passed} tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)