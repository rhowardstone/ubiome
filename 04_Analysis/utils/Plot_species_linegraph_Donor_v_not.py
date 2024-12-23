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
    if len(sys.argv)!=7:
        print("Error - usage:\n >>> python Plot_species_linegraphs_Donor_vs_not.py [Rosetta.csv] ['Species-name'] [tempfile.tsv] [0/1 wLeg?] [Donor-ASVs.txt] [Out.png]\n")
        exit()
    in_fname, species, tempfile, donor_ASVs_fname, wLeg, out_fname = sys.argv[1:]
    print("Reading the data for species name: '"+species+"'")
    sample_IDs, ros = read_rosetta(in_fname, cols=True)
    ASV_IDs = [ID for ID in ros]
    vects = [ros[ID][2] for ID in ASV_IDs]
    
    In = open(donor_ASVs_fname)
    Donor_ASVs = set([row for row in In.read().split("\n") if row!=""])
    In.close()
    
    print("Normalizing")
    vects = list(zip(*vects))
    temp = []
    for row in vects:
        tempsum = sum(row)
        temp.append([a/tempsum for a in row])
    vects = list(zip(*temp))
    
    print("Filtering")
    Species = {}
    Colors = {}
    for i in range(len(ASV_IDs)):
        tax = ros[ASV_IDs[i]][1].split(";")
        if tax[6]==species:
            new_ID = tax[6]
            if ASV_IDs[i] in Donor_ASVs:
                new_ID = 'Donor'
                Colors[new_ID] = 'green'
            else:
                new_ID = 'non-Donor'
                Colors[new_ID] = 'orange'
            if new_ID in Species:
                for j in range(len(sample_IDs)):
                    Species[new_ID][j] += vects[i][j]
            else:
                Species[new_ID] = list(vects[i])
    Species_names = sorted(Species)
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
    
    data = pd.read_csv(tempfile, sep='\t')
    data_long = pd.melt(data, id_vars=['Treatment', 'Day', 'Site', 'Sex', 'Animal'], 
                       var_name='Species', value_name='Relative Abundance')
    data_long['Day'] = data_long['Day'].astype(str)
    
    if wLeg == '1':
        fig, ax = plt.subplots()
        legend_handles = [mlines.Line2D([], [], color=Colors[name], marker='o', 
                         linestyle='-', label=name) for i, name in enumerate(Species_names)]
        ax = plt.gca()
        legend = ax.legend(handles=legend_handles, title='', loc='center', 
                         ncol=1, fancybox=True, shadow=True)
        plt.setp(legend.get_texts(), fontweight='bold')
        ax.axis('off')
        fig.canvas.draw()
    else:
        plt.figure(figsize=(10, 4))
        fig, ax = plt.subplots()
        
        # Define treatment and site order
        data_long['Treatment'] = pd.Categorical(data_long['Treatment'], 
                                              categories=['UNTR', 'CMT', 'ABX3CMT', 'ABX10'], 
                                              ordered=True)
        data_long['Site'] = pd.Categorical(data_long['Site'],
                                         categories=['LJ', 'GR'],
                                         ordered=True)
        
        # Create FacetGrid
        g = sns.FacetGrid(data_long, row='Site', col='Treatment', 
                         hue='Species', margin_titles=False, 
                         palette=Colors, sharex=True, sharey=True)
        
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
        
        g.fig.suptitle(species.replace("_"," "), fontweight='bold', fontsize=20)
        plt.tight_layout()
        
        # Calculate baseline and endpoint statistics
        print("\nBaseline (Day -2) Statistics by Site:")
        print("Site\tCategory\tMean\tStd Dev\tN")
        print("-" * 60)

        baseline_stats = data_long[data_long['Day'] == '-2'].groupby(['Site', 'Species'])['Relative Abundance'].agg(['mean', 'std', 'count']).reset_index()
        baseline_stats = baseline_stats.sort_values(['Site', 'Species'])

        for _, row in baseline_stats.iterrows():
            print(f"{row['Site']}\t{row['Species']}\t{row['mean']:.4f}\t{row['std']:.4f}\t{row['count']}")

        print("\nEndpoint (Day 60) Statistics by Site and Treatment:")
        print("Treatment\tSite\tCategory\tMean\tStd Dev\tN")
        print("-" * 80)

        endpoint_stats = data_long[data_long['Day'] == '60'].groupby(['Treatment', 'Site', 'Species'])['Relative Abundance'].agg(['mean', 'std', 'count']).reset_index()
        endpoint_stats = endpoint_stats.sort_values(['Treatment', 'Site', 'Species'])

        for _, row in endpoint_stats.iterrows():
            print(f"{row['Treatment']}\t{row['Site']}\t{row['Species']}\t{row['mean']:.4f}\t{row['std']:.4f}\t{row['count']}")
            
    plt.savefig(out_fname)
