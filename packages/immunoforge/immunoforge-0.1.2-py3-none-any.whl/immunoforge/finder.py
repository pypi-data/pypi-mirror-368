"""
Epitope finder pipeline for prediction

This pipeline focuses solely on running tools and returning raw outputs.
All scoring and analysis is handled separately by the EpitopeAnalyzer.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Union, Any
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from immunoforge.tools import get_tool_instance
from immunoforge.utils import validate_dataframe

logger = logging.getLogger(__name__)


class EpitopePipeline:
    """
    Epitope finder pipeline that runs tools and returns raw outputs
    """
    def __init__(
        self,
        alleles,
        nmer_length=9,
        parallel=True,
        n_workers=4,
        **kwargs
    ):
        self.tools_list = ['netchop', 'netmhcpan', 'mhcflurry', 'iedb', 'deepimmuno']
        self.alleles = alleles
        self.nmer_length = [nmer_length] if isinstance(nmer_length, int) else nmer_length
        self.parallel = parallel
        self.n_workers = n_workers
        self.tools = {}
        self.display_flag = kwargs.get('display_flag', False)
        self._initialize_tools(**kwargs)
        logger.info(f"Initialized pipeline with all tools: {self.tools_list}")


    def _initialize_tools(self, **kwargs):
        """Initialize all configured tools"""
        for tool_name in self.tools_list:
            try:
                # Get tool-specific config
                tool_config = kwargs.get(f'{tool_name}_config', {})

                # Special handling for MHCflurry peptide lengths
                if tool_name == 'mhcflurry' and 'peptide_lengths' not in tool_config:
                    tool_config['peptide_lengths'] = self.nmer_length

                tool_instance = get_tool_instance(tool_name, **tool_config)
                self.tools[tool_name] = tool_instance
                logger.debug(f"Initialized tool: {tool_name}")

            except Exception as e:
                logger.warning(f"Failed to initialize tool {tool_name}: {e}")
                raise


    def process(self, df: pd.DataFrame, progress_bar: bool = True) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Process protein sequences and return combined raw outputs with feature metadata

        Returns:
            tuple: (combined_results_df, feature_metadata_df)
        """
        # Prepare formatted alleles for all tools at the beginning

        # 1. Generate epitopes
        logger.info("Generating epitopes...")
        combined = self.generate_epitopes(df)
        peptide_distances = self._run_pepmatch(combined.epitope.unique().tolist())
        combined = pd.merge(combined, peptide_distances, on='epitope', how='left')
        print(f"Dealing with {combined.epitope.nunique()} unique epitopes across {len(self.alleles)} alleles.")

        if self.display_flag:
            display(combined)

        # 3. NetChop
        logger.info("Running NetChop...")
        netchop_df = self._run_netchop(df, progress_bar)
        if self.display_flag:
            display(netchop_df)

        combined = combined.merge(
            netchop_df.rename(columns={'score': 'netchop_score'}),
            on=['mut_id', 'epitope'], how='left'
        )

        # 4. Expand for alleles
        alleles_df = pd.DataFrame({'allele': self.alleles})
        combined = combined.assign(key=1).merge(alleles_df.assign(key=1), on='key').drop('key', axis=1)
        if self.display_flag:
            display(combined)

        # 5. NetMHCpan
        logger.info("Running netmhcpan...")
        netmhcpan_out = self._run_netmhcpan(combined, self.alleles)
        # netmhcpan_out['allele'] = netmhcpan_out['MHC'].apply(lambda allele: allele.replace('HLA-', '').replace(':', ''))

        if self.display_flag:
            display(netmhcpan_out)

        combined = combined.merge(
            netmhcpan_out, on=['epitope', 'allele'], how='left'
        )

        # 6. MHCflurry
        logger.info("Running mhcflurry...")
        mhcflurry_out = self._run_mhcflurry(combined.epitope.tolist(), combined.nterm.tolist(), combined.cterm.tolist(), self.alleles)
        mhcflurry_out = mhcflurry_out[mhcflurry_out.epitope.isin(combined.epitope.tolist())]
        mhcflurry_out = mhcflurry_out.drop(columns='sample_name').drop_duplicates()

        if self.display_flag:
            display(mhcflurry_out)

        combined = combined.merge(
            mhcflurry_out, on=['epitope', 'allele'], how='left'
        ).drop_duplicates(subset=['mut_id', 'epitope', 'allele'])


        if self.display_flag:
            display(combined)

        # 7. IEDB
        logger.info("Calculating IEDB scores...")
        combined['iedb_score'] = self.tools['iedb'].predict(
            combined,
            peptide_col='epitope',
            allele_col='allele'
        ).iedb_score


        # 8. DeepImmuno
        logger.info("Calculating DeepImmuno scores...")
        # Usage:

        combined['deepimmuno_score'] = self.tools['deepimmuno'].predict(
            combined['epitope'].tolist(),
            combined['allele'].tolist()
        )


        # 9. Create feature metadata DataFrame
        feature_metadata = self._create_feature_metadata()

        # 10. Deduplicate and return
        logger.info("Deduplicating results...")
        return combined, feature_metadata

    @staticmethod
    def _create_feature_metadata() -> pd.DataFrame:
        """Create a DataFrame describing all features and their sources"""
        metadata = [
            {'feature': 'epitope', 'tool': 'general', 'description': 'Peptide sequence', 'type': 'identifier'},
            {'feature': 'allele', 'tool': 'general', 'description': 'HLA allele', 'type': 'identifier'},
            {'feature': 'mut_id', 'tool': 'general', 'description': 'Mutation identifier', 'type': 'identifier'},
            {'feature': 'nmer_length', 'tool': 'general', 'description': 'Length of epitope', 'type': 'metadata'},

            {'feature': 'netchop_score', 'tool': 'netchop', 'description': 'Proteasomal cleavage score (0-1, higher is better)', 'type': 'score'},

            {'feature': '%Rank_EL', 'tool': 'netmhcpan', 'description': 'Eluted ligand percentile rank (0-100, lower is better)', 'type': 'percentile'},
            {'feature': '%Rank_BA', 'tool': 'netmhcpan', 'description': 'Binding affinity percentile rank (0-100, lower is better)', 'type': 'percentile'},

            {'feature': 'affinity_percentile', 'tool': 'mhcflurry', 'description': 'Binding affinity percentile (0-100, lower is better)', 'type': 'percentile'},
            {'feature': 'processing_score', 'tool': 'mhcflurry', 'description': 'Antigen processing score (0-1, higher is better)', 'type': 'score'},
            {'feature': 'presentation_score', 'tool': 'mhcflurry', 'description': 'Overall presentation score (0-1, higher is better)', 'type': 'score'},
            {'feature': 'presentation_percentile', 'tool': 'mhcflurry', 'description': 'Presentation percentile (0-100, lower is better)', 'type': 'percentile'},

            {'feature': 'iedb_score', 'tool': 'iedb', 'description': 'IEDB immunogenicity score (higher is more immunogenic)', 'type': 'score'},

            {'feature': 'deepimmuno_score', 'tool': 'deepimmuno', 'description': 'DeepImmuno immunogenicity probability (0-1, higher is better)', 'type': 'probability'},
        ]

        return pd.DataFrame(metadata)

    def generate_epitopes(self, df: pd.DataFrame) -> pd.DataFrame:
        epitopes = []
        for i, row in df.iterrows():
            # Skip rows with invalid protein sequences (NaN, None, or non-string values)
            if pd.isna(row.reference_protein) or pd.isna(row.variant_protein):
                logger.warning(f"Skipping row {i} (mut_id: {row.mut_id}) due to missing protein sequences")
                continue
            if not isinstance(row.reference_protein, str) or not isinstance(row.variant_protein, str):
                logger.warning(f"Skipping row {i} (mut_id: {row.mut_id}) due to non-string protein sequences")
                continue
            
            region_of_interest_ref, region_of_interest_var = self.focus_on_differences(row.reference_protein, row.variant_protein, self.nmer_length[0])
            ref = self.generate_nmers(region_of_interest_ref, k=self.nmer_length[0], metadata={'mut_id': row.mut_id, 'transcript_id': row.transcript_id, 'isoform_id': row.isoform_id, 'isoform_prevalence': row.isoform_prevalence})
            var = self.generate_nmers(region_of_interest_var, k=self.nmer_length[0], metadata={'mut_id': row.mut_id, 'transcript_id': row.transcript_id, 'isoform_id': row.isoform_id, 'isoform_prevalence': row.isoform_prevalence})
            var = var[~var.epitope.isin(ref.epitope.tolist())]
            epitopes.append(var)

        if not epitopes:
            logger.warning("No valid epitopes generated - all rows had invalid protein sequences")
            return pd.DataFrame()
        return pd.concat(epitopes)


    def focus_on_differences(self, s1, s2, k):
        # return s1, s2
        import difflib
        matcher = difflib.SequenceMatcher(None, s1, s2)
        blocks = matcher.get_matching_blocks()

        # First block is prefix, last meaningful block is suffix
        prefix = blocks[0].size if blocks[0].a == 0 and blocks[0].b == 0 else 0
        suffix = blocks[-2].size if blocks[-2].a + blocks[-2].size == len(s1) else 0

        start = max(0, prefix - k)
        return s1[start:len(s1) - suffix + k], s2[start:len(s2) - suffix + k]

    def generate_nmers(self, seq, k, metadata):
        epitopes = [seq[i:i + k] for i in range(len(seq) - k + 1)]
        df = pd.DataFrame({'epitope': epitopes})
        for k, v in metadata.items():
            df[k] = v
        return df


    def _run_netchop(self, df: pd.DataFrame, progress_bar: bool = True) -> pd.DataFrame:
        """Run NetChop on variant proteins to get cleavage scores"""
        tool = self.tools['netchop']
        if progress_bar:
            logger.debug("Running NetChop with progress tracking")
        all_results = []

        for idx, row in df.iterrows():
            sequence = row.get('variant_protein', '')
            if not isinstance(sequence, str) or len(sequence) < min(self.nmer_length):
                continue

            mut_id = row.get('mut_id', f'seq_{idx}')

            try:
                seq_df = pd.DataFrame({
                    'mut_id': [mut_id],
                    'variant_protein': [sequence]
                })

                # Get scores for each nmer length
                for nmer_len in self.nmer_length:
                    nmer_scores = tool.predict(seq_df, n=nmer_len)
                    if not nmer_scores.empty:
                        nmer_scores['nmer_length'] = nmer_len
                        nmer_scores['mut_id'] = mut_id
                        # Rename seq to epitope for consistency
                        if 'seq' in nmer_scores.columns:
                            nmer_scores = nmer_scores.rename(columns={'seq': 'epitope'})
                        all_results.append(nmer_scores)

            except Exception as e:
                logger.warning(f"NetChop failed for {mut_id}: {e}")

        if all_results:
            if self.display_flag:
                display(pd.concat(all_results))
            return pd.concat(all_results)
        return pd.DataFrame()


    def _run_netmhcpan(self, epitopes_df: pd.DataFrame, formatted_alleles: List[str]) -> pd.DataFrame: #allele_mapping: Dict[str, str], progress_bar: bool = True
        """Run NetMHCpan predictions on epitopes"""
        tool = self.tools['netmhcpan']
        unique_epitopes = epitopes_df[['epitope']].drop_duplicates()
        return tool.predict(unique_epitopes, alleles=formatted_alleles)

    def _run_mhcflurry(self, epitopes, nterm, cterm, alleles) -> pd.DataFrame: #allele_mappings['mhcflurry'] , progress_bar: bool = True
        """Run MHCFlurry predictions on variant proteins"""
        presentation_results = self.tools['mhcflurry'].predict(epitopes, nterm, cterm, alleles)
        return presentation_results


    def _run_pepmatch(self, epitopes):
        from scipy.stats.mstats import gmean
        from pepmatch import Matcher
        import tempfile

        human_proteome_path = '/tamir2/nicolaslynn/data/UniProt/raw_downloads/UP000005640_9606.fasta'

        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            temp_fasta = f.name
            for i, epitope in enumerate(epitopes):
                f.write(f">epitope_{i}\n{epitope}\n")

        res = Matcher(
            temp_fasta,
            human_proteome_path,
            max_mismatches=12,
            k=4,  # let it pick k = peptide length for each query
            output_format='dataframe'
        ).match().to_pandas().rename(columns={'Mismatches': 'mismatches', 'Query Sequence': 'epitope'})


        best = (
            res
            .groupby('epitope')['mismatches']
            .min()
            .reset_index()
            .rename(columns={'mismatches': 'min_mismatches'})
        )
        return best

