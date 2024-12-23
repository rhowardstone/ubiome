


import sys
from utils import read_rosetta
import pandas as pd
import numpy as np
from scipy import stats

def analyze_donor_content(in_fname):
    """Analyze donor content by both ASV count and read abundance with statistics."""
    # Get donor (W1/W2) ASVs
    sample_labels, ros = read_rosetta(in_fname, cols=True)
    inverted = list(zip(*[ros[ID][2] for ID in ros]))  # transpose to get samples as rows
    
    # Get indices for each group/timepoint/site
    indices = {}
    for i, label in enumerate(sample_labels):
        if label not in ['W1', 'W2']:
            group, day, site = label.split("_")[:3]
            key = (group, day, site)
            if key not in indices:
                indices[key] = []
            indices[key].append(i)
    
    # Get donor ASVs
    donor_asvs = set()
    for i, label in enumerate(sample_labels):
        if label in ['W1', 'W2']:
            for j, count in enumerate(inverted[i]):
                if count > 0:
                    donor_asvs.add(j)
    
    results = []
    # For day 60 samples, calculate donor content
    for group in ['CMT', 'ABX3CMT', 'UNTR']:
        for site in ['LJ', 'GR']:
            key = (group, 'd60', site)
            if key in indices:
                for idx in indices[key]:
                    # Calculate metrics for this sample
                    sample_asvs = set(j for j, count in enumerate(inverted[idx]) if count > 0)
                    donor_overlap = sample_asvs.intersection(donor_asvs)
                    
                    # Get both metrics
                    pct_donor_asvs = len(donor_overlap) / len(sample_asvs) if len(sample_asvs) > 0 else 0
                    donor_reads = sum(inverted[idx][j] for j in donor_overlap)
                    total_reads = sum(inverted[idx])
                    pct_donor_reads = donor_reads / total_reads if total_reads > 0 else 0
                    
                    results.append({
                        'Group': group,
                        'Site': site,
                        'Sample': sample_labels[idx],
                        'Pct_Donor_ASVs': pct_donor_asvs,
                        'Pct_Donor_Reads': pct_donor_reads
                    })
    
    df = pd.DataFrame(results)
    
    # Run statistical tests
    print("\nStatistical Tests for Donor Content at Day 60:")
    print("=" * 60)
    
    for metric in ['Pct_Donor_ASVs', 'Pct_Donor_Reads']:
        print(f"\nTests for {metric}:")
        for site in ['LJ', 'GR']:
            print(f"\n{site}:")
            # CMT vs UNTR
            cmt_vals = df[(df['Group'] == 'CMT') & (df['Site'] == site)][metric]
            untr_vals = df[(df['Group'] == 'UNTR') & (df['Site'] == site)][metric]
            t_stat, p_val = stats.ttest_ind(cmt_vals, untr_vals)
            print(f"CMT vs UNTR: t={t_stat:.3f}, p={p_val:.4f}")
            
            # ABX3CMT vs UNTR
            abx3_vals = df[(df['Group'] == 'ABX3CMT') & (df['Site'] == site)][metric]
            t_stat, p_val = stats.ttest_ind(abx3_vals, untr_vals)
            print(f"ABX3CMT vs UNTR: t={t_stat:.3f}, p={p_val:.4f}")
            
            # Summary statistics
            print("\nMean ± SD by group:")
            for group in ['CMT', 'ABX3CMT', 'UNTR']:
                vals = df[(df['Group'] == group) & (df['Site'] == site)][metric]
                print(f"{group}: {vals.mean():.3f} ± {vals.std():.3f}")
    
    return df

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Error - usage:\n >>> python analyze_donor_stats.py [Rosetta.csv]\n")
        sys.exit()
    
    results = analyze_donor_content(sys.argv[1])
    results.to_csv("data/donor_content_stats.csv", index=False)
