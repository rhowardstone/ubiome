import sys



# ASV_ID  Abund   Rel_abund       Num_samples     NN_dist NN_ID(s)        max_NN_abund
# 0:Abund   1:Num_samples     2:NN_distance	3:max_NN_abund


#editdistancefile
#ASV_ID0,Abund1,Rel_abund2,Num_samples3,NN_dist4,NN_ID5(s),max_NN_abund6,Ratio7
# ASV_ID, Abund, Rel_abund, Num_samples, NN_dist, NN_ID(s) ,max_NN_abund, Ratio

if __name__ == "__main__":
	if len(sys.argv)!=5:
		print("Error - usage:\n >>> python3 Filter_rosetta_final.py [Rosetta_in.csv] [Edist_stats.csv] [edist-level] [Rosetta_out.csv]\n")
		print("\t[Edist_stats.tsv]\tAs produced by '/data/shoreline/Clean/Filtering/Run_results/Calculate_ASV_NN_edist.py'")
		print("\tRosetta Report will be filtered to only ASVs that meet all the following criteria:")
		print("\t\t1) Occurs in more than one sample, AND:")
		print("\t\t2) Contains 10 or more reads, AND:")
		print("\t\t3) EITHER  Ratio of NN abundance:abundance is less than 100,  OR  edit distance to NN greater than 1.\n")
		print("\t\t(this has since been extended to edist-level: 1=50x1 / 2=158x2 / 3=500x3 / 4=1581x4 / 5=5000x5) (THIS IS IGNORED)\n")
		print("\tAll others will be excluded.\n")
		exit()
	ros_fname, stats_fname, edist_level, out_fname = sys.argv[1:]
	
	edist_level = 1
	
	stats = {}
	In = open(stats_fname)
	line = In.readline()
	line = In.readline()
	while line != "":
		temp = line[:-1].split(",")
		stats[temp[0]] = [float(temp[i]) for i in [1, 3, 4, 7]]  #meaning: abundance, nSamples, NN_dist, Ratio (temp[0] is ASVID)
		line = In.readline()
	In.close()
	
	toExclude = []
	for ID in stats:
		if stats[ID][1] == 1: #nSamps
			toExclude.append(ID)
		if stats[ID][0] < 10: #nReads
			toExclude.append(ID)
		dist_t, rat_t = 1, 1000
		for _ in range(int(1)):
			if stats[ID][2] <= dist_t and stats[ID][3] >= rat_t:  #If edist is <= thresh (1) and Ratio >= thresh (1000) - discard:
				toExclude.append(ID)
			dist_t += 1
			rat_t *= 10**0.5
	toExclude = set(toExclude)
	
	toInclude = set([ID for ID in stats if ID not in toExclude])
	#for ID in stats: #really hard to do while extending def'n of (3)..
	#	if stats[ID][1] > 1:
	#		if stats[ID][0] >= 10:
	#			if stats[ID][2] > 1 or stats[ID][3] < 1000:  #was: '...or stats[ID][3]/stats[ID][0]' --why ????
	#				toInclude.append(ID)
	#toInclude = set(toInclude)
	
	In = open(ros_fname)
	Out = open(out_fname, 'w+')
	Out.write(In.readline())
	line = In.readline()
	while line != "":
		if line[:-1].split(",")[0] in toInclude:
			Out.write(line)
		line = In.readline()
	In.close()
	Out.close()
	
