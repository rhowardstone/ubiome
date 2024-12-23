import sys
from utils import read_rosetta_indexed

if __name__ == "__main__":
	if len(sys.argv)!=3:
		print("Error - usage:\n >>> python3 Get_ASV_sums.py [Rosetta.csv] [out_fname.tsv]\n")
		exit()
	ros_fname, out_fname = sys.argv[1:]
	
	M, indices, sample_labels, ASV_IDs = read_rosetta_indexed(ros_fname, taxonomy=True)
	
	#M is a matrix with rows as samples, columns for ASVs
 	#indices is a dictionary mapping all tags ('UNTR', 'd10', etc) to a set of row indices in M corresponding to those samples
 	#cols is a list of column (sample) IDs
	
	Out = open(out_fname, "w+")
	for i in range(len(sample_labels)):
		Out.write(sample_labels[i]+"\t"+str(sum(M[i]))+"\n")
	Out.close()
		
	

	
