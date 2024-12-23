import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import sys



def export_legend(legend, filename="legend.png"):
	fig  = legend.figure
	fig.canvas.draw()
	bbox  = legend.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
	fig.savefig(filename, dpi="figure", bbox_inches=bbox)

if __name__ == "__main__":
	if len(sys.argv)!=7:
		print("Error - usage:\n >>> python3 Plot_linegraphs.py [In.rosetta-AS] [ASVs.txt] [0/1 yLogScale] [Title] [exclude#] [Out.png]\n")
		print("\t[In.rosetta-AS]\tMUST BE CONDENSED BY ANIMAL+SEX FIRST")
		print("\t[ASVs.txt]\tEnter '-1' to use all ASVs in Rosetta file")
		print("\t[exclude#]\Will exclude the top X most abundant ASVs from plotting\n")
		print("\t NOTE: will normalize by sample sum - do not subset ASVs first\n")
		exit()
	in_fname, asvs_fname, yLogScale, title, exclude, out_fname = sys.argv[1:] 
	yLogScale = yLogScale=='1'
	exclude = int(exclude)

	T = "UNTR FMT ABX3FMT ABX10".split()
	L = "LJ GR".split()

	#ASV_label_index = 6   #label legend by ASV taxonomy  // work on this later.. some kinda mouseover thing is ideal


	cols = L
	rows = T

	#in_fname = '/data/shoreline/ABX_resistance/R30_A10_S2_D1_R1000_ABS-AS.csv'
	In = open(in_fname)
	temp = [row.split(",") for row in In.read().split("\n") if row!=""]
	In.close()

	Headers = temp[0][9:]   #

	ASVs = [row[0] for row in temp[1:]]
	Counts = [row[9:] for row in temp[1:]]
	taxs = [row[8].split(";") for row in temp[1:]] #.split(";")


	if asvs_fname != '-1':
		In = open(asvs_fname)
		abr_asvs = set([row for row in In.read().split("\n") if row!=""])
		In.close()
	else:
		abr_asvs = set(ASVs)

	
	abr_asv_indices = [i for i in range(len(ASVs)) if ASVs[i] in abr_asvs]
	abr_asv_totals = [sum([int(ele) for ele in Counts[i]]) for i in abr_asv_indices]
	
	#print(list(zip(*sorted(zip(abr_asv_indices,abr_asv_totals), key = lambda x:x[1], reverse=True))))
	
	
	abr_indices_to_exclude = set(list(zip(*sorted(zip(abr_asv_indices,abr_asv_totals), key = lambda x:x[1], reverse=True)))[0][:exclude])
	
	#print("CHECK:", len(abr_asvs), "=", len(abr_asv_indices), "asvs", "("+asvs_fname+")")

	totals = [0 for _ in range(len(Headers))]
	for row in Counts:
		for i in range(len(Headers)):
			totals[i] += int(row[i])
	
	x, y = 0, 0
	fig, axes = plt.subplots(nrows=4, ncols=2, figsize=(32, 20), sharex=True, sharey=True)
	#delta = 0 #1e-5

	for t in T:  #absurdly inefficient :/
		for l in L:
			for i in abr_asv_indices: #range(len(Counts)):
				if i not in abr_indices_to_exclude:
					if 1 == 1: #taxs[i][-3] != "NOTATHING": #== 'Lactobacillus':
						X, Y = [], []
						for j in range(len(Headers)):
							temp = Headers[j].split("_")
							if temp[0] == t and temp[2] == l:
								X.append(temp[1])
								val = int(Counts[i][j]) / totals[j]
								Y.append(val)
						axes[y,x].plot(X, Y, label=i) # #ASVs[i])

			
			x += 1
			if x==2:
				y += 1
				x = 0
			
	#for row in axes:
	#	for ax in row:
	#		ax.set_yscale('log')


	#plt.setp(axes.flat, xlabel='Day', ylabel='Fraction of Sample') #, size=24)

	pad = 5 # in points

	for ax, col in zip(axes[0], cols):
	    ax.annotate(col, xy=(0.5, 1), xytext=(0, pad),
		        xycoords='axes fraction', textcoords='offset points',
		        size=36, ha='center', va='baseline')

	for ax, row in zip(axes[:,0], rows):
	    ax.annotate(row, xy=(0, 0.5), xytext=(-ax.yaxis.labelpad - pad, 0),
		        xycoords=ax.yaxis.label, textcoords='offset points',
		        size=32, ha='right', va='center')
	    #ax.set_ylabel(


	for ax in axes[-1,:]:  #last row, both columns (this is the bottom - want days)
		ax.set_xlabel(xlabel='Day', fontsize=24)
	for ax in axes[:,0]: #First column, both rows  (this is the left - want frac of samp)
		ax.set_ylabel(ylabel='Fraction of Sample', fontsize=24)

	if yLogScale:
		plt.yscale('log')
	#plt.xscale('log')


	#plt.legend()



	handles, labels = plt.gca().get_legend_handles_labels()

	#specify order of items in legend
	#order = 
	temp, order = zip(*sorted(zip(labels,[i for i in range(len(labels))]), key = lambda x:sum([int(ele) for ele in Counts[int(x[0])]]), reverse=True))
	#order = [1,2,0]

	order = order[:20] #max 20 on plot

	#add legend to plot
	#axes[0,1].legend([handles[idx] for idx in order],[taxs[int(labels[idx])][-1] for idx in order], bbox_to_anchor=(1.3, 1.0), loc='upper right') #, fontsize=14) #1.4 for long legend
	#

	fig.suptitle(title+" ("+str(len(abr_asvs))+" ASVs)", fontsize = 50)  #out_fname.replace("_"," ").split("/")[-1].split(".")[0]
	
	#plt.xticks(fontsize=24)
	for ax in axes[-1,:]:
		ax.tick_params(axis='x', labelsize=20)
	for ax in axes[:,0]:
		ax.tick_params(axis='y', labelsize=20)

	#plt.tick_params(axis='x', labelsize=20)
	
	
	legend = fig.legend([handles[idx] for idx in order],[taxs[int(labels[idx])][-1] for idx in order], fontsize=10, loc='upper right', bbox_to_anchor=(1.3, 1.0)) #
	export_legend(legend, filename = ".".join(out_fname.split(".")[:-1])+"_legend.png")

	#print(labels)
	#print(order)
	#print([taxs[int(labels[idx])][-1] for idx in order])
	
	fig.tight_layout()
	# tight_layout doesn't take these labels into account. We'll need 
	# to make some room. These numbers are are manually tweaked. 
	# You could automatically calculate them, but it's a pain.
	#fig.subplots_adjust(left=0.15, top=0.95)


	
	plt.savefig(out_fname)







