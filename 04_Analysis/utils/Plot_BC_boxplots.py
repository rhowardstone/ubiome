import matplotlib.pyplot as plt
from scipy.spatial.distance import braycurtis as BC
from utils import read_rosetta
import sys
# UNTR_d0_GR_M_a1

if __name__ == "__main__":
	if len(sys.argv)!=3:
		print("Error - usage:\n >>> python Plot_BC_boxplots.py [Rosetta.csv] [Out_basename]\n")
		print("\t\tFor all groups except UNTR, contemporary timepoints are compared between sites.\n\t\tFor UNTR, three modes of comparison are made within site.\n")
		exit()
	in_fname, out_bname = sys.argv[1:]
	
	#wilds = 'W1 W2'.split()
	groups = 'UNTR CMT ABX3CMT ABX10'.split()
	days = 'd-2 d1 d3 d5 d8 d10 d30 d60'.split()
	locs = 'GR LJ'.split()
	
	print("Loading, transposing, and normalizing abundance matrix by sample sums..")
	sample_labels, ros = read_rosetta(in_fname, cols=True)  #Load, transpose, and normalize abundance matrix by sample sums
	inverted = [] 								#rows are now samples, columns are ASVs
	for row in list(zip(*[ros[ID][2] for ID in ros])):
		tempsum = sum(row)
		inverted.append([row[i]/tempsum for i in range(len(row))])
	del ros
	
	ani_list = {G+"_"+L+"_"+D:[] for G in groups for L in locs for D in days}  #just for UNTR
	
	#index inverted rosetta:
	print("Indexing samples")
	indices = {} #{ele:[] for ele in groups+days+locs}
	for i in range(len(sample_labels)):
		if sample_labels[i] not in 'W1 W2'.split():  #EXCLUDE wildtype samples for now
			grp,day,loc,gen,ani = sample_labels[i].split("_")
			for ele in [grp,day,loc,gen,ani]:
				if ele in indices:
					indices[ele].append(i)
				else:
					indices[ele] = [i]
			ani_list[grp+"_"+loc+"_"+day].append(ani)
			
	for ele in indices:
		indices[ele] = set(indices[ele])
	
	print("Calculating BC and plotting")
	group = "UNTR"
		#if comparison_type == '0':
			#skip day 0, plot from 1:
	for loc in locs:
		IDs, vects = [], []
		for d in range(1,len(days)):
			temp = []
			for i in range(len(ani_list[group+"_"+loc+"_"+days[d]])):
				ani = ani_list[group+"_"+loc+"_"+days[d]][i]
				if ani in ani_list[group+"_"+loc+"_"+days[d-1]]:
					t0 = list(indices[loc].intersection(indices[group]).intersection(indices[days[d-1]]).intersection(indices[ani]))[0]
					t1 = list(indices[loc].intersection(indices[group]).intersection(indices[days[d]]).intersection(indices[ani]))[0]
					val = BC(inverted[t0], inverted[t1])
					temp.append(val)
			IDs.append(days[d])
			vects.append(temp)
		fig, ax = plt.subplots(1,1,figsize=(6.4*1.5,4.8*1.5))
		ax.boxplot(vects,labels=IDs)
		ax.set_ylim(0,1)
		fig.tight_layout()	
		plt.savefig(out_bname+'_BC_'+group+"_"+loc+'_consecutive.png')
	#if comparison_type == '1':
	#Plot from day 0, including day 0
	
	
	for loc in locs:
		IDs, vects = [], []
		for d in range(len(days)):
			t0 = indices[loc].intersection(indices[group]).intersection(indices[days[d]])  #e.g., LJ UNTR d0 's
			t1 = indices[loc].intersection(indices[group]).intersection(indices[days[d]])    #      LJ UNTR d1 's
			temp = []
			for i in t0:
				for j in t1:
					if i != j:
						val = BC(inverted[i],inverted[j])
						temp.append(val)
			IDs.append(days[d])
			vects.append(temp)
		fig, ax = plt.subplots(1,1,figsize=(6.4*1.5,4.8*1.5))
		ax.boxplot(vects,labels=IDs)
		ax.set_ylim(0,1)
		fig.tight_layout()	
		plt.savefig(out_bname+'_BC_'+group+"_"+loc+'_withinTimepoint.png')
	
	
	for loc in locs:
		IDs, vects = [], []
		for d in range(len(days)):
			t0 = indices[loc].intersection(indices[group]).intersection(indices[days[0]])  #e.g., LJ UNTR d0 's
			t1 = indices[loc].intersection(indices[group]).intersection(indices[days[d]])    #      LJ UNTR d1 's
			temp = []
			for i in t0:
				for j in t1:
					val = BC(inverted[i],inverted[j])
					temp.append(val)
			IDs.append(days[d])
			vects.append(temp)
		fig, ax = plt.subplots(1,1,figsize=(6.4*1.5,4.8*1.5))
		ax.boxplot(vects,labels=IDs)
		ax.set_ylim(0,1)
		fig.tight_layout()	
		plt.savefig(out_bname+'_BC_'+group+"_"+loc+'_beginning.png')
	#if comparison_type == '2':
	#Plot till the end, including the end
	
	for loc in locs:
		IDs, vects = [], []
		for d in range(len(days)):
			t0 = indices[loc].intersection(indices[group]).intersection(indices[days[-1]])  #e.g., LJ UNTR d0 's
			t1 = indices[loc].intersection(indices[group]).intersection(indices[days[d]])    #      LJ UNTR d1 's
			temp = []
			for i in t0:
				for j in t1:
					val = BC(inverted[i],inverted[j])
					temp.append(val)
			IDs.append(days[d])
			vects.append(temp)
		fig, ax = plt.subplots(1,1,figsize=(6.4*1.5,4.8*1.5))
		ax.boxplot(vects,labels=IDs)
		ax.set_ylim(0,1)
		fig.tight_layout()	
		plt.savefig(out_bname+'_BC_'+group+"_"+loc+'_end.png')
	
	#Now the other groups:
	for group in 'ABX3FMT ABX10 FMT UNTR'.split():
		IDs, vects = [], []
		for d in range(len(days)):
			t0 = indices['GR'].intersection(indices[group]).intersection(indices[days[d]])  #e.g., LJ UNTR d0 's
			t1 = indices['LJ'].intersection(indices[group]).intersection(indices[days[d]])    #      LJ UNTR d1 's
			temp = []
			for i in t0:
				for j in t1:
					val = BC(inverted[i],inverted[j])
					temp.append(val)
			IDs.append(days[d])
			vects.append(temp)
		fig, ax = plt.subplots(1,1,figsize=(6.4*1.5,4.8*1.5))
		ax.boxplot(vects,labels=IDs)
		ax.set_ylim(0,1)
		fig.tight_layout()	
		plt.savefig(out_bname+'_BC_'+group+'.png')
					


