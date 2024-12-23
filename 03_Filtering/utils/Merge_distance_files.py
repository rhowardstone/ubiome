import sys
from random import choice

if __name__ == "__main__":
	if len(sys.argv)<4:
		print("Error - usage:\n >>> python3 Merge_distance_files.py [Combined_out.csv] [In1.csv] [In2.csv]...")
		print("\t As long as the first three columns are readID, ASVID, dist, NOTHING ELSE will be copied to output.\n")
		exit()
	out_fname = sys.argv[1]
	fnames = sys.argv[2:]
	
	min_dists = {} #maps each read to its minimum distance
	min_lines = {} #maps the read with the minimum distance to a list of the input file line it came frmo 
	#readID, ASVID, dist, len(read), len(ASV), orientation of min dist\n')
	
	for f in fnames:
		print(f"Beginning {f}")
		In = open(f)
		Header = In.readline()
		line = In.readline()
		while line != "":
			temp = line[:-1].split(",")
			readID, ASVID, dist = temp[:3]
			dist = int(dist)
			line = ",".join(temp[:3])+'\n'
			
			if readID in min_dists:
				if dist < min_dists[readID]:
					min_dists[readID] = dist
					min_lines[readID] = [line]
				elif dist == min_dists[readID]:
					min_lines[readID].append(line)
			else:
				min_dists[readID] = dist
				min_lines[readID] = [line]
			
			line = In.readline()
		In.close()
	
	Out = open(out_fname, 'w+')
	for readID in min_dists:
		Out.write(choice(min_lines[readID]))  #break ties randomly
	Out.close()
		
