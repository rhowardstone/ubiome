import sys
from utils import read_rosetta
#FMT_d60_LJ_F_a80
def calculate_alpha_divs(input_file, output_file):
	sample_labels, ros = read_rosetta(input_file, cols=True)  # Load, transpose, and normalize abundance matrix by sample sums
	inverted = list(zip(*[ros[ID][2] for ID in ros])) # rows are now samples, columns are ASVs
	
	Out = open(output_file, 'w+')
	#Out.write('Group\tDay\tBray-Curtis\n')
	for i in range(len(inverted)):
		if sample_labels[i] not in 'W1 W2'.split():
			grp, day, loc = sample_labels[i].split("_")[:3]
			Out.write("\t".join([grp, day[1:], loc, str(sum(inverted[i]))])+"\n")
	Out.close()

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("Error - usage:\n >>> python calculate_nReads.py [Rosetta.csv] [Output_file.tsv]\n")
		print("\tCounts number of reads detected per sample.\n")
		sys.exit()

	in_fname, out_fname = sys.argv[1:]
	calculate_alpha_divs(in_fname, out_fname)

