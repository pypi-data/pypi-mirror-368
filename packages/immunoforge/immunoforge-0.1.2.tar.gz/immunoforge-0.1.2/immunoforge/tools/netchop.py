"""
NetChop tool wrapper for proteasomal cleavage prediction
"""

import subprocess
import logging
import tempfile
from pathlib import Path
import pandas as pd
import numpy as np
import os
from typing import List, Optional, Dict, Any

from .base import BaseTool
from ..config import DefaultConfig

logger = logging.getLogger(__name__)


class NetChopTool(BaseTool):
    """Wrapper for NetChop proteasomal cleavage prediction"""

    def __init__(
            self,
            executable: Optional[str] = None,
            model_version: int = 0,
            threshold: float = 0.5,
            min_length: int = 8,
            tmpdir: Optional[str] = None,
            **kwargs
    ):
        """
        Initialize NetChop tool

        Parameters
        ----------
        executable : str
            Path to NetChop executable
        model_version : int
            0 for Cterm3.0, 1 for 20S-3.0
        threshold : float
            Cleavage threshold
        min_length : int
            Minimum epitope length
        tmpdir : str, optional
            Temporary directory
        """
        # Use default executable if not provided
        if executable is None:
            executable = DefaultConfig.get_executable_path('netchop')
        if executable is None:
            raise ValueError("NetChop executable not configured. Set path in DefaultConfig or pass executable parameter.")
        
        self.executable = Path(executable)
        self.model_version = model_version
        self.threshold = threshold
        self.min_length = min_length
        self.tmpdir = Path(tmpdir or DefaultConfig.get_temp_dir('netchop'))
        self.tmpdir.mkdir(parents=True, exist_ok=True)

        super().__init__(name='netchop', **kwargs)

    def _validate_config(self):
        """Validate NetChop configuration"""
        if not self.executable.exists():
            raise FileNotFoundError(f"NetChop executable not found: {self.executable}")

        if self.model_version not in (0, 1):
            raise ValueError("model_version must be 0 or 1")

    def predict(self, sequences: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """
        Run NetChop predictions

        Parameters
        ----------
        sequences : pd.DataFrame
            DataFrame with protein sequences

        Returns
        -------
        pd.DataFrame
            Cleavage scores for epitopes
        """
        results = []

        # Process each protein sequence
        for idx, row in sequences.iterrows():
            if 'variant_protein' in row:
                sequence = row['variant_protein']
            elif 'sequence' in row:
                sequence = row['sequence']
            else:
                continue

            if not isinstance(sequence, str) or len(sequence) < self.min_length:
                continue

            try:
                # Get cleavage scores
                scores = self._run_netchop([sequence])[0]

                # Score fixed n-mers
                n = kwargs.get('n', 9)
                nmer_scores = self._score_fixed_nmers(sequence, scores, n)

                # Add source information if available
                for col in ['mut_id', 'source_id', 'source_mut_id']:
                    if col in row:
                        nmer_scores[col] = row[col]
                        break

                results.append(nmer_scores)

            except Exception as e:
                logger.warning(f"NetChop failed for sequence {idx}: {e}")

        if results:
            return pd.concat(results, ignore_index=True)
        else:
            return pd.DataFrame()

    def _run_netchop(self, sequences: List[str]) -> List[List[float]]:
        """Run NetChop on sequences"""
        # Write sequences to temporary FASTA
        with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.fasta',
                dir=self.tmpdir,
                delete=False
        ) as f:
            for i, seq in enumerate(sequences):
                f.write(f">seq_{i}\n{seq}\n")
            temp_file = f.name

        try:
            # Run NetChop
            cmd = [
                str(self.executable),
                "-v", str(self.model_version),
                temp_file
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            # Parse output
            return self._parse_output(result.stdout)

        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def _parse_output(self, output: str) -> List[List[float]]:
        """Parse NetChop output using same logic as working implementation"""
        line_iterator = iter(output.split("\n"))
        scores = []
        
        for line in line_iterator:
            if "pos" in line and 'AA' in line and 'score' in line:
                scores.append([])
                try:
                    next_line = next(line_iterator)
                    if "----" not in next_line:
                        raise ValueError("Dashes expected")
                    line = next(line_iterator)
                    while '-------' not in line and line.strip():
                        parts = line.split()
                        if len(parts) >= 4:
                            try:
                                score = float(parts[3])
                                scores[-1].append(score)
                            except (ValueError, IndexError):
                                pass
                        try:
                            line = next(line_iterator)
                        except StopIteration:
                            break
                except StopIteration:
                    break
        
        return scores

    def _score_fixed_nmers(
            self,
            sequence: str,
            scores: List[float],
            n: int = 9
    ) -> pd.DataFrame:
        """Score fixed-length n-mers"""
        if len(sequence) != len(scores):
            logger.warning(f"Sequence length ({len(sequence)}) != scores length ({len(scores)})")
            return pd.DataFrame()

        if len(sequence) < n:
            return pd.DataFrame()

        records = []
        for i in range(len(sequence) - n + 1):
            j = i + n
            nmer = sequence[i:j]

            # Score based on cleavage at start and end positions
            # Higher cleavage probability at boundaries = better processing
            start_score = scores[i] if i < len(scores) else 0
            end_score = scores[j - 1] if j - 1 < len(scores) else 0

            # Penalize internal cleavages
            internal_scores = scores[i + 1:j - 1] if j - 1 > i + 1 else []
            internal_penalty = np.mean(internal_scores) if internal_scores else 0

            # Combined score
            score = (start_score + end_score) / 2 - internal_penalty * 0.5
            score = max(0, min(1, score))  # Normalize to [0, 1]

            if j + 3 < len(sequence):
                cterm = sequence[j:j + 3]
            else:
                cterm = 'AAA'

            if i - 3 > 0:
                nterm = sequence[i - 3:i]
            else:
                nterm = 'AAA'

            records.append({
                'seq': nmer,
                'start': i,
                'end': j,
                'score': score,
                'start_cleavage': start_score,
                'end_cleavage': end_score,
                'internal_penalty': internal_penalty,
                'nterm': nterm,
                'cterm': cterm
            })

        return pd.DataFrame(records)