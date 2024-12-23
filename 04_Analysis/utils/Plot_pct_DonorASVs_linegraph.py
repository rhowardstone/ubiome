import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Error - usage:\n >>> python Plot_alpha_diversity_linegraph.py [In.tsv] [Out.png]\n")
        sys.exit()

    in_fname, out_fname = sys.argv[1:]

    data = pd.read_csv(in_fname, sep="\t", header=None, names=["Group", "Day", "Category", "Value"])
    data['Day'] = pd.to_numeric(data['Day'], errors='coerce')
    	
    # Sort data by 'Day' numerically
    custom_order = ['UNTR', 'CMT', 'ABX3CMT', 'ABX10']
    data['Group'] = pd.Categorical(data['Group'], categories=custom_order, ordered=True)
    	    
    # Sort data by 'Group' first, then 'Day' numerically
    data.sort_values(['Group', 'Day'], inplace=True)
    data.sort_values('Day', inplace=True)
    # Prepend 'd' to each entry in the 'Day' column
    data['Day'] = data['Day'].astype(str) #'d' + 
    
    sns.set(style="whitegrid")
    
    palette = sns.color_palette("deep", 4)
    group_colors = {"CMT": palette[2], "ABX10": palette[3], "ABX3CMT": palette[1], "UNTR": palette[0]}
    
    plt.figure(figsize=(10, 6))
    for (group, category), group_data in data.groupby(["Group", "Category"], observed=True):
        # Choose the line style based on the category
        line_style = "--" if category == "GR" else "-"
        # Get the color for the group, or use the default color if the group is not in the map
        line_color = group_colors.get(group, 'black')
        
        #if category == 'GR':
        label=f"{group} ({category})"
        #else:
        #    label=f"{group} (LJ)"
        sns.lineplot(data=group_data, x="Day", y="Value", label=label, linestyle=line_style, errorbar='sd', color=line_color)
    #for (group_tuple, group_data) in data.groupby(["Group"]):
    #    group = group_tuple if isinstance(group_tuple, str) else group_tuple[0]  # Ensure group is a string
    #    # Plotting each group with a specific color
    #    sns.lineplot(data=group_data[group_data["Category"] == "LJ"], x="Day", y="Number of Wild ASVs", label=group, linestyle='-', color=group_colors[group])
    #    sns.lineplot(data=group_data[group_data["Category"] == "GR"], x="Day", y="Number of Wild ASVs", linestyle='--', color=group_colors[group]), label='_nolegend_')

    # Custom legend for site categories
    #handles, labels = plt.gca().get_legend_handles_labels()
    # Add custom entries for "GR" and "LJ"
    #handles.append(plt.Line2D([0], [0], color='black', linestyle='--', label='GR'))
    #handles.append(plt.Line2D([0], [0], color='black', linestyle='-', label='LJ'))
    #labels.append('GR')
    #labels.append('LJ')
    
    #plt.legend(title='Treatment (Site)', loc='upper left', bbox_to_anchor=(1, 1)) #, handles=handles)
    plt.legend().remove()
    plt.yticks(fontsize=20, fontweight='bold')
    plt.xticks(fontsize=20, fontweight='bold')
    plt.ylabel("")
    plt.xlabel(xlabel='Day', fontsize=20, fontweight='bold')
    
    plt.title("Donor ASVs as proportion of total ASVs", fontsize=20, fontweight='bold')
    plt.autoscale(enable=True, axis='x', tight=True)
    plt.tight_layout()  # Adjust layout
    
    plt.gca().tick_params(axis='x',          # Changes apply to the y-axis
                      which='both',      # Applies changes to both the major and minor ticks
                      bottom=True,         # Keeps the left ticks (change to `right=True` if you're dealing with the right y-axis)
                      labelbottom=False)
    
    plt.savefig(out_fname)



    
    

