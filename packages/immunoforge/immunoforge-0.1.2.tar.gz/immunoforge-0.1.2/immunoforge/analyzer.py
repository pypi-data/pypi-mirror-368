import pandas as pd
import numpy as np
from scipy.stats import gmean, pearsonr
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations
import os


class EpitopeImmunogenicityPipeline:
    def __init__(self, threshold=0.05):
        self.threshold = threshold
        self.source_features = ['mut_id', 'transcript_id', 'isoform_id', 'isoform_prevalence']
        self.epitope_features = ['epitope', 'allele']

        self.processing_cols = ['processing_score', 'netchop_score']
        self.presentation_cols = ['Rank_EL', 'Rank_BA', 'presentation_percentile', 'affinity_percentile']
        self.immunogenicity_cols = ['iedb_score', 'deepimmuno_score']
        self.core_features = self.processing_cols + self.presentation_cols + self.immunogenicity_cols

    def harmonize_features(self, df):
        df = df.copy()
        for col in ['processing_score', 'netchop_score', 'iedb_score', 'deepimmuno_score']:
            if col in df.columns:
                df[col] = df[col].clip(0, 1)
        for col in ['Rank_EL', 'Rank_BA', 'presentation_percentile', 'affinity_percentile']:
            if col in df.columns:
                df[col] = 1 - (df[col] / 100).clip(0, 1)
        return df

    def compute_feature_scores(self, df):
        for cols, name in zip(
            [self.processing_cols, self.presentation_cols, self.immunogenicity_cols],
            ['processing_score', 'presentation_score', 'immunogenicity_score']
        ):
            valid_cols = [c for c in cols if c in df.columns]
            if valid_cols:
                df[name] = gmean(df[valid_cols].fillna(0) + 1e-10, axis=1)
            else:
                df[name] = 0.5
        return df

    def compute_combined_score(self, df):
        df['combined_score'] = (
            gmean([df['processing_score'], df['presentation_score'], df['immunogenicity_score']], axis=0) *
            df.get('isoform_prevalence', 1)
        )
        return df

    def aggregate_epitopes(self, df):
        # Remove allele-level information to aggregate across alleles
        epitope_cols = [col for col in self.source_features if col in df.columns]
        score_cols = ['processing_score', 'presentation_score', 'immunogenicity_score', 'combined_score']
        if 'min_missmatches' in df.columns:
            score_cols.append('min_missmatches')

        agg_dict = {col: 'first' for col in epitope_cols}
        agg_dict.update({col: gmean for col in score_cols})

        # Group only by epitope, not allele
        epitope_df = df.groupby('epitope').agg(agg_dict).reset_index()
        epitope_df = epitope_df.sort_values('combined_score', ascending=False).reset_index(drop=True)
        epitope_df.insert(0, 'epitope_index', ['epitope_' + str(i + 1) for i in range(len(epitope_df))])
        return epitope_df



    def filter_by_threshold(self, df):
        return df[df['combined_score'] >= self.threshold].copy()

    def aggregate_mutations(self, df):
        agg_dict = {
            'combined_score': 'sum',
            'epitope': 'count'
        }
        for col in self.processing_cols + self.presentation_cols + self.immunogenicity_cols:
            if col in df.columns:
                agg_dict[col] = 'mean'

        mut_agg = df.groupby('mut_id').agg(agg_dict).rename(columns={'epitope': 'n_epitopes'})
        mut_agg['mutation_immunogenicity'] = mut_agg['combined_score']
        mut_agg = mut_agg.sort_values('mutation_immunogenicity', ascending=False).reset_index()
        mut_agg.insert(0, 'mutation_index', ['mutation_' + str(i + 1) for i in range(len(mut_agg))])
        return mut_agg


    def create_mutation_libraries(self, df):
        return {
            mut_id: group.sort_values('combined_score', ascending=False)
            for mut_id, group in df.groupby('mut_id')
        }




    def create_appendix_data(self, extra_mutation_descriptions=None):
        from datetime import datetime

        rows = [
            {'Section': 'Metadata', 'Field': 'Execution Date', 'Description': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            {'Section': 'Metadata', 'Field': 'Data Recipient', 'Description': 'Specify the recipient here'},
            {'Section': 'Metadata', 'Field': 'Notes', 'Description': 'General notes about this analysis'},
            {'Section': '', 'Field': '', 'Description': ''},  # spacer
        ]

        # Base descriptions
        descriptions = {
            'Epitope Summary': {
                'epitope': 'Peptide sequence generated from variant protein',
                'source_mut_id': 'Unique ID linking peptide back to its mutation/transcript',
                'avg_prevalence': 'Average prevalence of this epitope across all isoforms/samples',
                'processing_score': 'Proteasome cleavage score (0–1)',
                'presentation_score': 'MHC presentation probability (0–1)',
                'binding_score': 'T-cell binding score (0–1)',
                'gmean_score': 'Geometric mean of all scores',
                'prevalence_in_tumor': 'Fraction of tumors expressing this epitope',
                'missmatches_to_nearest_ref': 'AA differences from nearest reference peptide'
            },
            'Mutation Summary': {
                'source_mut_id': 'Mutation or transcript ID',
                'prevalence_in_tumor': 'Fraction of tumors carrying this mutation',
                'lung_cancer_patients': 'Number of patients with this mutation',
                'immunogenic_potential': 'Summed score of all immunogenic epitopes',
                'num_targetable_epitopes': 'Count of high-scoring epitopes from this mutation'
            }
        }

        # Inject extra descriptions
        if extra_mutation_descriptions:
            descriptions['Mutation Summary'].update(extra_mutation_descriptions)

        # Flatten to row format
        for section, fields in descriptions.items():
            for field, desc in fields.items():
                rows.append({'Section': section, 'Field': field, 'Description': desc})

        return pd.DataFrame(rows)


    def process(self, df):
        df = self.harmonize_features(df)
        df = self.compute_feature_scores(df)
        df = self.compute_combined_score(df)
        epitope_summary = self.aggregate_epitopes(df)
        epitope_filtered = self.filter_by_threshold(epitope_summary)
        mutation_summary = self.aggregate_mutations(epitope_filtered)
        libraries = self.create_mutation_libraries(epitope_filtered)
        return {
            'epitope_summary': epitope_summary,
            'epitope_filtered': epitope_filtered,
            'mutation_summary': mutation_summary,
            'libraries': libraries,
            'full_df': df
        }

    def write_to_excel(self, results, filename='immunogenicity_results.xlsx', write_mutation_libraries=False, mutation_metadata=None, case_metadata=None):
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            self.create_appendix_data().to_excel(writer, sheet_name='Appendix', index=False)

            results['epitope_filtered'].to_excel(writer, sheet_name='Epitope Summary', index=False)

            mutation_summary = results['mutation_summary']
            if mutation_metadata is not None:
                mutation_summary = mutation_summary.merge(mutation_metadata, on='mut_id', how='left')

            mutation_summary.drop(columns=['combined_score'], errors='ignore').to_excel(writer, sheet_name='Mutation Summary', index=False)

            # Map mut_id → mutation_index
            mutation_index_map = dict(zip(results['mutation_summary']['mut_id'], results['mutation_summary']['mutation_index']))

            # Select libraries
            if isinstance(write_mutation_libraries, int):
                top_mutations = results['mutation_summary'].nlargest(write_mutation_libraries, 'mutation_immunogenicity')['mut_id']
                libraries_to_write = {mut_id: results['libraries'][mut_id] for mut_id in top_mutations if mut_id in results['libraries']}
            elif write_mutation_libraries is True:
                libraries_to_write = dict(list(results['libraries'].items())[:50])
            else:
                libraries_to_write = {}

            # Write each library
            for mut_id, lib_df in libraries_to_write.items():
                sheet_name = mutation_index_map.get(mut_id, f'Library_{mut_id}')[:31]
                lib_df.to_excel(writer, sheet_name=sheet_name, index=False)

    def _plot_feature_correlations(self, df, save_analysis=None):
        groups = {
            'Processing': [c for c in self.processing_cols if c in df.columns],
            'Presentation': [c for c in self.presentation_cols if c in df.columns],
            'Immunogenicity': [c for c in self.immunogenicity_cols if c in df.columns]
        }

        for group, cols in groups.items():
            for x, y in combinations(cols, 2):
                self._plot(df, x, y, group, save_analysis)


    def _plot(self, df, x, y, group='', save_analysis=None):
        plt.figure(figsize=(5, 5))
        sns.scatterplot(data=df, x=x, y=y, s=20, alpha=0.6)
        corr, pval = pearsonr(df[x].fillna(0), df[y].fillna(0))
        plt.title(f'{group}: {x} vs {y}\nPearson r = {corr:.2f}, p = {pval:.2g}')
        sns.despine()
        plt.tight_layout()
        if save_analysis:
            os.makedirs(save_analysis, exist_ok=True)
            plt.savefig(os.path.join(save_analysis, f'{group}_{x}_vs_{y}.png'))
        else:
            plt.show()
        plt.close()


