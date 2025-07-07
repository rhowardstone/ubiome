import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys
import numpy as np

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Error - usage:\n >>> python plot_linegraph_style.py [In.tsv] [Out.png]\n")
        exit()

    in_fname, out_fname = sys.argv[1:]

    # Read the data with specified column names
    data = pd.read_csv(in_fname, sep="\t", header=None, names=["Group", "Day", "Site", "Category", "Bray-Curtis Dissimilarity"])

    data['Day'] = data['Day'].astype(str)
    sns.set(style="whitegrid")
    palette = sns.color_palette("deep", 4)
    group_colors = {"CMT": palette[2], "ABX10": palette[3], "ABX3CMT": palette[1], "UNTR": palette[0]}
    default_color = "gray"
    
    # Plot
    plt.figure(figsize=(16, 10))
    
    #day_order = ["0", "1", "3", "5", "8", "10", "30", "60"]
    #plt.xticks(ticks=range(len(day_order)), labels=day_order)
    
    legend_handles = {}
    # Iterate over each unique group to plot them separately. This allows for custom line styles per category.
    for (group, site, category), group_data in data.groupby(["Group", "Site", "Category"]):
        # Choose the line style based on the site
        line_style = "--" if site == "GR" else "-"
        # Get the color for the group, or use the default color if the group is not in the map
        line_color = group_colors.get(group, default_color)
        
        if category == 'Within':
            line_color = 'black'
            label=f"{group} (Within: {site})"
            line = sns.lineplot(data=group_data, x="Day", y="Bray-Curtis Dissimilarity", label=label, linestyle=line_style, errorbar=None, color=line_color) #errorbar='sd',
        else:
            label=f"{group}"
            line = sns.lineplot(data=group_data, x="Day", y="Bray-Curtis Dissimilarity", label=label, linestyle=line_style, errorbar='sd', color=line_color)
        legend_handles[label] = line.lines[-1]

    ax = plt.gca()
    plt.ylim(0,1)
    ax.set_yticks(np.arange(0, 1.2, 0.1))
    
    # Set y-axis tick labels to bold
    for label in ax.get_yticklabels():
        label.set_fontweight('bold')
        label.set_fontsize(22)
    for label in ax.get_xticklabels():
        label.set_fontweight('bold')
        label.set_fontsize(26)
        
    # Enhancing plot aesthetics
    plt.title("Bray-Curtis Dissimilarity", fontweight='bold', fontsize=32)
    plt.xlabel("Day", fontsize=24, weight='bold')

    plt.ylabel("")
    
    desired_order = 'UNTR CMT ABX10 ABX3CMT'.split() #sorted([label for label in legend_handles if 'Within' not in label], reverse=True)
    desired_order += [label for label in legend_handles if 'Within' in label]  # Append 'Within' entries last

    ordered_handles = [legend_handles[label] for label in desired_order]
    ordered_labels = [label for label in desired_order]
    
    
    plt.autoscale(enable=True, axis='x', tight=True)
    # Create legend with specified order
    #Below, 4 columns:    #plt.legend(ordered_handles, ordered_labels, title='', loc='upper center', bbox_to_anchor=(0.5, -0.35), ncol=3, fancybox=True, shadow=True, prop={'size': 20, 'weight': 'bold'}) #, fontweight='bold')
    plt.legend(ordered_handles, ordered_labels, title='', loc='center left', bbox_to_anchor=(1, 0.5), ncol=1, fancybox=True, shadow=True, prop={'size': 20, 'weight': 'bold'}) #, fontweight='bold')
   
    #plt.legend(title='Treatment', loc='upper left', bbox_to_anchor=(1, 1))
    
    plt.tight_layout()  # Adjust layout

    # Save the plot to file
    plt.savefig(out_fname)
    

    summary = data.groupby(['Group', 'Day'])['Bray-Curtis Dissimilarity'].agg(['mean', 'std']).reset_index()
    print()
    print("Group\tDay\tBC (mean)\tBC (stdev)")
    for _, row in summary.iterrows():
        print(f"{row['Group']}\t{row['Day']}\t{row['mean']:.4f}\t{row['std']:.4f}")
    print()








    
    
