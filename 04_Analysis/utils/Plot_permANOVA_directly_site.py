import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import numpy as np
import matplotlib.colors as mcolors

def prepare_data(input_file):
    # Load the data
    data = pd.read_csv(input_file, sep='\t')
    
    # Filter the data according to the requirements
    data = data[data['Group'] != '-1']
    
    # Remove the first character of the Day entry and convert to numeric
    data['Day'] = data['Day'].str[1:].astype(int)
    
    return data

def plot_heatmap_with_circles(data, output_file):
    # Define a custom colormap that transitions from light green to yellow
    colors = [(0.2, 0.8, 0.2), (0.5, 1.0, 0.5), (1.0, 1.0, 0.0)]  # Light green to yellow
    n_bins = 100  # Discretizes the interpolation into bins
    custom_cmap = mcolors.LinearSegmentedColormap.from_list('custom_yellowgreen', colors, N=n_bins)

    # Set the style and palette
    sns.set(style="whitegrid")
    palette = sns.color_palette("deep", 4)
    group_colors = {"CMT": palette[2], "ABX10": palette[3], "ABX3CMT": palette[1], "UNTR": palette[0]}
    
    # Define the custom order for groups
    group_order = ['UNTR', 'CMT', 'ABX3CMT', 'ABX10']
    
    # Get unique days and groups
    unique_days = sorted(data['Day'].unique())
    unique_groups = group_order
    
    # Create a pivot table for the heatmap
    heatmap_data = data.pivot(index='Group', columns='Day', values='Pval').reindex(index=unique_groups, columns=unique_days, fill_value=np.nan)

    # Normalize eta-sqr values for color mapping
    eta_sqr_data = data.pivot(index='Group', columns='Day', values='eta-sqr').reindex(index=unique_groups, columns=unique_days, fill_value=np.nan)
    norm = plt.Normalize(eta_sqr_data.min().min(), eta_sqr_data.max().max())

    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot the heatmap
    sns.heatmap(heatmap_data, ax=ax, cmap='coolwarm_r', cbar=False, linewidths=0.5, linecolor='gray', square=True, vmin=0, vmax=0.05, annot=False)

    # Overlay circles for eta-squared values and annotate eta-squared values
    for y in range(heatmap_data.shape[0]):
        for x in range(heatmap_data.shape[1]):
            eta_sqr = eta_sqr_data.iloc[y, x]
            pval = heatmap_data.iloc[y, x]
            if not np.isnan(eta_sqr):
                color = custom_cmap(norm(eta_sqr))
                ax.add_patch(plt.Circle((x + 0.5, y + 0.5), 0.3, color=color, ec='black', lw=0.5))
                ax.text(x + 0.5, y + 0.5, f'{eta_sqr:.2f}', ha='center', va='center', fontweight='bold', color='black')

    # Set the labels
    ax.set_xticks(np.arange(len(unique_days)) + 0.5)
    ax.set_yticks(np.arange(len(unique_groups)) + 0.5)
    ax.set_xticklabels(unique_days, fontsize=12, fontweight='bold', color='black')
    ax.set_yticklabels(unique_groups, fontsize=12, fontweight='bold', color='black')
    ax.set_xlabel('Day', fontsize=12, fontweight='bold', color='black')
    ax.set_ylabel('', fontsize=12, fontweight='bold', color='black')

    # Customize tick labels to be bold
    plt.setp(ax.get_xticklabels(), fontweight='bold')
    plt.setp(ax.get_yticklabels(), fontweight='bold')

    # Create a legend for eta-squared values
    sm = plt.cm.ScalarMappable(cmap=custom_cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, orientation='vertical', fraction=0.05, pad=0.045, shrink=0.6)
    cbar.ax.tick_params(labelsize=12, colors='black')
    plt.setp(cbar.ax.get_yticklabels(), fontweight='bold')
    cbar.set_label(r'  $\mathbf{\eta^2}$', fontsize=14, color='black', labelpad=-40, y=1.05, rotation=0)

    # Create a legend for p-values
    sm_pval = plt.cm.ScalarMappable(cmap='coolwarm_r', norm=plt.Normalize(vmin=0, vmax=0.05))
    sm_pval.set_array([])
    cbar_pval = plt.colorbar(sm_pval, ax=ax, orientation='vertical', fraction=0.05, pad=0.045, shrink=0.6)
    cbar_pval.ax.tick_params(labelsize=12, colors='black')
    plt.setp(cbar_pval.ax.get_yticklabels(), fontweight='bold')
    cbar_pval.set_label(r'$\mathbf{p}$', fontsize=14, fontweight='bold', color='black', labelpad=-40, y=1.05, rotation=0)
    
    plt.title('Site', fontsize=24, fontweight='bold', y=1.02)
    # Save the plot to the specified output file
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate heatmap with circles from TSV data.')
    parser.add_argument('input_file', type=str, help='Input TSV file with data')
    parser.add_argument('output_file', type=str, help='Output file for the heatmap with circles')
    
    args = parser.parse_args()
    
    data = prepare_data(args.input_file)
    plot_heatmap_with_circles(data, args.output_file)

