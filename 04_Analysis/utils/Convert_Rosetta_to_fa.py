from utils import read_rosetta, write_fasta
import sys

if __name__ == "__main__":
	if len(sys.argv)!=3:
		print("Error - usage:\n >>> python3 Convert_Rosetta_to_fa.py [In.rosetta] [Out.fa]\n")
		exit()
	
	in_fname, out_fname = sys.argv[1:]
	
	ros = read_rosetta(in_fname)
	
	fa = {ID:ros[ID][0] for ID in ros}
	
	write_fasta(fa, out_fname)
