"""
Utility functions for epitope prediction
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any
import logging
import yaml
import json
from pathlib import Path
import re

logger = logging.getLogger(__name__)


def format_hla_codes(alleles: List[str]) -> List[str]:
    """
    Format HLA allele codes for NetMHCpan tool
    
    Parameters
    ----------
    alleles : List[str]
        List of HLA alleles in various formats
        
    Returns
    -------
    List[str]
        Formatted alleles for NetMHCpan (HLA-A02:01 format)
    """
    formatted = []
    
    for allele in alleles:
        # Handle different input formats
        if allele.startswith('HLA-'):
            # Already in correct format, just ensure colons
            clean_allele = allele.replace('HLA-', '')
            if ':' not in clean_allele and len(clean_allele) >= 5:
                # A0201 -> A02:01
                formatted.append(f"HLA-{clean_allele[0]}{clean_allele[1:3]}:{clean_allele[3:5]}")
            else:
                formatted.append(allele)
        elif '*' in allele:
            # A*02:01 format -> HLA-A02:01
            formatted.append(f"HLA-{allele}")
        elif len(allele) >= 5:
            # A0201 format -> HLA-A02:01
            formatted.append(f"HLA-{allele[0]}{allele[1:3]}:{allele[3:5]}")
        else:
            # Keep as is if format unclear
            formatted.append(allele)
    
    return formatted


def validate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate input dataframe has required columns

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe

    Returns
    -------
    pd.DataFrame
        Validated dataframe

    Raises
    ------
    ValueError
        If required columns are missing
    """
    required_columns = [
        'mut_id', 'isoform_id', 'isoform_prevalence',
        'reference_protein', 'variant_protein'
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"DataFrame missing required columns: {missing}")

    # Validate data types
    for col in ['reference_protein', 'variant_protein']:
        if not df[col].apply(lambda x: isinstance(x, str) or pd.isna(x)).all():
            raise ValueError(f"Column {col} must contain strings")

    return df