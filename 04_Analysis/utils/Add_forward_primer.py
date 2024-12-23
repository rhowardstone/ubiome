import sys
from utils import read_fasta, write_fasta

if __name__ == "__main__":
	if len(sys.argv)!=4:
		print("Error - usage:\n >>> python3 Add_forward_primer.py [In.fa] [seq] [Out.fa]\n")
		exit()
	in_fname, seq, out_fname = sys.argv[1:]
	
	fa = read_fasta(in_fname)
	fa = {ID:seq+fa[ID] for ID in fa}
	write_fasta(fa, fname=out_fname)
