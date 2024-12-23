import sys
from scipy.spatial.distance import braycurtis as BC
from utils import read_rosetta_indexed
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats

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

def calculate_t_tests(df):
    """Calculate t-tests comparing each treatment group to UNTR for each day and site."""
    results = []
    
    treatment_groups = ['CMT', 'ABX3CMT', 'ABX10']
    sites = ['LJ', 'GR']
    days = ['d-2', 'd1', 'd3', 'd5', 'd8', 'd10', 'd30', 'd60']
    
    for group in treatment_groups:
        for site in sites:
            for day in days:
                # Get UNTR data for this day/site
                untr_data = df[(df['Group'] == 'UNTR') & 
                             (df['Site'] == site) & 
                             (df['Day'] == day)]['BC_Dissimilarity']
                
                # Get treatment group data
                treat_data = df[(df['Group'] == group) & 
                              (df['Site'] == site) & 
                              (df['Day'] == day)]['BC_Dissimilarity']
                
                if len(untr_data) > 0 and len(treat_data) > 0:
                    t_stat, p_val = stats.ttest_ind(untr_data, treat_data)
                    
                    results.append({
                        'Group': group,
                        'Site': site,
                        'Day': day,
                        'T_statistic': t_stat,
                        'P_value': p_val,
                        'UNTR_mean': untr_data.mean(),
                        'UNTR_std': untr_data.std(),
                        'Treatment_mean': treat_data.mean(),
                        'Treatment_std': treat_data.std()
                    })
    
    return pd.DataFrame(results)

def plot_within_group_bc(df, output_file):
    """Create faceted boxplot showing BC dissimilarity distributions."""
    # Set figure size
    fig = plt.figure(figsize=(15, 10))

    # Create facet grid
    g = sns.FacetGrid(data=df, 
                      col="Group",
                      row="Site",
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
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        ax.set_title(ax.get_title(), fontsize=20, fontweight='bold')
        ax.set_xlabel('Day', fontsize=16, fontweight='bold')
        ax.set_ylabel('Bray-Curtis Dissimilarity', fontsize=16, fontweight='bold')
        
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontsize(14)
            label.set_fontweight('bold')
            
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig(output_file, bbox_inches='tight', dpi=300)
    plt.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Error - usage:\n >>> python analyze_within_group_bc.py [Rosetta.csv] [Output_plot.png] [Output_stats.tsv]\n")
        sys.exit()
    
    in_fname, plot_fname, stats_fname = sys.argv[1:]
    
    # Read and normalize the data
    M, indices, sample_labels = read_rosetta_indexed(in_fname, relative=True)
    
    # Calculate within-group dissimilarities
    print("Calculating within-group BC dissimilarities...")
    df = calculate_within_group_bc(M, indices, sample_labels)
    
    # Calculate t-tests
    print("Performing statistical tests...")
    stats_df = calculate_t_tests(df)
    
    # Print summary statistics
    #print("\nWithin-group BC dissimilarity statistics:")
    #print("=" * 60)
    #group_stats = df.groupby(['Group', 'Site', 'Day'])['BC_Dissimilarity'].agg(['count', 'mean', 'std']).round(3)
    #print(group_stats)
    
    # Save detailed statistics
    stats_df.to_csv(stats_fname, sep='\t', index=False)
    print(f"\nDetailed statistics saved to: {stats_fname}")
    
    # Create visualization
    plot_within_group_bc(df, plot_fname)
    print(f"Plot saved to: {plot_fname}")
