"""
Simple MHCFlurry wrapper for MHC binding prediction
"""

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import logging
import warnings
logging.getLogger("tensorflow").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", message="Downcasting behavior in `replace` is deprecated", category=FutureWarning, module=r"mhcflurry\.amino_acid")
logging.getLogger("mhcflurry").setLevel(logging.ERROR)
logging.getLogger("mhcflurry").propagate = False

import pandas as pd
from typing import Dict, List

from .base import BaseTool

logger = logging.getLogger(__name__)

try:
    import mhcflurry
    MHCFLURRY_AVAILABLE = True
except ImportError:
    MHCFLURRY_AVAILABLE = False
    logger.warning("MHCFlurry not available. Install with: pip install mhcflurry")


class MHCFlurryTool(BaseTool):
    """Simple wrapper for MHCFlurry MHC binding predictions"""

    def __init__(self, peptide_lengths: List[int] = None, **kwargs):
        super().__init__(name='mhcflurry', **kwargs)
        
        if not MHCFLURRY_AVAILABLE:
            raise ImportError("MHCFlurry is not installed")
        
        self.peptide_lengths = peptide_lengths or [8, 9, 10, 11]
        
        try:
            self.affinity_predictor = mhcflurry.Class1AffinityPredictor.load()
            self.predictor_presentation = mhcflurry.Class1PresentationPredictor.load()

        except Exception as e:
            logger.error(f"Failed to load MHCFlurry models: {e}")
            logger.info("Download models with: mhcflurry-downloads fetch")
            raise

    def predict(self, proteins, nterm, cterm, alleles: List[str]) -> tuple:
        """
        Run MHCFlurry predictions on full proteins

        Parameters
        ----------
        proteins : Dict[str, str]
            Dictionary mapping protein IDs to full protein sequences
        alleles : List[str]
            Formatted allele list from epitope analyzer

        Returns
        -------
        tuple
            (presentation_results, binding_results) as DataFrames
        """
        return self._predict_presentation(proteins, nterm, cterm, alleles)

    def _predict_presentation(self, epitopes, nterm, cterm, alleles: List[str]) -> pd.DataFrame:
            all_results = []
            for allele in alleles:
                result = self.predictor_presentation.predict(
                    peptides=epitopes,
                    alleles=[allele],
                    n_flanks=nterm,
                    c_flanks=cterm,
                    include_affinity_percentile=True,
                    verbose=0
                )
                result.rename(columns={'peptide': 'epitope', 'best_allele': 'allele'}, inplace=True)
                all_results.append(result)

            return pd.concat(all_results, axis=0).drop_duplicates(subset=['epitope', 'allele'])

