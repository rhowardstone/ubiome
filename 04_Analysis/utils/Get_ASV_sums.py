import sys


if __name__ == "__main__":
	if len(sys.argv)!=3:
		print("Error - usage:\n >>> python3 Get_ASV_sums.py [Rosetta.csv] [out_fname.tsv]\n")
		exit()
	ros_fname, out_fname = sys.argv[1:]
	
	Out = open(out_fname, 'w+')
	In = open(ros_fname)
	line = In.readline()
	line = In.readline()
	while line != "":
		temp = line[:-1].split(",")

		tax = temp[8].split(";")[7]

		tot = sum([int(ele) for ele in temp[9:]])
		Out.write(temp[0]+'\t'+tax+'-'+str(tot)+'\n')
		line = In.readline()
	Out.close()
	print(f"Output written to {out_fname}")
		

	
