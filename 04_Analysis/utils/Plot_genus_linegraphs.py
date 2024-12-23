import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import sys, os
from utils import read_rosetta

def custom_plot(x, y, **kwargs):
    ax = plt.gca()
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontweight('bold')

if __name__ == "__main__":
    if len(sys.argv)!=6:
        print("Error - usage:\n >>> python Plot_genus_linegraphs.py [Rosetta.csv] [Genus-name] [tempfile.tsv] [0/1 wLeg?] [Out.png]\n")
        exit()
    in_fname, genus, tempfile, wLeg, out_fname = sys.argv[1:]
    print("Reading the data")
    sample_IDs, ros = read_rosetta(in_fname, cols=True)
    ASV_IDs = [ID for ID in ros]
    vects = [ros[ID][2] for ID in ASV_IDs]
    
    print("Normalizing")
    vects = list(zip(*vects))
    temp = []
    for row in vects:
        tempsum = sum(row)
        temp.append([a/tempsum for a in row])
    vects = list(zip(*temp))
    
    print("Filtering")
    Species = {}
    for i in range(len(ASV_IDs)):
        tax = ros[ASV_IDs[i]][1].split(";")
        if tax[5]==genus:
            new_ID = tax[6]
            if new_ID in Species:
                for j in range(len(sample_IDs)):
                    Species[new_ID][j] += vects[i][j]
            else:
                Species[new_ID] = list(vects[i])
    Species_names = [ID for ID in Species]
    vects = list(zip(*[Species[ID] for ID in Species_names]))
    
    print("Collating")
    Out = open(tempfile, 'w+')
    Out.write('\t'.join('Treatment Day Site Sex Animal'.split() + Species_names)+"\n")
    for i in range(len(vects)):
        if not sample_IDs[i].startswith('W'):
            temp = sample_IDs[i].split("_")
            temp[1] = temp[1][1:]
            Out.write("\t".join(temp) + '\t' + '\t'.join([str(a) for a in list(vects[i])]) + '\n')
        else:
            temp = ['W', sample_IDs[i], 'W', 'W', 'W']
    Out.close()
    print("Plotting. There are", len(Species_names), "legend entries in the plot.")
    
    data = pd.read_csv(tempfile, sep='\t')
    data_long = pd.melt(data, id_vars=['Treatment', 'Day', 'Site', 'Sex', 'Animal'], 
                       var_name='Species', value_name='Relative Abundance')
    data_long['Day'] = data_long['Day'].astype(str)
    
    if wLeg == '1':
        plt.figure(figsize=(14, 6))
        fig, ax = plt.subplots()
        palette = sns.color_palette("tab10", n_colors=len(Species_names))
        legend_handles = [mlines.Line2D([], [], color=palette[i], marker='o', 
                         linestyle='-', label=name) for i, name in enumerate(Species_names)]
        ax = plt.gca()
        legend = ax.legend(handles=legend_handles, title='Species', loc='center', 
                         ncol=3, fancybox=True, shadow=True)
        plt.setp(legend.get_title(), fontweight='bold')
        plt.setp(legend.get_texts(), fontweight='bold')
        ax.axis('off')
        fig.canvas.draw()
        bbox = legend.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        fig.set_size_inches(bbox.width+1, bbox.height+1)
    else:
        plt.figure(figsize=(10, 4))

        # Define treatment order
        data_long['Treatment'] = pd.Categorical(data_long['Treatment'], 
                                              categories=['UNTR', 'CMT', 'ABX3CMT', 'ABX10'], 
                                              ordered=True)
        # Define site order (LJ first, then GR)
        data_long['Site'] = pd.Categorical(data_long['Site'], 
                                         categories=['LJ', 'GR'], 
                                         ordered=True)
        
        # Create FacetGrid
        g = sns.FacetGrid(data_long, row='Site', col='Treatment', 
                         hue='Species', margin_titles=False, 
                         palette='tab10', sharex=True, sharey=True)
        
        g.map(sns.lineplot, 'Day', 'Relative Abundance', linestyle='', marker="o")
        g.map(custom_plot, 'Day', 'Relative Abundance')
        
        # Set the column titles (top row only)
        for ax, title in zip(g.axes[0], ['UNTR', 'CMT', 'ABX3CMT', 'ABX10']):
            ax.set_title(title, fontweight='bold')
            
        # Clear any existing titles on bottom row
        for ax in g.axes[1]:
            ax.set_title("")
        
        # Add row labels (site names) on the right side
        for idx, (ax, title) in enumerate(zip(g.axes[:, -1], ['LJ', 'GR'])):
            ax.annotate(title, xy=(1.02, 0.5), xycoords='axes fraction',
                       fontweight='bold', rotation=0,
                       ha='left', va='center')
        
        g.set_axis_labels("Day", "Relative Abundance", fontweight='bold')
        g.set(ylim=(0, None))
        
        plt.tight_layout()
        
        # Print statistics
        print("\nRelative Abundance Statistics:")
        print("Treatment\tSite\tDay\tSpecies\tMean\tStd Dev")
        print("-" * 70)

        stats = data_long.groupby(['Treatment', 'Site', 'Day', 'Species'])[
            'Relative Abundance'].agg(['mean', 'std']).reset_index()
        stats = stats.sort_values(['Treatment', 'Site', 'Day', 'Species'])

        for _, row in stats.iterrows():
            mean_val = row['mean']
            std_val = row['std'] if not pd.isna(row['std']) else 0
            print(f"{row['Treatment']}\t{row['Site']}\t{row['Day']}\t"
                  f"{row['Species']}\t{mean_val:.4f}\t{std_val:.4f}")

        print("\nOverall averages by Species:")
        print("Species\tMean\tStd Dev")
        print("-" * 40)

        overall_stats = data_long.groupby(['Species'])[
            'Relative Abundance'].agg(['mean', 'std']).reset_index()
        for _, row in overall_stats.iterrows():
            print(f"{row['Species']}\t{row['mean']:.4f}\t{row['std']:.4f}")
            
    plt.savefig(out_fname)
