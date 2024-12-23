import sys
from utils import read_rosetta_indexed
#FMT_d60_LJ_F_a80
def calculate(input_file, output_file):
	M, indices, sample_labels, ASV_IDs = read_rosetta_indexed(input_file, taxonomy=True)
	
	Out = open(output_file, 'w+')
	#Out.write('ASV\tnReads\tnSamples\n')
	for i in range(len(M)):
		nReads = str(sum(M[i]))
		Out.write("\t".join([sample_labels[i], nReads])+"\n")
	Out.close()

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("Error - usage:\n >>> python Calculate_nReads_perSample.py [Rosetta.csv] [Output_file.tsv]\n")
		print("\tCounts number of reads and samples detected per ASVs.\n")
		sys.exit()

	in_fname, out_fname = sys.argv[1:]
	calculate(in_fname, out_fname)

