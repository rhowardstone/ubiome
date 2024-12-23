import sys

def read_fasta(file):
	"""
	Generator function to yield one sequence at a time from a FASTA file.
	"""
	with open(file, 'r') as fasta_file:
		sequence_id, sequence = '', ''
		for line in fasta_file:
			line = line.strip()
			if line.startswith(">"):
				if sequence_id:
					yield (sequence_id, sequence)
				sequence_id, sequence = line[1:], ''
			else:
				sequence += line
		# Yield the last sequence
		if sequence_id:
			yield (sequence_id, sequence)

if __name__ == "__main__":
	if len(sys.argv) != 5:
		print("Error - usage:\n >>> python3 Filter_amplicons.py [In.fasta] [min-len] [max-len] [Out.fasta]\n")
		exit()
	in_fname, min_len, max_len, out_fname = sys.argv[1:]
	min_len, max_len = int(min_len), int(max_len)
	
	Out = open(out_fname, 'w+')
	for ID, seq in read_fasta(in_fname):
		if min_len <= len(seq) <= max_len:
			Out.write('>'+ID+'\n')
			Out.write(seq+'\n')
	Out.close()
