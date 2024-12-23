import sys


if __name__ == "__main__":
	if len(sys.argv)!=3:
		print("Error - usage:\n >>> python3 utils/Convert_rosetta_to_linegraph_format.py [Rosetta.csv] [Out.tsv]\n")
		exit()
	in_fname, out_fname = sys.argv[1:]
	
	In = open(in_fname)
	Out = open(out_fname, 'w+')
	Headers = In.readline()[:-1].split(",")[9:]
	line = In.readline()
	while line != "":
		temp = line[:-1].split(",")
		ID, counts = temp[0], temp[9:]
		for i in range(len(Headers)):
			if Headers[i] not in "W1 W2".split():
				#if float(counts[i])!=0:
				group, day, site = Headers[i].split("_")[:3]
				day = day[1:]
				Out.write("\t".join([group, day, site, ID, counts[i]])+"\n")
		line = In.readline()
	Out.close()
	In.close()
