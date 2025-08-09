"""
Tests for the epitope prediction pipeline
"""

import pytest
import pandas as pd
import numpy as np

from immunoforge import (
    EpitopePipeline, PipelineConfig, EpitopeAnalyzer
)
from immunoforge.tools import BaseTool, register_tool


class TestPipeline:
    """Test the main pipeline functionality"""

    @pytest.fixture
    def sample_data(self):
        """Create sample test data"""
        return pd.DataFrame({
            'mut_id': ['MUT001', 'MUT002', 'MUT003'],
            'transcript_id': ['TRANS001', 'TRANS002', 'TRANS003'],
            'isoform_id': ['ISO001', 'ISO002', 'ISO003'],
            'isoform_prevalence': [0.8, 0.6, 0.9],
            'reference_protein': [
                'MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTL',
                'MVSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTL',
                'MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTL'
            ],
            'variant_protein': [
                'MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLV',
                'MVSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLX',
                'MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLY'
            ]
        })

    @pytest.fixture
    def mock_tool(self):
        """Create a mock tool for testing"""

        class MockTool(BaseTool):
            def predict(self, sequences, **kwargs):
                # Return mock predictions
                results = []
                if isinstance(sequences, pd.DataFrame):
                    for idx, row in sequences.iterrows():
                        results.append({
                            'epitope': row.get('novel_epitope', 'TESTEPITOPE'),
                            'score': np.random.rand(),
                            'source_id': row.get('source_id', 'TEST')
                        })
                else:
                    for seq in sequences:
                        results.append({
                            'epitope': seq[:9] if len(seq) >= 9 else seq,
                            'score': np.random.rand()
                        })
                return pd.DataFrame(results)

        return MockTool

    def test_pipeline_initialization(self):
        """Test pipeline initialization"""
        # Test with default config
        pipeline = EpitopePipeline(alleles=['A0201'])
        assert pipeline.config.nmer_length == 9
        assert pipeline.config.alleles == ['A0201']

        # Test with custom config
        config = PipelineConfig(
            nmer_length=12,
            alleles=['A0201', 'B0702'],
            tools={'mock': {}}
        )
        pipeline = EpitopePipeline(config=config)
        assert pipeline.config.nmer_length == 12
        assert len(pipeline.config.alleles) == 2

    def test_config_serialization(self):
        """Test config serialization"""
        config = PipelineConfig(
            nmer_length=10,
            alleles=['A0301'],
            tools={'test': {'param': 'value'}}
        )

        # Test to_dict
        config_dict = config.to_dict()
        assert config_dict['nmer_length'] == 10
        assert config_dict['tools']['test']['param'] == 'value'

        # Test from_dict
        config2 = PipelineConfig.from_dict(config_dict)
        assert config2.nmer_length == config.nmer_length
        assert config2.alleles == config.alleles

    def test_epitope_generation(self, sample_data):
        """Test epitope generation from sequences"""
        pipeline = EpitopePipeline(alleles=['A0201'], nmer_length=9)

        # Add source IDs
        sample_data = pipeline._add_source_ids(sample_data)

        # Generate epitopes
        epitopes_df = pipeline._generate_epitopes(sample_data)

        assert not epitopes_df.empty
        assert 'novel_epitope' in epitopes_df.columns
        assert 'source_id' in epitopes_df.columns
        assert 'epitope_prevalence' in epitopes_df.columns

        # Check that epitopes are the right length
        epitope_lengths = epitopes_df['novel_epitope'].str.len()
        assert (epitope_lengths == 9).all()

    def test_custom_tool_registration(self, mock_tool):
        """Test registering and using custom tools"""
        # Register custom tool
        register_tool('mock', mock_tool)

        # Use in pipeline
        pipeline = EpitopePipeline(alleles=['A0201'])
        assert 'mock' in pipeline.tools

    def test_pipeline_with_mock_tools(self, sample_data, mock_tool):
        """Test full pipeline with mock tools"""
        # Register mock tool
        register_tool('mock_predictor', mock_tool)

        # Create pipeline with mock tool
        pipeline = EpitopePipeline(
            tools=['mock_predictor'],
            nmer_length=9,
            alleles=['A0201']
        )

        # Process data
        results = pipeline.process(sample_data, progress_bar=False)

        assert not results.empty
        assert 'epitope' in results.columns
        assert 'source_mut_id' in results.columns
        assert 'combined_score' in results.columns


