''' read_rosetta_indexed     Returns     (M, indices, cols)    where:
M is a matrix with rows as samples, columns for ASVs
indices is a dictionary mapping all tags ('UNTR', 'd10', etc) to a set of row indices in M corresponding to those samples
cols is a list of column (sample) IDs
	If cols==True, return value is (columnIDs, {ID:(seq, tax, abund_vector)})
'''
# UNTR_d0_GR_M_a1  is format of sample ID

import sys
from PyPerMANOVA import permutational_analysis
from utils import read_rosetta_indexed
import pandas as pd
from multiprocessing import Pool, cpu_count

def run_permanova(args):
	target_day, target_group, target_site = args
	#Load matrix of relative abundances
	global M, indices, sample_labels
	temp, mapping = [], []
	for i in range(len(M)):
		if sample_labels[i][0] != 'W':	# Exclude wildtype
			group, day, site, sex, animal = sample_labels[i].split("_")
			if site == target_site and day == target_day and (group==target_group or target_group=='-1'):		# Just baseline
				temp.append(M[i])
				mapping.append(sex)
	M = pd.DataFrame(data=list(zip(*temp)))
	
	#print(len(M), len(mapping))
	result = permutational_analysis(M, mapping, norm='None', metric='braycurtis', permutations=10000)
	
	res = [result[0][X].iloc[0] for X in 'Pval eta-sqr F'.split()] + [result[1][X].iloc[0] for X in 'A B Pval bonf eta-sqr F t'.split()]
	res = "\t".join([str(e) for e in res])
	
	return "\t".join([target_day,target_group,target_site, res])
		


if __name__ == "__main__":
	if len(sys.argv)!=4:
		print("Error - usage:\n >>> python3 Run_permanova_sex.py [Rosetta.csv] [n-threads(-1 for all)] [Out.tsv]\n")
		print("\tRuns permanova on all samples (day 0) using sex as the factor\n")
		print("\t\tColumns are: Pval eta-sqr F A B Pval bonf eta-sqr F t")
		print("\t(where all but the first three (Pval eta-sqr F) refer to the posthoc result)\n")
		exit()
	in_fname, nthreads, out_fname = sys.argv[1:]
	if nthreads == '-1':
		nthreads = cpu_count()-1
	else:
		nthreads = int(nthreads)
	global M, indices, sample_labels
	M, indices, sample_labels = read_rosetta_indexed(in_fname, relative=True)
	dataset = []
	for d in 'd-2 d1 d3 d5 d8 d10 d30 d60'.split():
		for g in '-1 UNTR ABX10 ABX3CMT CMT'.split():
			for s in 'LJ GR'.split():
				dataset.append([d, g, s])
				#run_permanova(in_fname, d, g, s)
	print(f'Multiprocessing on {nthreads} threads.')
	with Pool(processes=nthreads) as pool:
		result = pool.map(run_permanova, dataset)
	Out = open(out_fname, 'w+')
	Out.write('Day Group Site Pval eta-sqr F A B Pval bonf eta-sqr F t'.replace(' ','\t')+'\n')
	Out.write('\n'.join(result)+'\n')
	print(f'Output written to {out_fname}.\n')
	
