import sys
from scipy.spatial.distance import braycurtis as BC
from utils import read_rosetta_indexed
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats

def calculate_consecutive_bc(M, indices, sample_labels):
    """Calculate BC dissimilarities between consecutive timepoints."""
    results = []
    
    groups = ['UNTR', 'CMT', 'ABX3CMT', 'ABX10']
    sites = ['LJ', 'GR']
    days = ['d-2', 'd1', 'd3', 'd5', 'd8', 'd10', 'd30', 'd60']
    day_pairs = [f"{days[i]}-{days[i+1]}" for i in range(len(days)-1)]
    
    for group in groups:
        for site in sites:
            for i in range(len(days)-1):
                day1 = days[i]
                day2 = days[i+1]
                
                day1_indices = list(indices[group].intersection(indices[site]).intersection(indices[day1]))
                day2_indices = list(indices[group].intersection(indices[site]).intersection(indices[day2]))
                
                for idx1 in day1_indices:
                    for idx2 in day2_indices:
                        bc = BC(M[idx1], M[idx2])
                        results.append({
                            'Group': group,
                            'Site': site,
                            'Day_Pair': f"{day1}-{day2}",
                            'BC_Dissimilarity': bc
                        })
    
    df = pd.DataFrame(results)
    df['Day_Pair'] = pd.Categorical(df['Day_Pair'], categories=day_pairs, ordered=True)
    return df

def calculate_t_tests(df):
    """Calculate statistical tests comparing each treatment group to UNTR for all day pairs."""
    results = []
    
    treatment_groups = ['CMT', 'ABX3CMT', 'ABX10']
    sites = ['LJ', 'GR']
    
    # Get unique day pairs in chronological order
    day_pairs = df['Day_Pair'].unique()
    
    for group in treatment_groups:
        for site in sites:
            for day_pair in day_pairs:
                # Get UNTR data for this day pair/site
                untr_data = df[(df['Group'] == 'UNTR') & 
                             (df['Site'] == site) & 
                             (df['Day_Pair'] == day_pair)]['BC_Dissimilarity']
                
                # Get treatment group data
                treat_data = df[(df['Group'] == group) & 
                              (df['Site'] == site) & 
                              (df['Day_Pair'] == day_pair)]['BC_Dissimilarity']
                
                if len(untr_data) > 0 and len(treat_data) > 0:
                    stat, pval = stats.ranksums(treat_data, untr_data)
                    
                    results.append({
                        'Group': group,
                        'Site': site,
                        'Day_Pair': day_pair,
                        'Test_statistic': stat,
                        'P_value': pval,
                        'UNTR_mean': untr_data.mean(),
                        'UNTR_std': untr_data.std(),
                        'Treatment_mean': treat_data.mean(),
                        'Treatment_std': treat_data.std(),
                        'UNTR_n': len(untr_data),
                        'Treatment_n': len(treat_data)
                    })
    
    return pd.DataFrame(results)

def plot_consecutive_bc(df, output_file):
    """Create faceted boxplot showing BC dissimilarity distributions."""
    fig = plt.figure(figsize=(15, 10))

    # Create FacetGrid with modified group order
    groups = ['UNTR', 'CMT', 'ABX3CMT', 'ABX10']
    df['Group'] = pd.Categorical(df['Group'], categories=groups, ordered=True)
    
    g = sns.FacetGrid(data=df, 
                      col="Group",
                      row="Site",
                      height=4,
                      aspect=1.5,
                      margin_titles=False)  # Turn off default margin titles

    palette = sns.color_palette("deep", 4)
    group_colors = {
        "CMT": palette[2],
        "ABX10": palette[3],
        "ABX3CMT": palette[1],
        "UNTR": palette[0]
    }

    def draw_boxplot(data, **kwargs):
        sns.boxplot(data=data, x="Day_Pair", y="BC_Dissimilarity", 
                   width=0.7, color=group_colors[data['Group'].iloc[0]])

    g.map_dataframe(draw_boxplot)

    # Add a single y-axis label for each row
    g.figure.supylabel('Bray-Curtis Dissimilarity', fontsize=20, fontweight='bold', x=0.11)

    # Customize each subplot
    for i, row_axes in enumerate(g.axes):
        site = ['LJ', 'GR'][i]  # Get site for this row
        for j, ax in enumerate(row_axes):
            group = groups[j]  # Get group for this column
            
            # Set column titles (only top row)
            if i == 0:
                ax.set_title(group, fontsize=24, fontweight='bold', pad=20)
            else:
                ax.set_title('')
            
            # Set row labels (as text on right side)
            if j == len(row_axes) - 1:  # Last column
                ax.text(1.1, 0.5, site, 
                       transform=ax.transAxes,
                       fontsize=24,
                       fontweight='bold',
                       va='center')
            
            # Customize axis labels and ticks
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            ax.tick_params(axis='both', labelsize=16)
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontweight('bold')
            
            # Remove individual y-axis labels
            ax.set_ylabel('')
            
            # Only bottom plots should have x-axis label
            if i == len(g.axes) - 1:
                ax.set_xlabel('Day Transitions', fontsize=20, fontweight='bold')
            else:
                ax.set_xlabel('')
            
            ax.grid(True, axis='y', linestyle='--', alpha=0.7)

    # Adjust layout to account for row labels and shared y-axis label
    plt.subplots_adjust(right=0.95, left=0.15)
    plt.savefig(output_file, bbox_inches='tight', dpi=300)
    plt.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Error - usage:\n >>> python analyze_consecutive_bc.py [Rosetta.csv] [Output_plot.png] [Output_stats.tsv]\n")
        sys.exit()
    
    in_fname, plot_fname, stats_fname = sys.argv[1:]
    
    # Read and normalize the data
    M, indices, sample_labels = read_rosetta_indexed(in_fname, relative=True)
    
    # Calculate consecutive day dissimilarities
    print("Calculating consecutive day BC dissimilarities...")
    df = calculate_consecutive_bc(M, indices, sample_labels)
    
    # Calculate statistical tests
    print("Performing statistical tests...")
    stats_df = calculate_t_tests(df)
    
    # Print summary statistics
    #print("\nConsecutive day BC dissimilarity statistics:")
    #print("=" * 60)
    #group_stats = df.groupby(['Group', 'Site', 'Day_Pair'])['BC_Dissimilarity'].agg(['count', 'mean', 'std']).round(3)
    #print(group_stats)
    
    # Save statistical results
    stats_df.to_csv(stats_fname, sep='\t', index=False)
    print(f"\nDetailed statistics saved to: {stats_fname}")
    
    # Create visualization
    plot_consecutive_bc(df, plot_fname)
    print(f"Plot saved to: {plot_fname}")
    
    # Print final timepoint summaries
    #print("\nFinal timepoint transitions summary:")
    #final_stats = df[df['Day_Pair'] == 'd30-d60'].groupby(['Group', 'Site'])['BC_Dissimilarity'].agg(['mean', 'std']).round(3)
    #print(final_stats)