class TestAnalyzer:
    """Test the epitope analyzer functionality"""

    @pytest.fixture
    def sample_results(self):
        """Create sample results for testing"""
        np.random.seed(42)
        n = 100

        return pd.DataFrame({
            'source_mut_id': [f'MUT{i:03d}' for i in range(n)],
            'transcript_id': [f'TRANS{i:03d}' for i in range(n)],
            'isoform_id': [f'ISO{i:03d}' for i in range(n)],
            'epitope': [f'EPITOPE{i:02d}' for i in range(n)],
            'epitope_prevalence': np.random.uniform(0.5, 1.0, n),
            'processing_score': np.random.uniform(0.1, 0.9, n),
            'mhc_affinity': np.random.exponential(500, n),
            'mhc_presentation_score': np.random.uniform(0.1, 0.9, n),
            'tcell_binding_response': np.random.uniform(0.1, 0.8, n),
            'immunogenicity_score': np.random.uniform(0.1, 0.9, n)
        })

    def test_analyzer_initialization(self, sample_results):
        """Test analyzer initialization"""
        analyzer = EpitopeAnalyzer(sample_results)

        assert len(analyzer.results) == len(sample_results)
        assert 'combined_score' in analyzer.results.columns

    def test_top_epitopes(self, sample_results):
        """Test getting top epitopes"""
        analyzer = EpitopeAnalyzer(sample_results)

        # Get top 10 epitopes
        top = analyzer.get_top_epitopes(n=10)
        assert len(top) == 10

        # Check they're actually the top by score
        all_sorted = analyzer.results.sort_values('combined_score', ascending=False)
        assert top.iloc[0]['epitope'] == all_sorted.iloc[0]['epitope']

    def test_filtering(self, sample_results):
        """Test filtering functionality"""
        analyzer = EpitopeAnalyzer(sample_results)

        # Test single filter
        filtered = analyzer.filter_epitopes(min_processing_score=0.5)
        assert len(filtered) < len(sample_results)
        assert (filtered['processing_score'] >= 0.5).all()

        # Test multiple filters
        filtered = analyzer.filter_epitopes(
            min_processing_score=0.5,
            max_mhc_affinity=500,
            min_immunogenicity=0.3
        )
        assert (filtered['processing_score'] >= 0.5).all()
        assert (filtered['mhc_affinity'] <= 500).all()
        assert (filtered['immunogenicity_score'] >= 0.3).all()

    def test_summary_statistics(self, sample_results):
        """Test summary statistics generation"""
        analyzer = EpitopeAnalyzer(sample_results)

        # Overall summary
        summary = analyzer.summarize()
        assert 'processing_score' in summary.columns
        assert 'mean' in summary.index
        assert 'std' in summary.index

        # Grouped summary
        sample_results['group'] = ['A', 'B'] * 50
        analyzer = EpitopeAnalyzer(sample_results)
        grouped_summary = analyzer.summarize(groupby='group')
        assert len(grouped_summary) > 0

    def test_export(self, sample_results, tmp_path):
        """Test export functionality"""
        analyzer = EpitopeAnalyzer(sample_results)

        # Test CSV export
        csv_path = tmp_path / "results.csv"
        analyzer.export_results(csv_path, format='csv')
        assert csv_path.exists()

        # Load and verify
        loaded = pd.read_csv(csv_path)
        assert len(loaded) == len(sample_results)

        # Test Excel export
        excel_path = tmp_path / "results.xlsx"
        analyzer.export_results(excel_path, format='excel')
        assert excel_path.exists()


