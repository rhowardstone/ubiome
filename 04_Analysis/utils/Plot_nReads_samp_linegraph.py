import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Error - usage:\n >>> python Plot_alpha_diversity_linegraph.py [In.tsv] [Out.png]\n")
        exit()

    in_fname, out_fname = sys.argv[1:]

    # Read the data with specified column names
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
    
    # Setting the seaborn style
    sns.set(style="whitegrid")
    
    palette = sns.color_palette("deep", 4)
    
    # Define a color map for groups, for example
    group_colors = {
        "CMT": palette[2],
        "ABX10": palette[3],
        "ABX3CMT": palette[1],
        "UNTR": palette[0]
    }
    
    # Default color for categories not in group_colors
    default_color = "gray"
    
    # Plot
    plt.figure(figsize=(10, 4))
    # Iterate over each unique group to plot them separately. This allows for custom line styles per category.
    for (group, category), group_data in data.groupby(["Group", "Category"]):
        # Choose the line style based on the category
        line_style = "--" if category == "GR" else "-"
        # Get the color for the group, or use the default color if the group is not in the map
        line_color = group_colors.get(group, default_color)
        
        if category == 'GR':
            label=f"{group} (GR)"
        else:
            label=f"{group} (LJ)"
        sns.lineplot(data=group_data, x="Day", y="Value", label=label, linestyle=line_style, errorbar='sd', color=line_color)

    # Setting the order of 'Day' values explicitly
    day_order = ["0", "1", "3", "5", "8", "10", "30", "60"]
    plt.xticks(ticks=range(len(day_order)), labels=day_order, fontsize=14)

    # Enhancing plot aesthetics
    plt.title("")
    plt.xlabel("Day")
    plt.ylabel("Number of Reads", fontsize=24)
    #plt.legend(title='Treatment', loc='upper left', bbox_to_anchor=(1, 1))
    plt.legend().remove()
    plt.autoscale(enable=True, axis='x', tight=True)
    plt.tight_layout()  # Adjust layout

    # Save the plot to file
    plt.savefig(out_fname)







    
    

