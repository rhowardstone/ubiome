import sys
import seaborn as sns
import pandas as pd
from utils import read_rosetta_indexed#(fname):
from scipy.stats import ranksums
import matplotlib.pyplot as plt



if __name__ == "__main__":
	if len(sys.argv)!=5:
		print("Error - usage:\n >>> python Plot_Jitter_temporal.py [Rosetta.csv] [Treatment-code] [ID_to_plot] [Out_fname.png]\n")
		print("\t[treatment-code]\tcan be one of: UNTR, CMT, ABX3CMT, or ABX10.\n")
		exit()
	in_fname, treatment, tax_to_plot, out_fname = sys.argv[1:]
	tax_to_plot = tax_to_plot.replace("_", " ")
	
	colors = {'LJ':'#F9564F', 'GR':'#3ABECF'}  
	days = [int(i) for i in '-2 1 3 5 8 10 30 60'.split()]
	
	M, indices, sample_IDs, taxa_IDs = read_rosetta_indexed(in_fname, relative=False, taxonomy=True)  #Returns M with rows as samples, columns for taxa
	print(len(M),"samples,", len(M[0]), "taxa")
	
	taxa_IDs = [t.replace("_"," ") for t in taxa_IDs]
	indices_to_plot = [i for i in range(len(taxa_IDs)) if taxa_IDs[i]==tax_to_plot]
	
	dat = []
	for j in range(len(M)):
		tempsum = sum(M[j])
		tempvec = [M[j][i]/tempsum for i in range(len(M[j]))]
		tmpIDs = sample_IDs[j].split("_")
		if len(tmpIDs)>1:
			group, day, site, sex = tmpIDs[:4]
			if group == treatment:
				for i in indices_to_plot:
					rel_abund = tempvec[i]
					dat.append([tax_to_plot, group, int(day[1:]), site, sex, rel_abund])
		
	df = pd.DataFrame(dat, columns = ('name, group, Day, Site, sex, Relative Abundance').split(', '))
	
	#df = df[(df['name'] == tax_to_plot) & (df['group'] == 'UNTR')]  #should no longer be neccessary with th
	
	newOrder = 'LJ GR'.split()
	df['Site'] = pd.Categorical(df['Site'], categories=newOrder, ordered=True)
	df = df.sort_values('Site')
	
	print(in_fname, tax_to_plot, treatment)
	#print("Day\tTest-Statistic\tp-value")
	significance = []
	for d in days:
		gr = list(df[(df['Day']==d) & (df['Site']=='GR')]['Relative Abundance'])
		lj = list(df[(df['Day']==d) & (df['Site']=='LJ')]['Relative Abundance'])
		stat,p_val = ranksums(gr, lj, alternative='two-sided')
		significance.append(p_val)
		print(d, stat, p_val, sep='\t')
	
	significance = ["***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "" for p in significance]
	
	fig, ax = plt.subplots()
	jitter_plot = sns.stripplot(data=df, y="Relative Abundance", x='Day', hue="Site", dodge=True, palette=colors, size=4)	
	jitter_plot.legend_.remove()
	
	medians = df.groupby(['Day', 'Site'],observed=True)['Relative Abundance'].median()
	#print(medians)
	
	unit = 1/len(days)  #space between taxa on y-axis
	strip = 0.025 #space between median marker strips for sites w/in each taxa
	height = 0.014  #half of median marker strip length
	
	posn = 0 + unit/2
	
	max_val = df['Relative Abundance'].max()
	if max_val == None:
		print("Hmm why was it none?:")
		print(max(df['Relative Abundance'])) #error?
		max_val = 0
	else:
		print("but it was not infinite, right..?", max_val)
		print()
		print(df['Relative Abundance'])
		print()
		
	scale = max_val - df['Relative Abundance'].min()
	plt.ylim([0,max_val+0.06])
	
	for i in range(len(days)):
		gr_median = medians.loc[(days[i], 'GR')]
		lj_median = medians.loc[(days[i], 'LJ')]
		gr_posn = posn + strip
		lj_posn = posn - strip
		jitter_plot.axhline(y=gr_median, xmin=gr_posn-height, xmax=gr_posn+height, color='black', linestyle='-', lw=2, zorder=3)
		jitter_plot.axhline(y=lj_median, xmin=lj_posn-height, xmax=lj_posn+height, color='black', linestyle='-', lw=2, zorder=3)
		
		if significance[i] != "":
			jitter_plot.axhline(y=max_val+0.02*scale, xmin=lj_posn, xmax=gr_posn, color='black', linestyle='-', lw=1.5) #, transform=ax.transData)
			jitter_plot.text(x=i, y=max_val+0.05*scale, s=significance[i], horizontalalignment='center', verticalalignment='top', fontsize=12, transform=ax.transData) #, weight='bold')
		
		posn += unit
	
	ax.set_ylabel("Relative Abundance", fontsize=20, fontweight='bold')
	plt.yticks(fontsize=20, fontweight='bold')
	plt.xticks(fontsize=20, fontweight='bold')
	plt.xlabel(xlabel='Day', fontsize=20, fontweight='bold')
	ax.set_title(tax_to_plot, fontsize=20, fontweight='bold')
	#sns.move_legend(jitter_plot, "upper left", bbox_to_anchor=(1, 1))
	#fig = jitter_plot.get_figure()
	fig.tight_layout()
	fig.savefig(out_fname) 
	print()
	
	# Calculate overall stats pooled across all days for each site
	overall_stats = df.groupby('Site', observed=True)['Relative Abundance'].agg(['mean', 'std']).reset_index()

	print("\nOverall statistics (pooled across all days):")
	print("Site\tMean\tStd Dev")
	print("-" * 30)
	for _, row in overall_stats.iterrows():
		print(f"{row['Site']}\t{row['mean']:.4f}\t{row['std']:.4f}")
	print()
		
	
	
	
	
	