class TestTools:
    """Test individual tool implementations"""

    def test_epitope_filter(self):
        """Test epitope filter tool"""
        from immunoforge.tools import EpitopeFilter

        ef = EpitopeFilter(n=9)

        # Test n-mer generation
        sequence = "MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTL"
        nmers = ef.generate_nmers(sequence)
        assert len(nmers) == len(sequence) - 9 + 1
        assert all(len(nmer) == 9 for nmer in nmers)

        # Test unique epitope extraction
        reference = "MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTL"
        variant = "MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLV"

        unique = ef.get_unique_epitopes(reference, variant)
        assert len(unique) > 0
        assert all(epitope not in reference for epitope in unique)

    def test_base_tool_caching(self, tmp_path):
        """Test tool caching functionality"""
        from immunoforge.tools import BaseTool

        class CachingTool(BaseTool):
            def __init__(self, **kwargs):
                super().__init__(name='cache_test', **kwargs)
                self.call_count = 0

            def predict(self, sequences, **kwargs):
                self.call_count += 1
                return pd.DataFrame({
                    'sequence': sequences,
                    'score': [0.5] * len(sequences)
                })

        # Create tool with caching
        tool = CachingTool(cache_dir=tmp_path, enable_cache=True)

        # First call
        sequences = ['SEQ1', 'SEQ2']
        result1 = tool.predict_with_cache(sequences)
        assert tool.call_count == 1

        # Second call with same input should use cache
        result2 = tool.predict_with_cache(sequences)
        assert tool.call_count == 1  # Should not increase
        assert result1.equals(result2)

        # Different input should trigger new prediction
        result3 = tool.predict_with_cache(['SEQ3'])
        assert tool.call_count == 2

    def test_uniprot_blast_tool(self):
        """Test UniProt BLAST tool initialization"""
        from immunoforge.tools import UniProtBLASTTool
        
        # Test online BLAST configuration
        tool = UniProtBLASTTool(
            use_online_blast=True,
            identity_threshold=95.0,
            coverage_threshold=90.0
        )
        
        assert tool.use_online_blast is True
        assert tool.identity_threshold == 95.0
        assert tool.coverage_threshold == 90.0


class TestUtils:
    """Test utility functions"""

    def test_source_id_creation(self):
        """Test source ID creation"""
        from immunoforge.utils import create_source_id

        source_id = create_source_id('MUT001', 'TRANS001', 'ISO001', 0.8)
        assert source_id == 'MUT001|TRANS001|ISO001|0.8'

    def test_dataframe_validation(self):
        """Test dataframe validation"""
        from immunoforge.utils import validate_dataframe

        # Valid dataframe
        valid_df = pd.DataFrame({
            'mut_id': ['M1'],
            'transcript_id': ['T1'],
            'isoform_id': ['I1'],
            'reference_protein': ['MSKGEEL'],
            'variant_protein': ['MSKGEELV']
        })

        validated = validate_dataframe(valid_df)
        assert isinstance(validated, pd.DataFrame)

        # Missing required column
        invalid_df = pd.DataFrame({
            'mut_id': ['M1'],
            'transcript_id': ['T1']
        })

        with pytest.raises(ValueError):
            validate_dataframe(invalid_df)


class TestScoring:
    """Test scoring functionality"""

    def test_combined_scorer(self):
        """Test combined scoring"""
        from immunoforge.scoring import CombinedScorer

        # Create sample data
        df = pd.DataFrame({
            'processing_score': [0.8, 0.6, 0.7],
            'mhc_affinity': [100, 300, 200],
            'mhc_presentation_score': [0.9, 0.5, 0.7],
            'immunogenicity_score': [0.8, 0.4, 0.6]
        })

        scorer = CombinedScorer()
        result_df = scorer.calculate_combined_score(df)

        assert 'combined_score' in result_df.columns
        assert (result_df['combined_score'] >= 0).all()
        assert (result_df['combined_score'] <= 1).all()

    def test_custom_scorers(self):
        """Test custom scoring functions"""
        from immunoforge.scoring import (
            AffinityRankScorer, LengthPreferenceScorer,
            SequenceComplexityScorer, create_ensemble_score
        )

        # Create sample data
        df = pd.DataFrame({
            'epitope': ['YLQPRTFLL', 'SIINFEKL', 'AAAAAAAA'],
            'mhc_affinity': [50, 150, 500]
        })

        # Test individual scorers
        affinity_scorer = AffinityRankScorer()
        affinity_scores = affinity_scorer.score(df)
        assert len(affinity_scores) == len(df)

        length_scorer = LengthPreferenceScorer(preferred_lengths=[9])
        length_scores = length_scorer.score(df)
        assert len(length_scores) == len(df)

        complexity_scorer = SequenceComplexityScorer()
        complexity_scores = complexity_scorer.score(df)
        assert len(complexity_scores) == len(df)

        # Test ensemble scoring
        scorers = [affinity_scorer, length_scorer, complexity_scorer]
        ensemble_scores = create_ensemble_score(df, scorers)
        assert len(ensemble_scores) == len(df)


if __name__ == '__main__':
    pytest.main([__file__])