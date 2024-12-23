import sys
import seaborn as sns
import pandas as pd
from scipy.stats import ranksums
from matplotlib import pyplot as plt
from utils import read_rosetta_indexed#(fname):
from hashlib import md5
#import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker
from statannot import add_stat_annotation

def hash_sequence(sequence):
    # Using MD5 hashing
    # Return the hexadecimal representation of the binary hash
    return md5(sequence.encode('utf-8')).hexdigest()  #THIS DOES NOT MATCH THE STRAINID ASV IDs from sbAnalyzer - FIND EXACT HASH ALGO USED

''' read_rosetta_indexed  Returns M, indices, cols where:
M is a matrix with rows as samples, columns for ASVs
indices is a dictionary mapping all tags ('UNTR', 'd10', etc) to a set of column indices in M corresponding to those samples
	If cols==True, return value is (columnIDs, {ID:(seq, tax, abund_vector)})
	
sample IDs look like:  ABX10_d3_GR_M_a22  yielding:   {treatment}_d{day}_{site}_{sex}_a{animal}
'''
	
if __name__ == "__main__":
	if len(sys.argv)!=5:
		print("Error - usage:\n >>> python Plot_Jitter.py [Rosetta.csv] [tax-level] [0/1 legend?] [Out_fname.png]\n")
		print("\tTop 5 most abundant of whatever a row means (ASV, species, etc) will be plotted by mouse,")
		print("\t\tdots colored by sex. Sites will be plotted side-by-side.\n")
		print("\t[tax-level]\t must be one of 'ASV/Genus/Species/V3V4' and must match [Rosetta.csv]'s summary level\n")
		exit()
	in_fname, tax_level, toLegend, out_fname = sys.argv[1:]
	tax_level = tax_level.upper()
	
	numTop = 5#000
	
	colors = {'LJ':'#F9564F', 'GR':'#3ABECF'}
	
	M, indices, sample_IDs, taxa_IDs = read_rosetta_indexed(in_fname, relative=False, taxonomy=True)  #Returns M with rows as samples, columns for taxa
	print(len(M),"samples,", len(M[0]), "taxa for tax-level:", tax_level)
	
	#taxa_IDs = [e if e!='Hungateiclostridium' else 'Hungatei-\nclostridium' for e in taxa_IDs]
	
	taxa_IDs = [text.replace("_","\n",1).replace("_"," ") for text in taxa_IDs]
	
	if tax_level == 'ASV':
		In = open(in_fname)
		temp = [row.split(",")[:9] for row in In.read().split("\n")[1:] if row!=""]
		In.close()
		#Need mapping from ASV ID to 'species + pct ID + 1st 8 of ASV hash':
		#seqID,pol_sequence,refID,matches,mismatches,gaps,PID,score,taxonomy
		mapper = {}
		for row in temp:
			row[0] = row[0].replace("_","\n",1).replace("_"," ")#.replace('Hungateiclostridium','Hungatei-\nclostridium')
			t = row[8].split(";")
			if len(t)>1:
				sp = t[6]
			else:
				sp = t[0]
			mapper[row[0]] = "#"+row[0][:8]+"\n"+sp.replace("_","\n",1).replace("_"," ")  #sp+"\n"+row[6]+"% #"+row[0][:8]
		taxa_IDs = [mapper[ID] for ID in taxa_IDs]
		del temp, mapper
	elif tax_level not in 'SPECIES GENUS'.split(): #= 'V3V4':
		In = open(in_fname)
		temp = [row.split(",")[:9] for row in In.read().split("\n")[1:] if row!=""]
		In.close()
		#Need mapping from V3V4 region to 'species + pct ID + 1st 8 of ASV hash':
		#seqID,pol_sequence,refID,matches,mismatches,gaps,PID,score,taxonomy
		mapper = {}
		for row in temp:
			row[0] = row[0].replace("_","\n",1).replace("_"," ")#.replace('Hungateiclostridium','Hungatei-\nclostridium')
			t = row[8].split(";")
			if len(t)>1:
				sp = t[6]
			else:
				sp = t[0]
			mapper[row[0]] = "#"+hash_sequence(row[0])[:8]
		taxa_IDs = [mapper[ID] for ID in taxa_IDs]
		del temp, mapper
	#else:
		
		
	
	
	taxa_indices = {taxa_IDs[i]:i for i in range(len(taxa_IDs))}
	
	M_baseline = [M[i] for i in indices['d-2']]   #just baseline
	print(len(taxa_IDs), 'taxa IDs total, filtering to top', numTop)
	sorted_abunds = sorted(zip(taxa_IDs, [sum(row) for row in list(zip(*M_baseline))]), key = lambda x:x[1], reverse=True)
	top10indices = [taxa_indices[r[0]] for r in sorted_abunds[:numTop]]
	top10names = [taxa_IDs[i] for i in top10indices]
	
	
	dat = []
	for j in range(len(M)):
		tempsum = sum(M[j])
		if tempsum == 0:  #some subregions may have zero-sum samples
			tempvec = [0 for _ in top10indices]
		else:
			tempvec = [M[j][i]/tempsum for i in top10indices]
		tmpIDs = sample_IDs[j].split("_")
		if len(tmpIDs)>1:
			group, day, site, sex = tmpIDs[:4]
			for i in range(len(tempvec)):
				name = top10names[i]
				
				rel_abund = tempvec[i]
				
				if day == 'd-2':
					dat.append([name, group, day, site, sex, rel_abund])
	
	df = pd.DataFrame(dat, columns = (tax_level+', group, day, Site, Sex, Relative Abundance').split(', '))
	#df['Relative Abundance'] = df['Relative Abundance']*100
	df[tax_level] = pd.Categorical(df[tax_level], categories=top10names, ordered=True)
	df = df.sort_values(tax_level)
	#print()
	
	print(in_fname, tax_level)
	#print("Name\tTest-Statistic\tp-value")
	p_vals = []
	for n in top10names:
		gr = list(df[(df[tax_level]==n) & (df['Site']=='GR')]['Relative Abundance'])
		lj = list(df[(df[tax_level]==n) & (df['Site']=='LJ')]['Relative Abundance'])
		stat,p_val = ranksums(gr, lj, alternative='two-sided')
		p_vals.append(p_val)
		#print(n, stat, p_val, sep='\t')
	
	
	
	
	significance = ["***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "" for p in p_vals]
	
	for i in range(len(top10names)):
		print(top10names[i], p_vals[i], significance[i])
	print()
	#OK now you have the top 10 taxa (over just baseline), normalized by sample sum (across all taxa)
	#
	
	fig, ax = plt.subplots(figsize=(12, 6))
	#plt.figure().set_figwidth(1)
	jitter_plot = sns.stripplot(data=df, x="Relative Abundance", y=tax_level, hue="Site", dodge=True, palette=colors, size=4) #y=tax_level
	
	
	#box_pairs = [("LJ", "GR")]
	#test_results = add_stat_annotation(
	#	ax, data=df, x='Site', y='Relative Abundance', hue='Site',
	#	box_pairs=box_pairs, # ) for n in top10names],
	#	test='Mann-Whitney', text_format='star', loc='outside', verbose=2,
	#	line_height=0.01, line_offset=0.02, line_offset_to_box=0.05,
	#	linewidth=1.5, fontsize='medium', use_fixed_offset=True
	#)
	
	
	jitter_plot.set_xlim(0,1)
	
	jitter_plot.legend_.remove()
	#sns.move_legend(jitter_plot, "upper left", bbox_to_anchor=(1, 1))
	jitter_plot.set_ylabel('')
			
	if toLegend == '1':
		jitter_plot.set_xlabel('Relative Abundance', fontsize = 24, fontweight='bold')
	else:
		jitter_plot.set_xlabel('')

	
	
	# Calculate the medians for each category and site
	medians = df.groupby([tax_level, 'Site'],observed=True)['Relative Abundance'].median()
	
	#print(medians)
	
	unit = 1/numTop  #space between taxa on y-axis
	strip = 0.04 #space between median marker strips for sites w/in each taxa
	height = 0.018  #half of median marker strip height
	
	posn = 1-unit/2
	
	max_val = df['Relative Abundance'].max()
	
	for i in range(len(top10names)):
		gr_median = medians.loc[(top10names[i], 'GR')]
		lj_median = medians.loc[(top10names[i], 'LJ')]
		gr_posn = posn + strip
		lj_posn = posn - strip
		jitter_plot.axvline(x=gr_median, ymin=gr_posn-height, ymax=gr_posn+height, color='black', linestyle='-', lw=2, zorder=3)
		jitter_plot.axvline(x=lj_median, ymin=lj_posn-height, ymax=lj_posn+height, color='black', linestyle='-', lw=2, zorder=3)
		
		if significance[i] != "":
			jitter_plot.axvline(x=0.95, ymin=lj_posn, ymax=gr_posn, color='black', linestyle='-', lw=2) #, transform=ax.transData)
			jitter_plot.text(y=i, x=0.98, s=significance[i], horizontalalignment='center', verticalalignment='center', fontsize=14, transform=ax.transData, rotation=90) #, weight='bold')
		
		posn -= unit
	
	#jitter_plot = boxplot(data=df, x="Relative Abundance", y=tax_level, hue="Site - Sex", dodge=True, palette=colors)
	#jitter_plot = swarmplot(data=df, x="Relative Abundance", y=tax_level, hue="Site - Sex", dodge=True, palette=colors, size=4)
	
	#jitter_plot = violinplot(data=df, x="Relative Abundance", y=tax_level, hue="Site - Sex", dodge=True, palette=colors) #, size=4)
	
	
	
	for label in jitter_plot.get_yticklabels():
		label.set_fontweight('bold')
		label.set_fontsize(18)
		text = label.get_text()
		# Replace the first underscore with a newline, and then replace remaining underscores with spaces
		text = text.replace("_", "\n", 1).replace("_", " ")
		label.set_text(text)
		
	for label in jitter_plot.get_xticklabels():
		label.set_fontweight('bold')
		label.set_fontsize(24)
	ax.xaxis.set_major_locator(ticker.MaxNLocator(3))
	ax.set_aspect(0.2)
	
	fig.tight_layout()
	if tax_level not in {'ASV', "V1V2","V1V3","V3V4","V4","V4V5","V6V8","V7V9","V1V9"}:
		plt.gca().tick_params(axis='x', which='both', bottom=True, labelbottom=False)
    
	
	fig.savefig(out_fname) 
	
	
	
# Add annotations


	
	
	
	
	
	
	
	
	#ros = pd.read_csv(in_fname)
	
	
	
	
	
	
