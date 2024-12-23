import sys

if __name__ == "__main__":
	if len(sys.argv)!=4:
		print("Error - usage:\n >>> python3 Subset_rosetta_columns.py [Rosetta.csv] [Columns-order.txt] [Rosetta_out.csv]\n")
		print("\t[Columns.txt]\tis newline-separated column names to keep\n")
		exit()
	ros_fname, cols_fname, out_fname = sys.argv[1:]
	
	In = open(cols_fname)
	cols = [row for row in In.read().split("\n") if row!=""]
	In.close()
	cols = {cols[i]:i for i in range(len(cols))} #column ID maps to sorted index
	
	In = open(ros_fname)
	ros = [row.split(",") for row in In.read().split("\n") if row!=""]
	In.close()
	
	ros = list(zip(*ros)) #transpose
	
	new_ros = ros[:9] + sorted(ros[9:], key = lambda x:cols[x[0]])
	
	
	new_ros = list(zip(*new_ros)) #transpose back
	out_ros = [new_ros[0]]
	for i in range(1,len(new_ros)):
		out_ros.append(new_ros[i])
	
	Out = open(out_fname, "w+")
	Out.write("\n".join([",".join(row) for row in out_ros])+"\n")
	Out.close()
	
	
	
