from matplotlib import pyplot as plt
from utils import read_rosetta_indexed
import sys
import os
''' read_rosetta_indexed     Returns     (M, indices, cols)    where:
M is a matrix with rows as samples, columns for ASVs
indices is a dictionary mapping all tags ('UNTR', 'd10', etc) to a set of row indices in M corresponding to those samples
cols is a list of column (sample) IDs
	If cols==True, return value is (columnIDs, {ID:(seq, tax, abund_vector)})
'''
# UNTR_d0_GR_M_a1  is format of sample ID

if __name__ == "__main__":
	if len(sys.argv)!=3:
		print("Error - usage:\n >>> python Plot_venn_baseline.py [Rosetta.csv] [Out_basename]\n")
		exit()
	in_fname, out_fname = sys.argv[1:]
	
	#wilds = 'W1 W2'.split()
	#groups = 'UNTR FMT ABX3FMT ABX10'.split()
	#days = 'd0 d1 d3 d5 d8 d10 d30 d60'.split()
	#locs = 'LJ GR'.split()
	
	M, indices, sample_labels, ASV_IDs = read_rosetta_indexed(in_fname, relative=False, taxonomy=True)
	
	M = list(zip(*M)) #invert so rows are taxa, columns are samples. 
	
	LJ_indices = indices['d-2'].intersection(indices['LJ'])
	GR_indices = indices['d-2'].intersection(indices['GR'])  #these are now column indices in M!
	
	#Now need to assemble a list of taxa present in only one or the other, along with the reads that represents and intersection values
	LJ_taxa, LJ_abund = 0, 0
	In_taxa, In_abund = 0, 0
	GR_taxa, GR_abund = 0, 0
	
	for i in range(len(M)):  #for each taxa,
		LJ_tot = sum([M[i][j] for j in LJ_indices])
		GR_tot = sum([M[i][j] for j in GR_indices])
		if LJ_tot != 0 and GR_tot == 0:
			LJ_taxa += 1
			LJ_abund += LJ_tot
		elif LJ_tot != 0 and GR_tot != 0:
			In_taxa += 1
			In_abund += GR_tot + LJ_tot
		elif LJ_tot == 0 and GR_tot != 0:
			GR_taxa += 1
			GR_abund += GR_tot
	
	#Super lazy but will work:
	os.system("python3 utils/Plot_venn_rectangles.py "+out_fname+"_taxa.png "+" ".join([str(ele) for ele in (LJ_taxa, In_taxa, GR_taxa)])+" 0 5 2 28")
	os.system("python3 utils/Plot_venn_rectangles.py "+out_fname+"_abund.png "+" ".join([str(ele) for ele in (LJ_abund, In_abund, GR_abund)])+" 1 5 2 28") # '#fdbbb9' '#e789e7' '#b0e5ec'".upper())
	#convert test.png -trim -bordercolor White -border 5x5 test-trimmed.png

	#os.system("convert -trim -bordercolor White -border 4x4 taxa.png taxa.png")
	#os.system("convert -trim -bordercolor White -border 4x4 abund.png abund.png")
	
	#os.system("python3 utils/Combine_images.py "+out_fname+" 1 taxa.png abund.png")
	
	#os.system("convert -trim -bordercolor White -border 5x10 "+out_fname+" "+out_fname)
	
	#os.system("rm taxa.png abund.png")
	
	
	
