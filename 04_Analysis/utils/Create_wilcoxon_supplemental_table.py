import sys
import pandas as pd
import numpy as np
from scipy.stats import ranksums
import statsmodels.stats.multitest as smm
from utils import read_rosetta_indexed
from multiprocessing import Pool, cpu_count
from functools import partial
import matplotlib.pyplot as plt

def process_taxon(df, tax_level, raw_df, taxon):
	"""Process statistics for a single taxon"""
	# Get relative abundances for statistical testing
	gr_rel_data = list(df[(df[tax_level] == taxon) & (df['Site'] == 'GR')]['Relative Abundance'])
	lj_rel_data = list(df[(df[tax_level] == taxon) & (df['Site'] == 'LJ')]['Relative Abundance'])
	
	# Get raw counts for totals
	gr_raw_data = list(raw_df[(raw_df[tax_level] == taxon) & (raw_df['Site'] == 'GR')]['Raw Abundance'])
	lj_raw_data = list(raw_df[(raw_df[tax_level] == taxon) & (raw_df['Site'] == 'LJ')]['Raw Abundance'])
	
	if len(gr_rel_data) > 0 and len(lj_rel_data) > 0:
		# Always perform the statistical test - ranksum can handle zeros
		stat, p_val = ranksums(gr_rel_data, lj_rel_data, alternative='two-sided')
		
		# Sum raw counts
		gr_total = sum(gr_raw_data)
		lj_total = sum(lj_raw_data)
		return (taxon, p_val, gr_total, lj_total)
	return None

