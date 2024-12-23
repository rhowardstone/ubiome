import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys

if __name__ == "__main__":
	if len(sys.argv) != 4:
		print("Error - usage:\n >>> python Plot_alpha_diversity_linegraph.py [In.tsv] [0/1 with legend?] [Out.png]\n")
		exit()

	in_fname, wLeg, out_fname = sys.argv[1:]

	# Read the data with specified column names
	data = pd.read_csv(in_fname, sep="\t", header=None, names=["Group", "Day", "Category", "Number of ASVs"])

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
		sns.lineplot(data=group_data, x="Day", y="Number of ASVs", label=label, linestyle=line_style, errorbar='sd', color=line_color)

	# Setting the order of 'Day' values explicitly
	#day_order = ["0", "1", "3", "5", "8", "10", "30", "60"]
	#plt.xticks(ticks=range(len(day_order)), labels=day_order, fontsize=14)
	#plt.tick_params(
	#	axis='x',		  # changes apply to the x-axis
	#	which='both',	  # both major and minor ticks are affected
	#	bottom=False,	  # ticks along the bottom edge are off
	#	top=False,		 # ticks along the top edge are off
	#	labelbottom=False) # labels along the bottom edge are off
	plt.tick_params(axis='y', labelsize=18) #, labelweight='bold')
	plt.tick_params(axis='x', labelsize=18)
	
	ax = plt.gca()

	# Set y-axis tick labels to bold
	for label in ax.get_yticklabels():
		label.set_fontweight('bold')
	for label in ax.get_xticklabels():
		label.set_fontweight('bold')
		
	# Enhancing plot aesthetics
	plt.title("")
	plt.xlabel("")
	plt.ylabel("") #Number of ASVs", fontsize=24)
	if wLeg == '1':
		#plt.legend(title='Treatment', loc='upper left', bbox_to_anchor=(1, 1))
		legend = plt.legend(title='Treatment (Site)', loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=4, fancybox=True, shadow=True)
		legend.get_title().set_fontweight('bold')
		plt.setp(legend.get_texts(), fontweight='bold')
		plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False) #disable xticks
	else:
		plt.legend().remove()
	
	#plt.yscale('symlog')
	#plt.ylim([0,500])
	plt.autoscale(enable=True, axis='x', tight=True)
	plt.tight_layout()  # Adjust layout
	
	
	
	
	# Print ASV numbers for each group, day, and site
	print("\nNumber of ASVs by Group, Day, and Site:")
	print("Day\tGroup\tSite\tASVs\tStd Dev")
	print("-" * 50)

	# Group the data and calculate mean and std
	stats = data.groupby(['Day', 'Group', 'Category'])['Number of ASVs'].agg(['mean', 'std']).reset_index()

	# Sort by Day numerically (removing 'd' if present), then by Group
	stats['Day_num'] = stats['Day'].str.replace('d', '').astype(float)
	stats = stats.sort_values(['Day_num', 'Group', 'Category'])

	# Print the statistics
	for _, row in stats.iterrows():
		print(f"{row['Day']}\t{row['Group']}\t{row['Category']}\t{row['mean']:.1f}\t{row['std']:.1f}")

	print("\nOverall averages by Group and Site:")
	print("Group\tSite\tMean ASVs\tStd Dev")
	print("-" * 50)

	# Calculate overall averages by Group and Site
	overall_stats = data.groupby(['Group', 'Category'])['Number of ASVs'].agg(['mean', 'std']).reset_index()
	for _, row in overall_stats.iterrows():
		print(f"{row['Group']}\t{row['Category']}\t{row['mean']:.1f}\t{row['std']:.1f}")
		
	# Save the plot to file
	plt.savefig(out_fname)







	
	

