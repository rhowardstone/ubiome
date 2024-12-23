import sys

if len(sys.argv)!=4:
	print("Error - usage:\n >>> python3 Convert_PCoA_format.py [In-ordination.txt] [Out-matrix.tsv] [Out-varrats.txt]\n")
	exit()
in_fname, out_fname_matrix, out_fname_varrats = sys.argv[1:]

In = open(in_fname)
temp = [row.split('\t') for row in In.read().split("\n")]
In.close()

varrats = temp[4]
temp = temp[9:-5]

Out = open(out_fname_matrix, 'w+')
Out.write("\n".join(["\t".join(row) for row in temp])+"\n")
Out.close()

Out = open(out_fname_varrats, 'w+')
Out.write("\n".join(varrats)+"\n")
Out.close()



