from matplotlib import pyplot as plt

#from venn import venn
from matplotlib_venn import venn2

from utils import read_rosetta
import sys
# UNTR_d0_GR_M_a1

if __name__ == "__main__":
	if len(sys.argv)!=3:
		print("Error - usage:\n >>> python Plot_venn_diagrams.py [Rosetta.csv] [Out_fname]\n")
		exit()
	in_fname, out_fname = sys.argv[1:]
	
	#wilds = 'W1 W2'.split()
	groups = 'UNTR CMT ABX3CMT ABX10'.split()
	days = 'd-2 d1 d3 d5 d8 d10 d30 d60'.split()
	locs = 'LJ GR'.split()
	
	print("Loading, transposing, and normalizing abundance matrix by sample sums..")
	sample_labels, ros = read_rosetta(in_fname, cols=True)  #Load, transpose, and normalize abundance matrix by sample sums
	ASV_IDs = [ID for ID in ros]
	inverted = [] 								#rows are now samples, columns are ASVs
	for row in list(zip(*[ros[ID][2] for ID in ASV_IDs])):
		tempsum = sum(row)
		inverted.append([row[i]/tempsum for i in range(len(row))])
	del ros

	#index inverted rosetta:
	print("Indexing samples")
	indices = {ele:[] for ele in groups+days+locs}
	for i in range(len(sample_labels)):
		if sample_labels[i] not in 'W1 W2'.split():  #EXCLUDE wildtype samples for now
			grp,day,loc = sample_labels[i].split("_")[:3]
			for ele in [grp,day,loc]:
				indices[ele].append(i)
	for ele in indices:
		indices[ele] = set(indices[ele])
	
	print("Calculating and plotting")
	
	data_dict = {"UNTR_"+j:[] for j in locs}
	for loc in locs:
		inds = indices[loc].intersection(indices['d0'])
		for ind in inds:
			for ele in [ASV_IDs[i] for i in range(len(ASV_IDs)) if inverted[ind][i]!=0]:
				data_dict["UNTR_"+loc].append(ele)
	
		data_dict["UNTR_"+loc] = set(data_dict["UNTR_"+loc])
		
	V = venn2([data_dict["UNTR_"+loc] for loc in locs], set_labels=["", ""], set_colors=('#F9564F','#3ABECF')) #, fontsize=16) # for loc in locs])
	
	for text in V.subset_labels:
		text.set_fontsize(18)
	
	#plt.legend(loc='center right')
	plt.tight_layout()
	plt.savefig(out_fname)
	
	

