import sys

if __name__ == "__main__":
	if len(sys.argv)!=4:
		print("Error - usage:\n >> python3 Filter_rosetta.py [In.rosetta] [min_num_samples] [Out.rosetta]\n")
		print("\tWill produce a rosetta report csv containing only ASVs that occur in at least min_num_samples samples.\n")
		exit()
	in_fname, N, out_fname = sys.argv[1:]
	N = int(N)
	
	In = open(in_fname)
	Out = open(out_fname, 'w+')
	line = In.readline()
	Out.write(line)
	line = In.readline()
	while line != "":
		nsamps = len([ele for ele in line[:-1].split(",")[9:] if ele != "0"])
		if nsamps >= N:
			Out.write(line)
		line = In.readline()
	In.close()
	Out.close()
	
	
