from utils import read_rosetta_indexed
from numpy import percentile
import sys


if __name__ == "__main__":
	if len(sys.argv)!=4:
		print("Error - usage:\n >>> python3 Report_outlier_samples.py [Rosetta.csv] [N-reads min] [Out.txt]\n")
		print("")
		exit()
	in_fname, N, out_fname = sys.argv[1:]
	N = int(N)
	
	
	M, indices, sample_labels = read_rosetta_indexed(in_fname)
	Out = open(out_fname, 'w+')
	for i in indices['UNTR'].union(indices['FMT']):
		tot = sum(M[i])
		if tot < N:
			Out.write(sample_labels[i]+"\n")
	Out.close()
	
	
	#groups, days, locs = 'UNTR FMT ABX3FMT ABX10'.split(), 'd0 d1 d3 d5 d8 d10 d30 d60'.split(), 'GR LJ'.split()
	#for g in groups: #['UNTR', 'FMT']: #groups:
	#	for l in locs:
	#		for d in days:
	#			relevant_indices = list(indices[g].intersection(indices[l]).intersection(indices[d]))
	#			
	#			abundances = [sum(M[i]) for i in relevant_indices]
	#			q1, q3 = percentile(abundances, [25, 75])
	#			IQR = (q3-q1)
	#			upper = q3 + 1.4*IQR
	#			lower = q1 - 1.4*IQR
	#			#print(g, l, d, len(abundances)) #, q1, q3, IQR)			
	#			for i in range(len(abundances)):
	#				
	#				if abundances[i] < q1:
	#					score = (abundances[i] - q1)/IQR
	#				elif abundances[i] > q3:
	#					score = (abundances[i] - q3)/IQR
	#				if abundances[i] < lower:# or sample_labels[relevant_indices[i]] == 'FMT_d10_LJ_M_a65': #abundances[i] > upper or 
	#					print(sample_labels[relevant_indices[i]]+'  \t'+str(abundances[i])+'\t'+str(score))
	#					Out.write(sample_labels[relevant_indices[i]]+'\t'+str(abundances[i])+'\t'+str(score)+'\n')
	#Out.close()
	#
	#Out = open(out_fname, 'w+')
	#Out.write("UNTR_d3_LJ_M_a9\nUNTR_d60_LJ_M_a9\nFMT_d10_LJ_M_a65\n")
	#Out.close()
