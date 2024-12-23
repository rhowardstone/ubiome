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
    
    # Split the data by site
    data_gr = data[data['Site'] == 'GR']
    data_lj = data[data['Site'] == 'LJ']
    
    # Create pivot tables for the heatmap
    heatmap_data_gr = data_gr.pivot(index='Group', columns='Day', values='Pval').reindex(index=unique_groups, columns=unique_days, fill_value=np.nan)
    heatmap_data_lj = data_lj.pivot(index='Group', columns='Day', values='Pval').reindex(index=unique_groups, columns=unique_days, fill_value=np.nan)
    
    # Normalize eta-sqr values for color mapping
    eta_sqr_data_gr = data_gr.pivot(index='Group', columns='Day', values='eta-sqr').reindex(index=unique_groups, columns=unique_days, fill_value=np.nan)
    eta_sqr_data_lj = data_lj.pivot(index='Group', columns='Day', values='eta-sqr').reindex(index=unique_groups, columns=unique_days, fill_value=np.nan)
    norm = plt.Normalize(min(eta_sqr_data_gr.min().min(), eta_sqr_data_lj.min().min()), max(eta_sqr_data_gr.max().max(), eta_sqr_data_lj.max().max()))

    
    ## Create the figure and axes - note the reversed order
    #fig, (ax2, ax1) = plt.subplots(2, 1, figsize=(12, 16), sharex=True, gridspec_kw={'hspace': 0.001})  # Reduced spacing between plots
    
    # Create the figure and axes - with adjusted spacing
    fig = plt.figure(figsize=(12, 16))
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 1], hspace=0.05)
    ax2 = fig.add_subplot(gs[0])
    ax1 = fig.add_subplot(gs[1])
    
    # Plot the heatmaps
    sns.heatmap(heatmap_data_gr, ax=ax1, cmap='coolwarm_r', cbar=False, linewidths=0.5, linecolor='gray', square=True, vmin=0, vmax=0.05, annot=False)
    sns.heatmap(heatmap_data_lj, ax=ax2, cmap='coolwarm_r', cbar=False, linewidths=0.5, linecolor='gray', square=True, vmin=0, vmax=0.05, annot=False)



    # Overlay circles for eta-squared values and annotate eta-squared values for GR
    for y in range(heatmap_data_gr.shape[0]):
        for x in range(heatmap_data_gr.shape[1]):
            eta_sqr = eta_sqr_data_gr.iloc[y, x]
            pval = heatmap_data_gr.iloc[y, x]
            if not np.isnan(eta_sqr):
                color = custom_cmap(norm(eta_sqr))
                ax1.add_patch(plt.Circle((x + 0.5, y + 0.5), 0.3, color=color, ec='black', lw=0.5))
                ax1.text(x + 0.5, y + 0.5, f'{eta_sqr:.2f}', ha='center', va='center', fontweight='bold', color='black')

    # Overlay circles for eta-squared values and annotate eta-squared values for LJ
    for y in range(heatmap_data_lj.shape[0]):
        for x in range(heatmap_data_lj.shape[1]):
            eta_sqr = eta_sqr_data_lj.iloc[y, x]
            pval = heatmap_data_lj.iloc[y, x]
            if not np.isnan(eta_sqr):
                color = custom_cmap(norm(eta_sqr))
                ax2.add_patch(plt.Circle((x + 0.5, y + 0.5), 0.3, color=color, ec='black', lw=0.5))
                ax2.text(x + 0.5, y + 0.5, f'{eta_sqr:.2f}', ha='center', va='center', fontweight='bold', color='black')

    # Set the labels
    #ax1.text(-0.3, 0.5, 'GR', fontsize=14, fontweight='bold', color='black',  va='center', transform=ax1.transAxes)
    #ax2.text(-0.3, 0.5, 'LJ', fontsize=14, fontweight='bold', color='black',  va='center', transform=ax2.transAxes)
    #ax2.set_xlabel('Day', fontsize=12, fontweight='bold', color='black')
    #ax1.set_ylabel('GR', fontsize=12, fontweight='bold', color='black')
    #ax2.set_ylabel('LJ', fontsize=12, fontweight='bold', color='black')

    ax1.set_xlabel('Day', fontsize=12, fontweight='bold', color='black')

    ax2.text(-0.5, 2, 'LJ', fontsize=14, fontweight='bold', color='black', ha='right', va='center')
    ax1.text(-0.5, 2, 'GR', fontsize=14, fontweight='bold', color='black', ha='right', va='center')


    ax1.set_ylabel('')
    ax2.set_ylabel('')
    ax2.set_xlabel('')
    

    # Customize tick labels to be bold
    plt.setp(ax1.get_xticklabels(), fontweight='bold')
    plt.setp(ax1.get_yticklabels(), fontweight='bold')
    plt.setp(ax2.get_xticklabels(), fontweight='bold')
    plt.setp(ax2.get_yticklabels(), fontweight='bold')

    # Create a legend for eta-squared values
    sm = plt.cm.ScalarMappable(cmap=custom_cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=[ax1, ax2], orientation='vertical', fraction=0.05, pad=0.1, shrink=0.6)
    cbar.ax.tick_params(labelsize=12, colors='black')
    plt.setp(cbar.ax.get_yticklabels(), fontweight='bold')
    cbar.set_label(r'  $\mathbf{\eta^2}$', fontsize=14, color='black', labelpad=-40, y=1.05, rotation=0)

    # Create a legend for p-values
    sm_pval = plt.cm.ScalarMappable(cmap='coolwarm_r', norm=plt.Normalize(vmin=0, vmax=0.05))
    sm_pval.set_array([])
    cbar_pval = plt.colorbar(sm_pval, ax=[ax1, ax2], orientation='vertical', fraction=0.05, pad=0.1, shrink=0.6)
    cbar_pval.ax.tick_params(labelsize=12, colors='black')
    plt.setp(cbar_pval.ax.get_yticklabels(), fontweight='bold')
    cbar_pval.set_label(r'$\mathbf{p}$', fontsize=14, fontweight='bold', color='black', labelpad=-40, y=1.05, rotation=0)
    
    
    # Add title at the top
    plt.suptitle('Sex', fontsize=24, fontweight='bold', y = 0.825, x = 0.4) #, y=0.95)
    
    
    #plt.tight_layout(rect=[0, 0, 1, 0.97])
    #plt.tight_layout(rect=[0.1, 0, 0.9, 0.95])
    plt.savefig(output_file)
    plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate heatmap with circles from TSV data.')
    parser.add_argument('input_file', type=str, help='Input TSV file with data')
    parser.add_argument('output_file', type=str, help='Output file for the heatmap with circles')
    
    args = parser.parse_args()
    
    data = prepare_data(args.input_file)
    plot_heatmap_with_circles(data, args.output_file)

