import sys

if __name__ == "__main__":
	if len(sys.argv)!=4:
		print("Error - usage:\n >>> python3 Summarize_by_tax.py [Rosetta.csv] [tax-index] [Out.csv]\n")
		exit()
	in_fname, index, out_fname = sys.argv[1:]
	index = int(index)
	
	vectors = {}
	In = open(in_fname)
	Columns = [ele for ele in In.readline()[:-1].split(",")[9:]]
	line = In.readline()
	while line != "":
		temp = line[:-1].split(",")
		abunds = [int(ele) for ele in temp[9:]]
		tax = temp[8].split(";")
		if len(tax)>index:
			tax = tax[index]
		else:
			tax = ";".join(tax)
		if tax in vectors:
			for i in range(len(Columns)):
				vectors[tax][i] += abunds[i]
		else:
			vectors[tax] = abunds
		line = In.readline()
	In.close()
	
	Out = open(out_fname, "w+")
	Out.write("Taxonomy,Dummy,Dummy,Dummy,Dummy,Dummy,Dummy,Dummy,Dummy,"+",".join(Columns)+"\n")
	for tax in sorted(vectors):
		Out.write(tax+",,,,,,,,,"+",".join([str(ele) for ele in vectors[tax]])+"\n")
	Out.close()
	
