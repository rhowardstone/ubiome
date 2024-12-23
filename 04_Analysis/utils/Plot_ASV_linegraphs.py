import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys
from utils import read_rosetta
# UNTR_d0_GR_M_a1

if __name__ == "__main__":
	if len(sys.argv)!=5:
		print("Error - usage:\n >>> python Plot_ASV_linegraphs.py [Rosetta.csv] [ASV_list.txt] [tempfile.tsv] [Out.png]\n")
		exit()
	in_fname, asvs_fname, tempfile, out_fname = sys.argv[1:]
	print("Reading the data")
	sample_IDs, ros = read_rosetta(in_fname, cols=True) #maps ASV ID:(seq,tax,abund) 
	ASV_IDs = [ID for ID in ros]
	vects = [ros[ID][2] for ID in ASV_IDs]
	
	In = open(asvs_fname)
	to_plot = set([row for row in In.read().split("\n") if row!=""])
	In.close()
	
	print("Normalizing")
	vects = list(zip(*vects)) #transpose - rows are now samples
	temp = []
	for row in vects:
		tempsum = sum(row)
		temp.append([a/tempsum for a in row])
	vects = list(zip(*temp)) #transpose back - rows are again ASVs
	
	print("Filtering")
	temp_vects, temp_IDs = [], []
	for i in range(len(ASV_IDs)):  #filter only those ASVs we intend to plot
		if ASV_IDs[i] in to_plot:
			temp_vects.append(vects[i])
			temp_IDs.append(ASV_IDs[i])
	vects = list(zip(*temp_vects)) #transpose again - series (columns) will be ASVs, rows are samples
	ASV_IDs = temp_IDs.copy()
	
	print(len(vects), len(vects[0]))
	print(len(ASV_IDs))
	print(len(sample_IDs))
	
	print("Collating")
	Out = open(tempfile, 'w+')
	Out.write('\t'.join('Treatment Day Site Sex Animal'.split() + ASV_IDs)+"\n")
	for i in range(len(vects)):
		if not sample_IDs[i].startswith('W'): #exclude wildtype samples
			temp = sample_IDs[i].split("_")
			temp[1] = temp[1][1:]  #remove the 'd' prepending the day, but contonue to treat as string
			Out.write("\t".join(temp) + '\t' + '\t'.join([str(a) for a in list(vects[i])]) + '\n')
	Out.close()
	

	# Sample data creation
	# Assuming `data.csv` is your file where columns are ['Treatment', 'Day', 'Site', 'Sex', 'Animal', 'ASV1', 'ASV2', ...]

	# Load your dataset
	data = pd.read_csv(tempfile, sep='\t')

	# Melt the DataFrame to make it long-form
	data_long = pd.melt(data, id_vars=['Treatment', 'Day', 'Site', 'Sex', 'Animal'], var_name='ASV', value_name='Relative Abundance')

	# Convert 'Day' to string if it's not already, to ensure line plots are correctly generated
	data_long['Day'] = data_long['Day'].astype(str)

	# Creating the FacetGrid
	# Here, we're creating a grid with one row per 'Site' and one column per 'Treatment',
	# coloring by 'ASV' to differentiate the lines for each ASV.
	g = sns.FacetGrid(data_long, row='Site', col='Treatment', hue='ASV', margin_titles=True, palette='tab10', sharex=False, sharey=False)

	# Mapping the lineplot
	g.map(sns.lineplot, 'Day', 'Relative Abundance', marker="o")

	# Adding a legend
	g.add_legend()

	# Adjust the titles
	g.set_titles(row_template='{row_name}', col_template='{col_name}')

	# Optional: Adjusting axis labels and other aesthetic elements
	g.set_axis_labels("Day", "Relative Abundance")
	g.set(ylim=(0, None))  # Adjust based on your data's range

	plt.savefig(out_fname)  # Save the plot to a file



