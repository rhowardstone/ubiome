import sys
from scipy.spatial.distance import braycurtis as BC
from utils import read_rosetta_indexed
import pandas as pd
from scipy import stats
import numpy as np

def calculate_untr_similarities(M, indices, sample_labels):
    """Calculate and compare BC dissimilarities between treatment groups and UNTR."""
    results = []
    
    groups = ['ABX3CMT', 'ABX10', 'CMT']  # Treatment groups to compare
    sites = ['LJ', 'GR']
    days = ['d-2', 'd1', 'd3', 'd5', 'd8', 'd10', 'd30', 'd60']
    
    for site in sites:
        for day in days:
            # Get UNTR samples for this day/site
            untr_indices = list(indices['UNTR'].intersection(indices[site]).intersection(indices[day]))
            
            # Calculate within-UNTR dissimilarities
            untr_within_bcs = []
            for i in range(len(untr_indices)):
                for j in range(i+1, len(untr_indices)):
                    bc = BC(M[untr_indices[i]], M[untr_indices[j]])
                    untr_within_bcs.append(bc)
            
            # For each treatment group
            for group in groups:
                # Get treatment samples for this day/site
                treat_indices = list(indices[group].intersection(indices[site]).intersection(indices[day]))
                
                # Calculate treatment-to-UNTR dissimilarities
                treat_untr_bcs = []
                for treat_idx in treat_indices:
                    for untr_idx in untr_indices:
                        bc = BC(M[treat_idx], M[untr_idx])
                        treat_untr_bcs.append(bc)
                
                if len(treat_untr_bcs) > 0 and len(untr_within_bcs) > 0:
                    # Perform statistical test
                    stat, pval = stats.ranksums(treat_untr_bcs, untr_within_bcs)
                    
                    results.append({
                        'Group': group,
                        'Site': site,
                        'Day': day,
                        'Test_statistic': stat,
                        'P_value': pval,
                        'UNTR_within_mean': np.mean(untr_within_bcs),
                        'UNTR_within_std': np.std(untr_within_bcs),
                        'Treatment_UNTR_mean': np.mean(treat_untr_bcs),
                        'Treatment_UNTR_std': np.std(treat_untr_bcs),
                        'UNTR_within_n': len(untr_within_bcs),
                        'Treatment_UNTR_n': len(treat_untr_bcs)
                    })
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Error - usage:\n >>> python analyze_untr_similarity.py [Rosetta.csv] [Output_stats.tsv]\n")
        sys.exit()
    
    in_fname, stats_fname = sys.argv[1:]
    
    # Read and normalize the data
    print("Reading and normalizing data...")
    M, indices, sample_labels = read_rosetta_indexed(in_fname, relative=True)
    
    # Calculate similarities and perform tests
    print("Calculating similarities and performing statistical tests...")
    stats_df = calculate_untr_similarities(M, indices, sample_labels)
    
    # Save results
    stats_df.to_csv(stats_fname, sep='\t', index=False)
    print(f"\nResults saved to: {stats_fname}")
    
    # Print initial timepoint results to support manuscript statement
    print("\nInitial timepoint (d-2) results:")
    print("=" * 60)
    initial_results = stats_df[stats_df['Day'] == 'd-2'].sort_values(['Site', 'Group'])
    for _, row in initial_results.iterrows():
        print(f"\n{row['Group']} at {row['Site']}:")
        print(f"  UNTR within-group BC: {row['UNTR_within_mean']:.3f} ± {row['UNTR_within_std']:.3f} (n={row['UNTR_within_n']})")
        print(f"  {row['Group']}-to-UNTR BC: {row['Treatment_UNTR_mean']:.3f} ± {row['Treatment_UNTR_std']:.3f} (n={row['Treatment_UNTR_n']})")
        print(f"  Test statistic: {row['Test_statistic']:.3f}")
        print(f"  P-value: {row['P_value']:.3e}")
        
        # Interpret the result
        if row['P_value'] >= 0.05:
            print("  -> No significant difference from UNTR within-group variation")
        else:
            direction = "higher" if row['Test_statistic'] > 0 else "lower"
            print(f"  -> Significantly {direction} than UNTR within-group variation")
