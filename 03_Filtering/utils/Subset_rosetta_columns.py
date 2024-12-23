import sys

if __name__ == "__main__":
	if len(sys.argv)!=5:
		print("Error - usage:\n >>> python3 Subset_rosetta_columns.py [Rosetta.csv] [0/1 discard/keep] [Columns.txt] [Rosetta_out.csv]\n")
		print("\t[0/1 discard/keep]\tIF 0, discard the columns in Columns.txt, otherwise, keep just those listed.")
		print("\t[Columns.txt]\tis newline-separated column names to keep\n")
		exit()
	ros_fname, keep, cols_fname, out_fname = sys.argv[1:]
	keep = keep == '1'
	
	In = open(cols_fname)
	cols = set([row for row in In.read().split("\n") if row!=""])
	In.close()
	
	In = open(ros_fname)
	ros = [row.split(",") for row in In.read().split("\n") if row!=""]
	In.close()
	
	ros = list(zip(*ros)) #transpose
	
	new_ros = ros[:9]
	for i in range(9,len(ros)):
		if (ros[i][0] in cols) == keep:
			new_ros.append(ros[i])
	del ros
	
	new_ros = list(zip(*new_ros)) #transpose back
	out_ros = [new_ros[0]]
	for i in range(1,len(new_ros)):
		tempsum = sum([int(ele) for ele in new_ros[i][9:]])
		if tempsum != 0:
			out_ros.append(new_ros[i])
	
	Out = open(out_fname, "w+")
	Out.write("\n".join([",".join(row) for row in out_ros])+"\n")
	Out.close()
	
	
	
