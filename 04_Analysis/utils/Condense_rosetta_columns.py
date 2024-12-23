import sys

#UNTR_d0_GR_M_a1

if __name__ == "__main__":
	if len(sys.argv)!=5:
		print("Error - usage:\n >>> python3 Condense_rosetta_columns.py [In.rosetta] [columns_map.tsv] [0/1 days?] [Out.rosetta]\n")
		print("\t[columns_map]\tTSV with column name in first col, second is condensed column name\n")
		print("\t[0/1 days?]\tAre days included as the second underscore-separated condition label?\n")
		exit()
	ros_fname, cols_fname, days, out_fname = sys.argv[1:]
	
	In, mapper = open(cols_fname), {}
	line = In.readline()
	while line != "":
		old, new = line[:-1].split("\t")
		mapper[old] = new
		line = In.readline()
	In.close()
	
	new_colnames = list(dict.fromkeys(mapper.values()))
	temp = [c.split("_") for c in new_colnames]
	tmp = []
	for t in temp:
		if days == "1":
			if len(t)>1:
				t[1] = 60-int(t[1][1:])
		if len(t)>1:
			t = [t[2], t[0], t[1]] + t[3:]
		tmp.append(t)
	tmp.sort()
	temp = []
	for t in tmp[::-1]:
		if len(t)>1:
			t = [t[1], t[2], t[0]] + t[3:]
		if days == "1":
			if len(t)>1:
				t[1] = 'd'+str(60-t[1])
		temp.append(t)
	new_colnames = ["_".join([str(ele) for ele in c]) for c in temp]
	
	In = open(ros_fname)
	Out = open(out_fname, "w+")
	Header = In.readline()[:-1].split(",")
	Out.write(",".join(Header[:9])+","+",".join(new_colnames)+"\n")
	line = In.readline()
	while line != "":
		row = line[:-1].split(",")
		col_sums = {c:0 for c in new_colnames} #maps new colname to sum
		for i in range(9,len(Header)):
			col_sums[mapper[Header[i]]] += int(row[i]) #is new
		
		Out.write(",".join(row[:9]) + "," + ",".join([str(ele) for ele in [col_sums[c] for c in new_colnames]])+"\n")
		line = In.readline()
	In.close()
	Out.close()
		
	
	

	
	
