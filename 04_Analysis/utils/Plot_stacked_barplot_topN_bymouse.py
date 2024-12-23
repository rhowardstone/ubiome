import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import os

def get_top_species_by_plot(subset, n=20):
	# Calculate the average relative abundance for each species within the subset
	avg_abundance = subset.groupby('Taxonomy')['Relative_Abundance'].mean().nlargest(n)
	top_species = avg_abundance.index.tolist()
	return top_species

def process_data(input_file, output_dir, global_top_n=20, by_group=False):
	# Load the data
	df = pd.read_csv(input_file)
	
	# Remove W1 and W2 columns
	df = df.drop(columns=['W1', 'W2'])
	
	# Extract metadata from column names
	metadata = pd.DataFrame(df.columns[1:].str.split('_').tolist(), columns=['GROUP', 'DAY', 'SITE', 'SEX', 'ANIMAL'])
	metadata['Sample'] = df.columns[1:]
	
	# Melt the dataframe for easier plotting
	df_melted = df.melt(id_vars=['Taxonomy'], var_name='Sample', value_name='Abundance')
	df_melted = df_melted[df_melted['Abundance'] > 0]
	
	# Add metadata columns to the melted dataframe
	df_melted = df_melted.merge(metadata, on='Sample')
	
	# Ensure the column 'Relative_Abundance' is calculated correctly
	df_melted['Relative_Abundance'] = df_melted.groupby('Sample')['Abundance'].transform(lambda x: x / x.sum())
	
	# Create plots
	groups = df_melted['GROUP'].unique()
	days = df_melted['DAY'].unique()
	
	for group in reversed(groups):
		for day in days:
			subset = df_melted[(df_melted['GROUP'] == group) & (df_melted['DAY'] == day)]
			if not subset.empty:
				# Get top species based on average relative abundance within this subset
				top_species = get_top_species_by_plot(subset, global_top_n)
				#print(f"Top species in plot for Group: {group}, Day: {day}: {top_species}")  # Debug statement
				
				# Determine colors for the top species
				colors = sns.color_palette("tab20", n_colors=len(top_species)) + ['darkgrey']
				color_mapping = {species: colors[idx] for idx, species in enumerate(top_species + ['Other'])}

				# Separate top species and others
				subset = subset.copy()
				subset['Taxonomy'] = subset['Taxonomy'].apply(lambda x: x if x in top_species else 'Other')

				for site in subset['SITE'].unique():
					plot_data = subset[subset['SITE'] == site]
					
					if not plot_data.empty:
						plt.figure(figsize=(16, 10))
						
						# Pivot the data for stacked bar plot
						pivot_data = plot_data.pivot_table(values='Relative_Abundance', index='ANIMAL', columns='Taxonomy', aggfunc='sum', fill_value=0)
						# Sort the animals index numerically after removing the first letter
						pivot_data.index = sorted(pivot_data.index, key=lambda x: int(x[1:]))

						actual_species = [species for species in top_species if species in pivot_data.columns]
						if 'Other' in pivot_data.columns:
							pivot_data = pivot_data[actual_species + ['Other']]  # Ensure consistent column order
						else:
							pivot_data = pivot_data[actual_species]
						
						# Plot stacked bar
						bottom = None
						animals = pivot_data.index
						for taxon in pivot_data.columns:
							plt.bar(animals, pivot_data[taxon], bottom=bottom, color=color_mapping[taxon], label=taxon)
							if bottom is None:
								bottom = pivot_data[taxon]
							else:
								bottom += pivot_data[taxon]
						
						plt.title(f'Group: {group}, Day: {day}, Site: {site}', fontsize=20, fontweight='bold')
						plt.xlabel('Animal', fontsize=16, fontweight='bold')
						plt.ylabel('Relative Abundance', fontsize=16, fontweight='bold')
						plt.xticks(rotation=90, fontsize=12, fontweight='bold')
						plt.yticks(fontsize=12, fontweight='bold')
						plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title='Taxonomy', fontsize=12, title_fontsize='14', frameon=True, shadow=True)
						
						# Marking males and females on the x-axis
						x_labels = pivot_data.index.unique()
						for label in x_labels:
							if label.startswith('M'):
								plt.gca().get_xticklabels()[list(x_labels).index(label)].set_color('blue')
							elif label.startswith('F'):
								plt.gca().get_xticklabels()[list(x_labels).index(label)].set_color('red')
						
						plt.ylim(0, 1)
						plt.tight_layout()
						
						# Save plot
						os.makedirs(output_dir, exist_ok=True)
						plot_file = os.path.join(output_dir, f'{group}_{day}_{site}.png')
						plt.savefig(plot_file, bbox_inches='tight')
						plt.close()

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Plot relative abundance of species from CSV file')
	parser.add_argument('input_file', type=str, help='Input CSV file')
	parser.add_argument('output_dir', type=str, help='Output directory for plots')
	parser.add_argument('--global_top_n', type=int, default=20, help='Number of top species to consider globally or by group')
	parser.add_argument('--by_group', action='store_true', help='Use top N species by group instead of globally')
	
	args = parser.parse_args()
	
	process_data(args.input_file, args.output_dir, args.global_top_n, args.by_group)

