import sys
from utils import read_rosetta
#FMT_d60_LJ_F_a80
def calculate_alpha_divs(input_file, output_file):
	sample_labels, ros = read_rosetta(input_file, cols=True)  # Load, transpose, and normalize abundance matrix by sample sums
	
	IDs = [ID for ID in ros]
	inverted = list(zip(*[ros[ID][2] for ID in IDs])) # rows are now samples, columns are ASVs
	
	
	W_inds = {}
	for i in range(len(inverted)):
		if sample_labels[i] in 'W1 W2'.split():
			W_inds[sample_labels[i]] = set([j for j in range(len(inverted[i])) if inverted[i][j]!=0])
	W_inds = W_inds['W1'].union(W_inds['W2'])
	
	Out = open('data/Filt_Donor_ASVs.txt', 'w+')
	Out.write("\n".join([IDs[i] for i in W_inds])+"\n")
	Out.close()
	
	Out = open(output_file, 'w+')
	#Out.write('Group\tDay\tBray-Curtis\n')
	for i in range(len(inverted)):
		if sample_labels[i] not in 'W1 W2'.split():
			grp, day, loc = sample_labels[i].split("_")[:3]
			wild_count = sum([1 if inverted[i][j]!=0 else 0 for j in W_inds])
			totl_count = sum([1 if inverted[i][j]!=0 else 0 for j in range(len(inverted[i]))])
			Out.write("\t".join([grp, day[1:], loc, str(wild_count/totl_count)])+"\n")
	Out.close()

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("Error - usage:\n >>> python Calculate_pct_wildtype.py [Rosetta.csv] [Output_file.tsv]\n")
		print("\tCounts number of ASVs present (non-zero entries). Can be used to count species or genera as well,\n\t\t as long as rows are properly condensed.\n")
		sys.exit()

	in_fname, out_fname = sys.argv[1:]
	calculate_alpha_divs(in_fname, out_fname)

