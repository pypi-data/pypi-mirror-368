"""
NetMHCpan tool wrapper for MHC binding prediction
"""

import subprocess
import tempfile
import os
import re
import pandas as pd
from io import StringIO
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import logging
import numpy as np

from .base import BaseTool
from ..utils import format_hla_codes
from ..config import DefaultConfig

logger = logging.getLogger(__name__)


class NetMHCpanTool(BaseTool):
    """Wrapper for NetMHCpan MHC binding predictions"""

    def __init__(
            self,
            executable: Optional[str] = None,
            tmpdir: Optional[str] = None,
            extra_flags: List[str] = None,
            rank_threshold: float = 2.0,
            **kwargs
    ):
        """
        Initialize NetMHCpan tool

        Parameters
        ----------
        executable : str
            Path to NetMHCpan executable
        tmpdir : str, optional
            Temporary directory
        extra_flags : list of str
            Additional NetMHCpan flags
        rank_threshold : float
            Maximum rank percentile
        mock_mode : bool
            If True, use mock data instead of real NetMHCpan (default True for development)
        """
        self.rank_threshold = rank_threshold
        
        # Use default executable if not provided
        if executable is None:
            executable = DefaultConfig.get_executable_path('netmhcpan')
        if executable is None:
            raise ValueError("NetMHCpan executable not configured. Set path in DefaultConfig or pass executable parameter.")

        self.executable = Path(executable)
        self.tmpdir = Path(tmpdir or DefaultConfig.get_temp_dir('netmhcpan'))
        self.tmpdir.mkdir(parents=True, exist_ok=True)
        self.extra_flags = extra_flags or ["-p", "-BA"]


        super().__init__(name='netmhcpan', **kwargs)

    def _validate_config(self):
        """Validate NetMHCpan configuration"""
        if self.executable and not self.executable.exists():
            logger.warning(f"NetMHCpan executable not found: {self.executable}. Predictions will fail unless using mock_mode=True")
            # Don't raise error here - let it fail during prediction with clearer error handling

    def predict(
            self,
            peptides: Union[pd.DataFrame, List[str]],
            alleles: List[str] = None,
            **kwargs
    ) -> pd.DataFrame:
        """
        Run NetMHCpan predictions

        Parameters
        ----------
        peptides : pd.DataFrame or list of str
            Peptides to predict
        alleles : list of str
            HLA alleles

        Returns
        -------
        pd.DataFrame
            Binding predictions
        """
        # Extract peptides from DataFrame if needed
        if isinstance(peptides, pd.DataFrame):
            if 'novel_epitope' in peptides.columns:
                peptide_list = peptides['novel_epitope'].unique().tolist()
            elif 'epitope' in peptides.columns:
                peptide_list = peptides['epitope'].unique().tolist()
            elif 'seq' in peptides.columns:
                peptide_list = peptides['seq'].unique().tolist()
            else:
                logger.warning("No epitope, novel_epitope, or seq column found in DataFrame")
                return pd.DataFrame()
        else:
            peptide_list = peptides

        if not peptide_list:
            return pd.DataFrame()

        # Default alleles if not provided
        if alleles is None:
            alleles = kwargs.get('alleles', ['HLA-A*02:01', 'HLA-B*07:02'])

        # Format alleles
        formatted_alleles = format_hla_codes(alleles)
        logger.debug(f"NetMHCpan: Input alleles: {alleles}, Formatted alleles: {formatted_alleles}")
        logger.debug(f"NetMHCpan: Peptides to predict: {peptide_list}")

        try:
            results = self._run_netmhcpan(peptide_list, formatted_alleles)
            logger.debug(f"NetMHCpan: Prediction results shape: {results.shape if not results.empty else 'Empty'}")
            if not results.empty:
                logger.debug(f"NetMHCpan: Result columns: {results.columns.tolist()}")
                logger.debug(f"NetMHCpan: First result: {results.iloc[0].to_dict()}")

            # Filter by rank threshold if specified
            # if self.rank_threshold and '%Rank_BA' in results.columns:
            #     results = results[results['%Rank_BA'] <= self.rank_threshold]

            results.rename(columns={'Peptide': 'epitope', 'MHC': 'allele'}, inplace=True)
            results.allele = results.allele.apply(
                lambda allele: allele.replace("*", "").replace('HLA-', '').replace(':', ''))
            results.drop(columns=['Core', 'Of', 'Gp', 'Gl', 'Ip', 'Il', 'Icore', 'Identity'], inplace=True)
            return results
            
        except FileNotFoundError as e:
            logger.error(f"NetMHCpan executable not found. Use mock_mode=True for testing: {e}")
            raise e
        except Exception as e:
            logger.error(f"NetMHCpan prediction failed: {e}")
            logger.error(f"NetMHCpan prediction failed with peptides: {peptide_list}")
            logger.error(f"NetMHCpan prediction failed with alleles: {formatted_alleles}")
            import traceback
            logger.error(f"NetMHCpan full traceback: {traceback.format_exc()}")
            return pd.DataFrame()

    def _run_netmhcpan(self, peptides: List[str], alleles: List[str]) -> pd.DataFrame:
        """Run NetMHCpan binding predictions on a list of peptides"""

        # Write peptides to a temp file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".pep",
            dir=str(self.tmpdir) if self.tmpdir else None,
            delete=True
        ) as pep_file:
            for p in peptides:
                pep_file.write(p + "\n")
            pep_file.flush()

            dfs = []
            # If no alleles specified, run once without -a
            allele_list = alleles or [None]
            for allele in allele_list:
                cmd = [str(self.executable)] + self.extra_flags
                if allele:
                    cmd += ["-a", allele.replace("*", "")]  # drop '*' if needed
                cmd += [pep_file.name]

                try:
                    raw = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
                    logger.debug(f"NetMHCpan raw output for {allele}:\n{raw.decode()}")
                except subprocess.CalledProcessError as e:
                    raise RuntimeError(
                        f"netMHCpan failed for allele {allele}: {e.output.decode()}"
                    )

                df = self._parse_output(raw)
                logger.debug(f"Parsed dataframe shape: {df.shape}, columns: {df.columns.tolist()}")
                if allele:
                    df["Allele"] = allele
                dfs.append(df)

        # Concatenate results for all alleles
        result = pd.concat(dfs, ignore_index=True)
        return result

    def _parse_output(self, raw: bytes) -> pd.DataFrame:
        """Parse netMHCpan stdout into a DataFrame"""
        text = raw.decode('utf-8')
        # Split on dashed separator (>=80 dashes)
        parts = re.split(r"\n[-]{80,}\n", text)
        if len(parts) < 3:
            raise ValueError("Unexpected netMHCpan output format")
        body = parts[1] + "\n" + parts[2]
        # Normalize spacing to commas
        body = re.sub(r"[ ]+", ",", body)
        body = body.replace("\n,", "\n")
        # Read into DataFrame
        df = pd.read_csv(StringIO(body), )
        df.columns = [
            'Pos', 'MHC', 'Peptide', 'Core', 'Of', 'Gp', 'Gl', 'Ip', 'Il',
            'Icore', 'Identity', 'Score_EL', 'Rank_EL', 'Score_BA',
            'Rank_BA', 'Affinity_nM', 'spacer', 'BindLevel'
        ]
        # Drop unnamed index column if present
        # unnamed = [c for c in df.columns if c.startswith("Unnamed")]
        # print(unnamed)
        # if unnamed:
        #     df = df.drop(columns=unnamed)
        if 'Peptide' in df.columns:
            df['Peptide'] = df['Peptide'].str.strip()
        return df



        # result.rename(columns={'Peptide': 'epitope', 'MHC': 'allele'})
        # result.allele = result.allele.apply(lambda allele: allele.replace("*", "").replace('HLA-', '').replace(':', ''))
        # results.drop(columns=['Core','Of','Gp', 'Gl', 'Ip', 'Il', 'Icore', 'Identity'], inplace=True)