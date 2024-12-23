import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys
from utils import read_rosetta
# UNTR_d0_GR_M_a1

if __name__ == "__main__":
	if len(sys.argv)!=6:
		print("Error - usage:\n >>> python Plot_genus_linegraphs.py [Rosetta.csv] ['Species-name'] [tempfile.tsv] [0/1 ASVs?] [Out.png]\n")
		exit()
	in_fname, genus, tempfile, toASV, out_fname = sys.argv[1:]
	print("Reading the data")
	sample_IDs, ros = read_rosetta(in_fname, cols=True) #maps ASV ID:(seq,tax,abund) 
	ASV_IDs = [ID for ID in ros]
	vects = [ros[ID][2] for ID in ASV_IDs]
	
	print("Normalizing")
	vects = list(zip(*vects)) #transpose - rows are now samples
	temp = []
	for row in vects:
		tempsum = sum(row)
		temp.append([a/tempsum for a in row])
	vects = list(zip(*temp)) #transpose back - rows are again ASVs
	
	print("Filtering")
	Species = {}
	for i in range(len(ASV_IDs)):  #filter only those ASVs we intend to plot, sum by species
		tax = ros[ASV_IDs[i]][1].split(";")
		if tax[6]==genus:
			if toASV=='1':
				#strain = tax[7]
				#genus = strain.split(" ")[0]
				#strain = tax[7] #genus[0]+" "+" ".join(strain.split(" ")[1:])
				new_ID = '#'+ASV_IDs[i][:8]#+' '+strain
			else:
				new_ID = tax[7] #ASV_IDs[i] #tax[6]
			if new_ID in Species:
				for j in range(len(sample_IDs)):
					Species[new_ID][j] += vects[i][j]
			else:
				Species[new_ID] = list(vects[i])
	Species_names = [ID for ID in Species]
	vects = list(zip(*[Species[ID] for ID in Species_names]))  #transpose - rows are samples, columns are Species
	
	print("Collating")
	Out = open(tempfile, 'w+')
	Out.write('\t'.join('Treatment Day Site Sex Animal'.split() + Species_names)+"\n")
	for i in range(len(vects)):
		if not sample_IDs[i].startswith('W'): #exclude wildtype samples
			temp = sample_IDs[i].split("_")
			temp[1] = temp[1][1:]  #remove the 'd' prepending the day, but contonue to treat as string
			Out.write("\t".join(temp) + '\t' + '\t'.join([str(a) for a in list(vects[i])]) + '\n')
		else:
			temp = ['W', sample_IDs[i], 'W', 'W', 'W']
			#Out.write("\t".join(temp) + '\t' + '\t'.join([str(a) for a in list(vects[i])]) + '\n')
	Out.close()
	

	# Sample data creation
	# Assuming `data.csv` is your file where columns are ['Treatment', 'Day', 'Site', 'Sex', 'Animal', 'ASV1', 'ASV2', ...]

	# Load your dataset
	data = pd.read_csv(tempfile, sep='\t')

	# Melt the DataFrame to make it long-form
	data_long = pd.melt(data, id_vars=['Treatment', 'Day', 'Site', 'Sex', 'Animal'], var_name='Strain', value_name='Relative Abundance')

	# Convert 'Day' to string if it's not already, to ensure line plots are correctly generated
	data_long['Day'] = data_long['Day'].astype(str)

	# Creating the FacetGrid
	# Here, we're creating a grid with one row per 'Site' and one column per 'Treatment',
	# coloring by 'ASV' to differentiate the lines for each ASV.
	g = sns.FacetGrid(data_long, row='Site', col='Treatment', hue='Strain', margin_titles=True, palette='tab10', sharex=False, sharey=True)

	# Mapping the lineplot
	g.map(sns.lineplot, 'Day', 'Relative Abundance', linestyle='', marker="o")

	# Adding a legend
	#g.add_legend()

	# Adjust the titles
	g.set_titles(row_template='{row_name}', col_template='{col_name}')
	plt.legend(title='ASV' if toASV=='1' else 'Strain', loc='upper left', bbox_to_anchor=(1, 0.75)) #, handles=handles)
	# Optional: Adjusting axis labels and other aesthetic elements
	g.set_axis_labels("Day", "Relative Abundance")
	g.set(ylim=(0, None))  # Adjust based on your data's range
	plt.tight_layout()
	plt.savefig(out_fname)  # Save the plot to a file



