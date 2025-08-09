import sys
from tqdm import tqdm

sys.path.append('/tamir2/nicolaslynn/tools/DeepImmuno/')
from deepimmuno_cnn import computing_s


class DeepImmunoCNNTool:
    """Wrapper for DeepImmuno CNN predictions with allele formatting and long peptide handling"""

    @staticmethod
    def format_allele(allele):
        """Ensure allele has HLA- prefix"""
        if not allele.startswith('HLA-'):
            return f'HLA-{allele}'
        return allele

    def predict(self, peptides, alleles):
        """
        Predict immunogenicity scores

        Parameters:
        - peptides: list of peptide sequences
        - alleles: list of HLA alleles (with or without HLA- prefix)

        Returns:
        - list of scores (averaged for peptides > 10 aa)
        """
        if len(peptides) != len(alleles):
            raise ValueError("peptides and alleles must have same length")

        # Format alleles
        formatted_alleles = [self.format_allele(a) for a in alleles]


        if all([len(v) == 10 for v in peptides]):
            final_scores = computing_s(peptides, formatted_alleles)
            return final_scores

        else:
            # Process each peptide-allele pair
            final_scores = []
            for peptide, allele in tqdm(zip(peptides, formatted_alleles), total=len(peptides)):
                if len(peptide) <= 10:
                    # Direct scoring for short peptides
                    score = computing_s([peptide], [allele])[0]
                else:
                    # For long peptides, score all 10-mer windows and average
                    windows = []
                    for i in range(len(peptide) - 9):
                        windows.append(peptide[i:i + 10])

                    # Score all windows with the same allele
                    window_scores = computing_s(windows, [allele] * len(windows))
                    score = sum(window_scores) / len(window_scores)

                final_scores.append(score)

            return final_scores