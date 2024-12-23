import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys


if __name__ == "__main__":
	if len(sys.argv)!=4:
		print("Error - usage:\n >>> python Plot_faucetGrid.py [In.tsv] [Yaxlbl] [Out.png]\n")
		exit()
	in_fname, axlbl, out_fname = sys.argv[1:]
	# Read the data
	data = pd.read_csv(in_fname, sep="\t")
	data['Day'] = pd.to_numeric(data['Day'], errors='coerce')
	
	# Sort data by 'Day' numerically
	custom_order = ['UNTR', 'FMT', 'ABX3FMT', 'ABX10']
	data['Group'] = pd.Categorical(data['Group'], categories=custom_order, ordered=True)
	    
	# Sort data by 'Group' first, then 'Day' numerically
	data.sort_values(['Group', 'Day'], inplace=True)
	data.sort_values('Day', inplace=True)
	# Prepend 'd' to each entry in the 'Day' column
	data['Day'] = data['Day'].astype(str) #'d' + 

	# Normalize by row sum for columns with counts/values
	#columns_to_normalize = data.columns[5:]  # Adjust as needed
	#data[columns_to_normalize] = data[columns_to_normalize].div(data[columns_to_normalize].sum(axis=1), axis=0)

	# Melt the DataFrame for seaborn
	data_long = pd.melt(data, id_vars=["Group", "Day", "Site", "Sex", "Animal"], var_name="Outcome", value_name=axlbl)

	# Plotting
	g = sns.FacetGrid(data_long, col="Group", row="Site", hue="Outcome", margin_titles=True, sharex=False)

	# Map the lineplot
	g.map(sns.lineplot, "Day", axlbl)

	# Adjust the titles
	g.set_titles(row_template='{row_name}', col_template='{col_name}')

	g.add_legend()

	plt.savefig(out_fname)

