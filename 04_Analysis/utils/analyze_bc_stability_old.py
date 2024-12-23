import sys
from scipy.spatial.distance import braycurtis as BC
from utils import read_rosetta_indexed
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def calculate_within_group_bc(M, indices, sample_labels):
    """Calculate within-group BC dissimilarities for each timepoint."""
    results = []
    
    groups = ['UNTR', 'CMT', 'ABX3CMT', 'ABX10']
    sites = ['LJ', 'GR']
    days = ['d-2', 'd1', 'd3', 'd5', 'd8', 'd10', 'd30', 'd60']
    
    for group in groups:
        for site in sites:
            for day in days:
                # Get samples for this group/site/day
                sample_indices = indices[group].intersection(indices[site]).intersection(indices[day])
                sample_indices = list(sample_indices)
                
                # Calculate BC dissimilarity between all pairs
                for i in range(len(sample_indices)):
                    for j in range(i+1, len(sample_indices)):
                        bc = BC(M[sample_indices[i]], M[sample_indices[j]])
                        results.append({
                            'Group': group,
                            'Site': site,
                            'Day': day,
                            'BC_Dissimilarity': bc
                        })
    
    return pd.DataFrame(results)

def plot_within_group_bc(df, output_file):
    """Create faceted boxplot showing BC dissimilarity distributions."""
    # Set figure size
    fig = plt.figure(figsize=(15, 10))

    # Create facet grid
    g = sns.FacetGrid(data=df, 
                      col="Site",  # Columns are now sites
                      row="Group",  # Rows are now treatment groups
                      height=4,
                      aspect=1.5)

    # Define color palette similar to other figures
    palette = sns.color_palette("deep", 4)
    group_colors = {
        "CMT": palette[2],
        "ABX10": palette[3],
        "ABX3CMT": palette[1],
        "UNTR": palette[0]
    }

    # Add boxplots
    def draw_boxplot(data, **kwargs):
        sns.boxplot(data=data, x="Day", y="BC_Dissimilarity", 
                   width=0.7, color=group_colors[data['Group'].iloc[0]])

    g.map_dataframe(draw_boxplot)

    # Customize appearance
    for ax in g.axes.flat:
        # Rotate x-axis labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

        # Make labels bold
        ax.set_title(ax.get_title(), fontsize=20, fontweight='bold')
        ax.set_xlabel('Day', fontsize=16, fontweight='bold')
        ax.set_ylabel('Bray-Curtis Dissimilarity', fontsize=16, fontweight='bold')

        # Make tick labels bold
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontsize(14)
            label.set_fontweight('bold')

        # Add grid
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig(output_file, bbox_inches='tight', dpi=300)
    plt.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Error - usage:\n >>> python analyze_within_group_bc.py [Rosetta.csv]\n")
        sys.exit()
    
    in_fname = sys.argv[1]
    
    # Read and normalize the data
    M, indices, sample_labels = read_rosetta_indexed(in_fname, relative=True)
    
    # Calculate within-group dissimilarities
    print("Calculating within-group BC dissimilarities...")
    df = calculate_within_group_bc(M, indices, sample_labels)
    
    # Print summary statistics
    print("\nWithin-group BC dissimilarity statistics:")
    print("=" * 60)
    stats = df.groupby(['Group', 'Site', 'Day'])['BC_Dissimilarity'].agg(['count', 'mean', 'std']).round(3)
    print(stats)
    
    # Create visualization
    plot_within_group_bc(df, "Figs/within_group_bc_dissimilarity.png")
    
    # Save detailed results
    df.to_csv("data/within_group_bc_dissimilarity.csv", index=False)
    
    # Print specific comparison for manuscript
    print("\nComparison of final timepoints vs UNTR variation:")
    final_stats = df[df['Day'].isin(['d30', 'd60'])].groupby(['Group', 'Site'])['BC_Dissimilarity'].agg(['mean', 'std']).round(3)
    untr_stats = df[df['Group'] == 'UNTR'].groupby('Site')['BC_Dissimilarity'].agg(['mean', 'std']).round(3)
    print("\nFinal timepoints (d30-d60):")
    print(final_stats)
    print("\nUNTR all timepoints:")
    print(untr_stats)