if __name__ == "__main__":
	if len(sys.argv) != 4:
		print("Error - usage:\n >>> python Wilcoxon_Analysis.py [Rosetta.csv] [tax-level] [output_fname]\n")
		exit()
	
	in_fname, tax_level, output_file = sys.argv[1:]
	tax_level = tax_level.upper()
	M, indices, sample_IDs, taxa_IDs = read_rosetta_indexed(in_fname, relative=False, taxonomy=True)
	print(len(M), "samples,", len(M[0]), "taxa for tax-level:", tax_level)
	taxa_IDs = [text.replace("_", "\n", 1).replace("_", " ") for text in taxa_IDs]
	
	# Prepare both raw and relative abundance data
	dat_raw = []
	dat_rel = []
	for j in range(len(M)):
		tempsum = sum(M[j])
		tmpIDs = sample_IDs[j].split("_")
		if len(tmpIDs) > 1:
			group, day, site, sex = tmpIDs[:4]
			if day == 'd-2':
				for i in range(len(M[j])):
					name = taxa_IDs[i]
					raw_abund = M[j][i]
					rel_abund = raw_abund/tempsum if tempsum > 0 else 0
					dat_raw.append([name, group, day, site, sex, raw_abund])
					dat_rel.append([name, group, day, site, sex, rel_abund])
	
	# Create DataFrames for both raw and relative abundances
	df_raw = pd.DataFrame(dat_raw, columns=(tax_level + ', group, day, Site, Sex, Raw Abundance').split(', '))
	df_rel = pd.DataFrame(dat_rel, columns=(tax_level + ', group, day, Site, Sex, Relative Abundance').split(', '))
	print(in_fname, tax_level)
	
	# Set up parallel processing
	num_cores = cpu_count()
	print(f"Using {num_cores} CPU cores")
	
	# Create pool and process taxa in parallel
	with Pool(num_cores) as pool:
		process_func = partial(process_taxon, df_rel, tax_level, df_raw)
		results = pool.map(process_func, taxa_IDs)
	
	# Filter out None results and unpack
	results = [r for r in results if r is not None]
	if not results:  # Check if results is empty
		print("No valid results found!")
		exit()
		
	taxa_names, p_vals, gr_totals, lj_totals = zip(*results)
	
	# Perform Bonferroni correction
	reject, p_vals_corrected, alphacSidak, alphacBonf = smm.multipletests(p_vals, alpha=0.05, method='bonferroni')
	
	# Assign significance levels
	significance = ["***" if p <= 0.001 else 
				   "**" if p <= 0.01 else 
				   "*" if p <= 0.05 else 
				   "Not Significant" for p in p_vals_corrected]
	
	# Define significance counts here, before using it
	sig_counts = {
		"Not Significant (p > 0.05)": sum(1 for s in significance if s == "Not Significant"),
		"*   (0.01 < p <= 0.05)": sum(1 for s in significance if s == "*"),
		"**  (0.001 < p <= 0.01)": sum(1 for s in significance if s == "**"),
		"*** (p <= 0.001)": sum(1 for s in significance if s == "***")
	}
	
	# Create scatter plot
	# Create scatter plot with adjusted figure size
	plt.figure(figsize=(12, 10))

	# Define colors for significance levels
	colors = {
		"***": "red",
		"**": "yellow",
		"*": "lime",
		"Not Significant": "blue"
	}

	# Create subplot with specific grid placement
	ax = plt.subplot(111)

	# Plot points by significance level
	for sig_level in ["***", "**", "*", "Not Significant"]:
		mask = [s == sig_level for s in significance]
		if any(mask):
			x = [gr_totals[i] for i in range(len(mask)) if mask[i]]
			y = [lj_totals[i] for i in range(len(mask)) if mask[i]]
			ax.scatter(x, y, c=colors[sig_level], label=sig_level, alpha=0.6)

	# Add diagonal line
	max_val = max(max(gr_totals), max(lj_totals))
	ax.plot([0, max_val], [0, max_val], 'k--', alpha=0.3)
	
	
	
	for label in ax.get_yticklabels():
		label.set_fontweight('bold')
		label.set_fontsize(20)
	for label in ax.get_xticklabels():
		label.set_fontweight('bold')
		label.set_fontsize(20)
	
	# Set labels and title
	ax.set_xlabel('Groton Total Reads', fontsize=20, fontweight='bold')
	ax.set_ylabel('La Jolla Total Reads', fontsize=20, fontweight='bold')
	ax.set_title(f'{tax_level}', fontsize=32, fontweight='bold')

	# Set scales
	ax.set_xscale('symlog')
	ax.set_yscale('symlog')
	
	ax.set_xlim(0, max_val)
	ax.set_ylim(0, max_val)
	
	# Make axes equal
	ax.set_aspect('equal')

	# Add legend outside, make bold title and items
	legend = ax.legend(title='Significance (baseline)', fontsize=12, bbox_to_anchor=(1.05, 1), loc='upper left')
	legend.get_title().set_fontweight('bold')
	plt.setp(legend.get_texts(), fontweight='bold')
	
	# Adjust layout to prevent cutting off
	plt.tight_layout()
	plt.subplots_adjust(right=0.85)  # Make room for legend

	# Save plot
	plot_fname = output_file.replace('.tsv', '_scatter.png').replace("data/","Figs/")
	plt.savefig(plot_fname, bbox_inches='tight', dpi=300)
	plt.close()
		
	# Create output file
	with open(output_file, 'w') as f:
		# Write summary header
		f.write("\nSummary of Results:\n")
		f.write("-" * 20)
		f.write("\n")
		for level, count in sig_counts.items():
			f.write(f"{level}: {count}\n")
			
		# Write data header
		f.write("Taxon\tRaw p-value\tCorrected p-value\tSignificance\tGroton Total Reads\tLa Jolla Total Reads\n")
		
		# Write data
		for i, (name, p, p_corr, sig, gr_total, lj_total) in enumerate(zip(
			taxa_names, p_vals, p_vals_corrected, significance, 
			gr_totals, lj_totals)):
			
			namefmt = name.replace("\n", " ")
			f.write(f"{namefmt}\t{p:.4f}\t{p_corr:.4f}\t{sig}\t{int(gr_total)}\t{int(lj_total)}\n")
	
	print(f"\nResults written to: {output_file}")
	print(f"Scatter plot saved as: {plot_fname}")
