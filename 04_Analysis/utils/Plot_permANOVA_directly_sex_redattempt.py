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
    # Define a custom colormap that transitions from red to white
    colors = [(1.0, 0.0, 0.0), (1.0, 0.5, 0.5), (1.0, 0.75, 0.75), (1.0, 1.0, 1.0)]  # Red to white
    custom_cmap = mcolors.LinearSegmentedColormap.from_list('custom_red_white', colors, N=8)

    # Set the style and palette
    sns.set(style="whitegrid")
    palette = sns.color_palette("deep", 4)
    group_colors = {"FMT": palette[2], "ABX10": palette[3], "ABX3FMT": palette[1], "UNTR": palette[0]}
    
    # Define the custom order for groups
    group_order = ['UNTR', 'FMT', 'ABX3FMT', 'ABX10']
    
    # Get unique days and groups
    unique_days = sorted(data['Day'].unique())
    unique_groups = group_order
    
    # Split the data by site
    data_gr = data[data['Site'] == 'GR']
    data_lj = data[data['Site'] == 'LJ']
    
    # Create pivot tables for the heatmap
    heatmap_data_gr = data_gr.pivot(index='Group', columns='Day', values='Pval').reindex(index=unique_groups, columns=unique_days, fill_value=np.nan)
    heatmap_data_lj = data_lj.pivot(index='Group', columns='Day', values='Pval').reindex(index=unique_groups, columns=unique_days, fill_value=np.nan)
    
    # Normalize eta-sqr values for color mapping
    eta_sqr_data_gr = data_gr.pivot(index='Group', columns='Day', values='eta-sqr').reindex(index=unique_groups, columns=unique_days, fill_value=np.nan)
    eta_sqr_data_lj = data_lj.pivot(index='Group', columns='Day', values='eta-sqr').reindex(index=unique_groups, columns=unique_days, fill_value=np.nan)
    norm_eta = plt.Normalize(min(eta_sqr_data_gr.min().min(), eta_sqr_data_lj.min().min()), max(eta_sqr_data_gr.max().max(), eta_sqr_data_lj.max().max()))
    norm_pval = plt.Normalize(0, 1)

    # Create the figure and axes
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 16), sharex=True, gridspec_kw={'hspace': 0.05})

    # Plot the heatmaps for p-values
    sns.heatmap(heatmap_data_gr, ax=ax1, cmap=custom_cmap, cbar=False, linewidths=0.5, linecolor='gray', square=True, vmin=0, vmax=1, annot=False, norm=norm_pval)
    sns.heatmap(heatmap_data_lj, ax=ax2, cmap=custom_cmap, cbar=False, linewidths=0.5, linecolor='gray', square=True, vmin=0, vmax=1, annot=False, norm=norm_pval)

    # Overlay circles for eta-squared values and annotate eta-squared values for GR
    for y in range(heatmap_data_gr.shape[0]):
        for x in range(heatmap_data_gr.shape[1]):
            eta_sqr = eta_sqr_data_gr.iloc[y, x]
            if not np.isnan(eta_sqr):
                color = custom_cmap(1 - norm_eta(eta_sqr))  # Reverse color mapping
                ax1.add_patch(plt.Circle((x + 0.5, y + 0.5), 0.3, color=color, ec='black', lw=0.5))
                ax1.text(x + 0.5, y + 0.5, f'{eta_sqr:.2f}', ha='center', va='center', fontweight='bold', color='black')

    # Overlay circles for eta-squared values and annotate eta-squared values for LJ
    for y in range(heatmap_data_lj.shape[0]):
        for x in range(heatmap_data_lj.shape[1]):
            eta_sqr = eta_sqr_data_lj.iloc[y, x]
            if not np.isnan(eta_sqr):
                color = custom_cmap(1 - norm_eta(eta_sqr))  # Reverse color mapping
                ax2.add_patch(plt.Circle((x + 0.5, y + 0.5), 0.3, color=color, ec='black', lw=0.5))
                ax2.text(x + 0.5, y + 0.5, f'{eta_sqr:.2f}', ha='center', va='center', fontweight='bold', color='black')

    # Set the labels
    ax1.text(-0.3, 0.5, 'GR', fontsize=14, fontweight='bold', color='black', rotation=90, va='center', transform=ax1.transAxes)
    ax2.text(-0.3, 0.5, 'LJ', fontsize=14, fontweight='bold', color='black', rotation=90, va='center', transform=ax2.transAxes)
    ax2.set_xlabel('Day', fontsize=12, fontweight='bold', color='black')
    ax1.set_ylabel('GR', fontsize=12, fontweight='bold', color='black')
    ax2.set_ylabel('LJ', fontsize=12, fontweight='bold', color='black')

    # Customize tick labels to be bold
    plt.setp(ax1.get_xticklabels(), fontweight='bold')
    plt.setp(ax1.get_yticklabels(), fontweight='bold')
    plt.setp(ax2.get_xticklabels(), fontweight='bold')
    plt.setp(ax2.get_yticklabels(), fontweight='bold')

    # Create a single colorbar for both eta-squared and p-values
    sm = plt.cm.ScalarMappable(cmap=custom_cmap, norm=norm_pval)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=[ax1, ax2], orientation='vertical', fraction=0.05, pad=0.1, shrink=0.6)
    cbar.ax.tick_params(labelsize=12, colors='black')
    plt.setp(cbar.ax.get_yticklabels(), fontweight='bold')

    # Add ticks for eta-squared on the left
    eta_ticks = np.linspace(min(eta_sqr_data_gr.min().min(), eta_sqr_data_lj.min().min()), 
                            max(eta_sqr_data_gr.max().max(), eta_sqr_data_lj.max().max()), len(cbar.ax.get_yticks()))
    cbar.ax2 = cbar.ax.twinx()
    cbar.ax2.set_yticks(cbar.ax.get_yticks())
    cbar.ax2.set_yticklabels([f'{v:.2f}' for v in reversed(eta_ticks)])  # Reversed labels for eta-squared
    cbar.ax2.tick_params(labelsize=12, colors='black')
    plt.setp(cbar.ax2.get_yticklabels(), fontweight='bold')

    # Set labels for the colorbar
    cbar.ax.set_ylabel('P-value', fontsize=14, fontweight='bold', color='black', labelpad=20, y=0.5)
    cbar.ax2.set_ylabel('Eta-squared', fontsize=14, fontweight='bold', color='black', labelpad=20, y=0.5)
    
    # Set the title of the plot
    plt.suptitle('Sex', fontsize=24, fontweight='bold')
    
    # Save the plot to the specified output file
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust the layout to leave space for the suptitle
    plt.savefig(output_file)
    plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate heatmap with circles from TSV data.')
    parser.add_argument('input_file', type=str, help='Input TSV file with data')
    parser.add_argument('output_file', type=str, help='Output file for the heatmap with circles')
    
    args = parser.parse_args()
    
    data = prepare_data(args.input_file)
    plot_heatmap_with_circles(data, args.output_file)

