import sys


if __name__ == "__main__":
	if len(sys.argv)!=3:
		print("Error - usage:\n >>> python3 Zero-One_Rosetta.py [Rosetta.csv] [Identity_Rosetta.csv]\n")
		exit()
	in_fname, out_fname = sys.argv[1:]
	
	In = open(in_fname)
	Out = open(out_fname, 'w+')
	Out.write(In.readline()) #headers
	line = In.readline()
	while line != "":
		temp = line[:-1].split(",")
		Out.write(",".join(temp[:9] + ['1' if a!='0' else '0' for a in temp[9:]]) +"\n")
		line = In.readline()
	Out.close()
	In.close()
	
