import sys
from utils import read_rosetta
import matplotlib.pyplot as plt
import hashlib
from matplotlib import colors as mplcolors
from random import shuffle

if __name__ == "__main__":
	if len(sys.argv)!=10:
		print("Error - usage:\n >>> python3 Plot_stacked_barplot.py [Rosetta.csv] [tax-index] [Top-N] [Plot-title] [taxa-order.txt] [0/1 Wild] [0/1 separate locs] [0/1 legend?] [Out.png]\n")
		print("\teach column in rosetta will constitute one subplot - may want to run Condense_rosetta_columns.py first.")
		print("\t[Top-N]\tInclude the top N most abundant (by whatever metric is included in column 3 of [taxa-order.txt]\n")
		exit()
	ros_fname, index, topN, title, order_fname, isWild, isSep, toLegend, out_fname = sys.argv[1:]
	index, topN = int(index), int(topN)
	
	
	tab20 = [mplcolors.rgb2hex(row) for row in plt.get_cmap('tab20',20).colors]
	#shuffle(tab20)
	
	In = open(order_fname)
	temp = [row.split(",") for row in In.read().split("\n") if row!=""]
	In.close()
	order = [r[0] for r in sorted(temp, key=lambda x:float(x[2]))][::-1][:topN]
	#print(order)
	order = {order[i]:i for i in range(len(order))}
	order['Other'] = -1
	
	vectors = {}  #Opens rosetta, summing up vectors by identical entries in in the (index + 1)^th position of the ';'-separated taxonomy. Entries with incomplete taxonomic assigments are ignored.
	In = open(ros_fname)
	if isSep == '1':
		Columns = [ele.split("_")[1] for ele in In.readline()[:-1].split(",")[9:]]    # UNTR_d0_GR -> d0
	elif isWild == '0':
		Columns = ["_".join(ele.split("_")[1:]) for ele in In.readline()[:-1].split(",")[9:]]    # UNTR_d0_GR -> d0_GR
	else:
		Columns = [ele for ele in In.readline()[:-1].split(",")[9:]]
	totals = [0 for _ in range(len(Columns))]
	line = In.readline()
	while line != "":
		temp = line[:-1].split(",")
		abunds = [int(ele) for ele in temp[9:]]
		for i in range(len(Columns)):
			totals[i] += abunds[i]
		tax = temp[8].split(";")
		if len(tax)>index:
			tax = tax[index]
		else:
			tax = ";".join(tax)
		if tax in vectors:
			for i in range(len(Columns)):
				vectors[tax][i] += abunds[i]
		else:
			vectors[tax] = abunds
		line = In.readline()
	In.close()
	
	temp_vectors = {}
	temp_vectors['Other'] = [0 for _ in range(len(Columns))]
	total = sum(totals)
	
	for tax in vectors:
		if tax not in order:
			for i in range(len(Columns)):
				temp_vectors['Other'][i] += vectors[tax][i]
		else:
			temp_vectors[tax] = vectors[tax]
	vectors = temp_vectors
	
	for tax in vectors:  #Normalize by sample sum
		for i in range(len(Columns)):
			vectors[tax][i] /= totals[i]
	
	tax_order = [ele for ele in sorted(vectors, key=lambda x:order[x])]
	
	
	#print("\nThere are", len(order), "taxa >=", prop, "of global abundance.", len(tax_order), "appear in: ("+out_fname+")\n")
	
	fig, ax = plt.subplots()
	fig.set_size_inches(16,12)
	
	Columns = [c.replace("_LJ","  ").replace("_GR"," ")[1:] for c in Columns]
	#print(Columns)
	
	x_posns = [i for i in range(1,9)] + [i-0.5 for i in range(10,18)]
	#ax.autoscale(enable=True)
	labels = []
	totals_so_far = [0 for _ in range(len(Columns))]
	for tax in tax_order:
		#if tax != "Other":
		#col = "#"+hashlib.sha256(tax.encode('utf-8')).hexdigest()[6:12]
		col = tab20[order[tax]] #will fail when >20 taxa
		if tax == 'Other':
			col = "#5A5A5A"
		labels.append(tax.replace('_',' '))
		if isSep == '1' or isWild == '1':
			ax.bar(Columns, vectors[tax], 0.85, bottom=totals_so_far, label=tax, color=col)
		else:
			ax.bar(x_posns, vectors[tax], 0.85, bottom=totals_so_far, label=tax, color=col, tick_label=Columns)
		for i in range(len(Columns)):
			totals_so_far[i] += vectors[tax][i]
	
	#For middle line:
	#ax.axvline(x = len(Columns)/2-0.5, color = 'b')
	
	
	#fig.subplots_adjust(left=1, bottom=6, right=16, top=8)
	#
	
	#ax.bar(Columns, vectors["Other"], 0.7, bottom=totals_so_far, label="Other")
	#for i in range(len(Columns)):
	#	totals_so_far[i] += vectors['Other'][i]
	#labels.append('Other')
	
	
	
	if isSep == '1' or isWild == '1':
		ax.tick_params(axis='x', labelrotation=0, labelsize=22)
	else:
		ax.tick_params(axis='x', labelrotation=0, labelsize=22)  #was 90
		tmp_lbls = plt.gca().get_xticklabels()
		tmp_cols = 'red blue'.split()
		for i in range(len(tmp_lbls)//2):
			tmp_lbls[i].set_color(tmp_cols[0])
		for i in range(len(tmp_lbls)//2, len(tmp_lbls)):
			tmp_lbls[i].set_color(tmp_cols[1])
		ax.annotate('', xy=(0.025, -0.06), xycoords='axes fraction', xytext=(0.49, -0.06), arrowprops=dict(arrowstyle="<-", color=tmp_cols[0], lw=2))
		ax.annotate('', xy=(0.51, -0.06), xycoords='axes fraction', xytext=(0.975, -0.06), arrowprops=dict(arrowstyle="->", color=tmp_cols[1], lw=2))
		ax.annotate('La Jolla', xy=(0.25,-0.11), xycoords='axes fraction', color=tmp_cols[0], fontsize=28, fontweight='bold')
		ax.annotate('Groton', xy=(0.7,-0.11), xycoords='axes fraction', color=tmp_cols[1], fontsize=28, fontweight='bold')
	
	#tmp_lbls = plt.gca().get_xticklabels()
	#for lbl in tmp_lbls:
	#	lbl.set_text(lbl.get_text()[1:])
	#print(tmp_lbls)
	
	#ugly bandaid for specific case - fix later:
	#-AS_sorted_$n\.csv
	GROUP = ros_fname.split("_")[-1].split(".")[0]
	
	
	ax.set_ylabel("Relative ASV Richness", fontsize=28, fontweight='bold')
	plt.yticks(fontsize=28, fontweight='bold')
	#ax.set_ylabel("")
	plt.xticks(fontsize=30, fontweight='bold')
	ax.set_ylim((0,1))
	ax.set_title(title, fontsize=48, fontweight='bold')
	plt.autoscale(enable=True, axis='x', tight=True)
	#ax.legend(reversed(ax.legend().legend_handles), reversed(labels), loc='center left', bbox_to_anchor=(1,0.5), fontsize=14)  #outside, to right
	if toLegend == '1':
		legend = ax.legend(reversed(ax.legend().legend_handles), reversed(labels), fontsize=14, loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=3)  #outside below centered
		legend.get_title().set_fontweight('bold')
		plt.setp(legend.get_texts(), fontweight='bold')
	#ax.legend(loc='center left', bbox_to_anchor=(1,0.5), fontsize=8)
	for spine in ax.spines.values():
    		spine.set_linewidth(2)
	fig.tight_layout()
	if GROUP.find('ABX')!=-1:
		ax.set_yticks([])
		ax.set_ylabel("")
	
	plt.savefig(out_fname)
	
	
