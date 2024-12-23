import sys
from collections import Counter

if __name__ == "__main__":
	if len(sys.argv)<7:
		print("Error - usage:\n >>> python3 Extract_abundances_from_read_traces_from_multple_runs.py [Merged-Infix-edit-distances.csv] [sid_to_name.ssv] [distance-threshold] [RosettaReport_out_corrected.csv] [RosettaReport1.csv] [ [RosettaReport2.csv] ... \n")
		print("\tNOTE: COLUMNS MUST BE ALIGNED!\n")
		print("\tTaxonomy data will be taken from the first rosetta report containing that ASV\n")
		print("\tONLY ASVs contained within one of the rosetta reports will be output.\n")
		exit()
	in_fname, mapper_fname, thresh, out_fname = sys.argv[1:5]
	ros_fnames = sys.argv[5:]
	thresh = int(thresh)
	
	print('distance file:', in_fname)
	print('sample ID mapper:', mapper_fname)
	print('inclusive upper bound on infix distance:', thresh)
	print('Rosetta files from which the taxonomy and other info will be preserved:')
	print(ros_fnames)
	print()
	print('Output filename:', out_fname)
	print()
	
	In = open(mapper_fname)
	temp = [row.split(" ") for row in In.read().split("\n") if row!=""]
	In.close()
	mapper = {row[0]:row[1] for row in temp}
	
	print("Reading rosettas")
	rosetta = []
	Headers = []
	ros_IDs = set()
	for ros_fname in ros_fnames:
		In = open(ros_fname)
		Headers.append(In.readline())
		tmp_rosetta = [row.split(",") for row in In.read().split("\n") if row!=""]
		In.close()
		for row in tmp_rosetta[1:]:
			if row[0] not in ros_IDs:
				rosetta.append(row)
				ros_IDs.add(row[0])
			#else do nothing, take the first taxonomy that comes along
	
	
	#Headers[0].split(",")[:9]
	
	#m64248e_230209_145912/622/ccs/W1,816b5e5f85281295bd26e6211176aec2,4,2388,2282,R
	
	print("Counting reads and tracking samples")
	Counts = {}
	samples = []
	In = open(in_fname)
	line = In.readline()
	while line != "":
		temp = line[:-1].split(",")   #m64248e_230209_145912/1084/ccs/W1,816b5e5f85281295bd26e6211176aec2,8,2389,2282,R
		ASV_ID = temp[1]
		dist = int(temp[2])
		if dist <= thresh:
			samp = temp[0].split("/")[-1]
			samples.append(samp)
			if ASV_ID not in Counts:
				Counts[ASV_ID] = Counter()
			else:
				Counts[ASV_ID][samp] += 1
		#for ele in temp[2:]:
		#	samp = ele.split("/")[-1]
		#	samples.append(samp)
		#	Counts[ASV_ID][samp] += 1

		line = In.readline()
	In.close()
	samples = sorted(list(dict.fromkeys(samples)))
	
	print("Writing output\n")
	
	Out = open(out_fname, 'w+')
	Out.write(",".join(Headers[0].split(",")[:9])+","+",".join([mapper[s] for s in samples])+"\n")
	for i in range(len(rosetta)):
		ASV_ID = rosetta[i][0]
		if ASV_ID in Counts:
			Out.write(",".join(rosetta[i][:9]) + "," + ",".join([str(Counts[ASV_ID][samples[j]]) for j in range(len(samples))])+'\n')
	Out.close()
			
			
			
