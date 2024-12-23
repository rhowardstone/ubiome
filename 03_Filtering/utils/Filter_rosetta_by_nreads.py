import sys

if __name__ == "__main__":
	if len(sys.argv)!=4:
		print("Error - usage:\n >> python3 Filter_rosetta.py [In.rosetta] [Abundance_min] [Out.rosetta]\n")
		exit()
	in_fname, T, out_fname = sys.argv[1:]
	T = float(T)
	
	towrite = {} #maps line to sum abund
	#tot = 0
	In = open(in_fname)
	Out = open(out_fname, 'w+')
	
	line = In.readline()
	Out.write(line)
	
	line = In.readline()
	while line != "":
		abund = sum([int(ele) for ele in line[:-1].split(",")[9:]])
		#tot += abund
		towrite[line] = abund
		line = In.readline()
	In.close()
	
	for line in towrite:
		if towrite[line] >= T:
			Out.write(line)
	Out.close()
	
	
