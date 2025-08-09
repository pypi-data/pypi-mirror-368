"""
IEDB immunogenicity tool implementation - optimized version
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Tuple
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


class IEDBTool:
    """
    IEDB immunogenicity prediction tool

    Predicts immunogenicity based on amino acid properties and position-specific weights,
    with HLA allele-specific masking of anchor positions.
    """

    # Allele-specific mask positions (1-based, converted to 0-based internally)
    ALLELE_MASKS = {
        "H-2-Db": [1, 4, 8], "H-2-Dd": [1, 2, 4], "H-2-Kb": [1, 2, 8], "H-2-Kd": [1, 4, 8],
        "H-2-Kk": [1, 7, 8], "H-2-Ld": [1, 4, 8], "HLA-A0101": [1, 2, 8], "HLA-A0201": [0, 1, 8],
        "HLA-A0202": [0, 1, 8], "HLA-A0203": [0, 1, 8], "HLA-A0206": [0, 1, 8], "HLA-A0211": [0, 1, 8],
        "HLA-A0301": [0, 1, 8], "HLA-A1101": [0, 1, 8], "HLA-A2301": [1, 6, 8], "HLA-A2402": [1, 6, 8],
        "HLA-A2601": [0, 1, 8], "HLA-A2902": [1, 6, 8], "HLA-A3001": [0, 2, 8], "HLA-A3002": [1, 6, 8],
        "HLA-A3101": [0, 1, 8], "HLA-A3201": [0, 1, 8], "HLA-A3301": [0, 1, 8], "HLA-A6801": [0, 1, 8],
        "HLA-A6802": [0, 1, 8], "HLA-A6901": [0, 1, 8], "HLA-B0702": [0, 1, 8], "HLA-B0801": [1, 4, 8],
        "HLA-B1501": [0, 1, 8], "HLA-B1502": [0, 1, 8], "HLA-B1801": [0, 1, 8], "HLA-B2705": [1, 2, 8],
        "HLA-B3501": [0, 1, 8], "HLA-B3901": [0, 1, 8], "HLA-B4001": [0, 1, 8], "HLA-B4002": [0, 1, 8],
        "HLA-B4402": [1, 2, 8], "HLA-B4403": [1, 2, 8], "HLA-B4501": [0, 1, 8], "HLA-B4601": [0, 1, 8],
        "HLA-B5101": [0, 1, 8], "HLA-B5301": [0, 1, 8], "HLA-B5401": [0, 1, 8], "HLA-B5701": [0, 1, 8],
        "HLA-B5801": [0, 1, 8]
    }

    # Amino acid immunogenicity scores (Calis et al.)
    IMMUNOSCALE = {
        "A": 0.127, "C": -0.175, "D": 0.072, "E": 0.325, "F": 0.380,
        "G": 0.110, "H": 0.105, "I": 0.432, "K": -0.700, "L": -0.036,
        "M": -0.570, "N": -0.021, "P": -0.036, "Q": -0.376, "R": 0.168,
        "S": -0.537, "T": 0.126, "V": 0.134, "W": 0.719, "Y": -0.012
    }

    # Position-specific weights for 9-mers
    POSITION_WEIGHTS_9MER = np.array([0.00, 0.00, 0.10, 0.31, 0.30, 0.29, 0.26, 0.18, 0.00])

    def __init__(self):
        """Initialize IEDB tool with precomputed lookups"""
        # Convert immunoscale to numpy array for faster lookup
        self.aa_to_idx = {aa: i for i, aa in enumerate(self.IMMUNOSCALE.keys())}
        self.immunoscale_array = np.array(list(self.IMMUNOSCALE.values()))

        # Precompute normalized allele names
        self.normalized_alleles = self._precompute_allele_names()

    def _precompute_allele_names(self) -> Dict[str, str]:
        """Precompute all possible allele name variations"""
        normalized = {}

        for allele in self.ALLELE_MASKS:
            # Store original
            normalized[allele] = allele

            # Without HLA- prefix
            if allele.startswith('HLA-'):
                short = allele[4:]
                normalized[short] = allele
                normalized[f"{short[0]}*{short[1:3]}:{short[3:]}"] = allele  # A*02:01 format
                normalized[f"{short[0]}{short[1:3]}:{short[3:]}"] = allele   # A02:01 format

        return normalized

    def predict(self,
                data: Union[pd.DataFrame, List[str], str],
                allele: Optional[Union[str, List[str]]] = None,
                peptide_col: str = 'peptide',
                allele_col: Optional[str] = 'allele') -> pd.DataFrame:
        """
        Predict immunogenicity scores

        Parameters
        ----------
        data : DataFrame, list of peptides, or single peptide
            Input data containing peptides
        allele : str or list, optional
            HLA allele(s) for masking. If None, will look for allele_col in DataFrame
        peptide_col : str
            Column name for peptides in DataFrame
        allele_col : str
            Column name for alleles in DataFrame

        Returns
        -------
        pd.DataFrame
            DataFrame with peptide, allele (if provided), and iedb_score columns
        """
        # Convert input to DataFrame
        if isinstance(data, str):
            df = pd.DataFrame({peptide_col: [data]})
        elif isinstance(data, list):
            df = pd.DataFrame({peptide_col: data})
        elif isinstance(data, pd.DataFrame):
            df = data.copy()
        else:
            raise ValueError("Input must be string, list, or DataFrame")

        # Handle epitope/novel_epitope/seq column names
        if peptide_col not in df.columns:
            for alt_col in ['epitope', 'novel_epitope', 'seq']:
                if alt_col in df.columns:
                    peptide_col = alt_col
                    break
            else:
                raise ValueError(f"No peptide column '{peptide_col}' found")

        # Handle alleles
        if allele is not None:
            if isinstance(allele, str):
                df['allele'] = allele
            elif isinstance(allele, list):
                if len(allele) != len(df):
                    raise ValueError("Allele list must match number of peptides")
                df['allele'] = allele
        elif allele_col not in df.columns:
            df['allele'] = None

        # Vectorized scoring
        df['iedb_score'] = self._score_batch(df[peptide_col].values,
                                            df.get('allele', [None] * len(df)).values)

        # Return relevant columns
        result_cols = [peptide_col]
        if 'allele' in df.columns and df['allele'].notna().any():
            result_cols.append('allele')
        result_cols.append('iedb_score')

        # Preserve source_id if present
        if 'source_id' in df.columns:
            result_cols.insert(1, 'source_id')

        return df[result_cols]

    def _score_batch(self, peptides: np.ndarray, alleles: np.ndarray) -> np.ndarray:
        """Vectorized scoring of multiple peptides"""
        scores = np.zeros(len(peptides))

        # Group by peptide length and allele for efficient processing
        for i, (peptide, allele) in enumerate(zip(peptides, alleles)):
            if pd.isna(peptide) or not isinstance(peptide, str):
                continue

            scores[i] = self._score_single(peptide.upper(), allele)

        return np.round(scores, 5)

    @lru_cache(maxsize=10000)
    def _score_single(self, peptide: str, allele: Optional[str]) -> float:
        """Score a single peptide with caching"""
        # Validate peptide
        try:
            aa_indices = [self.aa_to_idx[aa] for aa in peptide]
        except KeyError as e:
            logger.warning(f"Unknown amino acid in peptide {peptide}: {e}")
            return 0.0

        # Get mask positions
        mask = self._get_mask(len(peptide), allele)

        # Get weights
        weights = self._get_weights(len(peptide))

        # Calculate score efficiently
        score = 0.0
        for pos, aa_idx in enumerate(aa_indices):
            if pos not in mask:
                score += weights[pos] * self.immunoscale_array[aa_idx]

        return score

    @lru_cache(maxsize=100)
    def _get_mask(self, peptide_length: int, allele: Optional[str]) -> Tuple[int, ...]:
        """Get mask positions for allele with caching"""
        if allele:
            # Normalize allele name
            normalized = self._normalize_allele(allele)
            if normalized in self.ALLELE_MASKS:
                # Filter positions that are within peptide length
                mask = tuple(pos for pos in self.ALLELE_MASKS[normalized]
                           if pos < peptide_length)
                if mask:
                    return mask

        # Default mask: first two and last position
        return (0, 1, peptide_length - 1) if peptide_length > 2 else tuple(range(peptide_length))

    def _normalize_allele(self, allele: str) -> Optional[str]:
        """Normalize allele name to standard format"""
        if not allele:
            return None

        # Remove common variations
        clean = allele.upper().replace('*', '').replace(':', '').replace('HLA-', '')

        # Try exact match first
        if allele in self.normalized_alleles:
            return self.normalized_alleles[allele]

        # Try without HLA prefix
        if clean in self.normalized_alleles:
            return self.normalized_alleles[clean]

        # Try adding HLA prefix
        hla_format = f"HLA-{clean}"
        if hla_format in self.normalized_alleles:
            return self.normalized_alleles[hla_format]

        logger.debug(f"Allele {allele} not found in predefined list")
        return None

    @lru_cache(maxsize=20)
    def _get_weights(self, peptide_length: int) -> np.ndarray:
        """Get position-specific weights for peptide length"""
        if peptide_length == 9:
            return self.POSITION_WEIGHTS_9MER

        elif peptide_length < 9:
            # Truncate weights for shorter peptides
            return self.POSITION_WEIGHTS_9MER[:peptide_length]

        else:
            # Extend weights for longer peptides
            # Keep first 5 positions, extend middle, keep last 4
            weights = np.zeros(peptide_length)
            weights[:5] = self.POSITION_WEIGHTS_9MER[:5]
            weights[-4:] = self.POSITION_WEIGHTS_9MER[-4:]

            # Fill middle positions with average weight
            if peptide_length > 9:
                middle_weight = 0.30  # Default middle weight
                weights[5:-4] = middle_weight

            return weights


# Example usage
if __name__ == "__main__":
    # Initialize tool
    iedb = IEDBTool()

    # Example 1: Single peptide
    score = iedb.predict("SIINFEKL", allele="H-2-Kb")
    print("Single peptide:", score)

    # Example 2: List of peptides
    peptides = ["SIINFEKL", "RGYVYQGL", "GILGFVFTL"]
    scores = iedb.predict(peptides, allele="HLA-A*02:01")
    print("\nList of peptides:", scores)

    # Example 3: DataFrame with peptide and allele columns
    df = pd.DataFrame({
        'peptide': ["SIINFEKL", "RGYVYQGL", "GILGFVFTL", "NLVPMVATV"],
        'allele': ["H-2-Kb", "HLA-A*02:01", "HLA-A0201", "HLA-A*02:01"],
        'source_id': ["P1", "P2", "P3", "P4"]
    })

    results = iedb.predict(df)
    print("\nDataFrame with alleles:", results)


