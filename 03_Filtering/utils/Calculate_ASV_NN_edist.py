import sys
from edlib import align
from utils import read_rosetta
from multiprocessing import Pool, cpu_count
from numpy import inf

def helper(i):
	global all_asvs
	min_dist, min_inds = inf, [-1]
	for j in range(len(all_asvs)):
		if j != i:
			dist = align(all_asvs[i], all_asvs[j])['editDistance']
			if dist < min_dist:
				min_dist = dist
				min_inds = [j]
			elif dist == min_dist:
				min_inds.append(j)
	return min_dist, min_inds

if __name__ == "__main__":
	if len(sys.argv)!=4:
		print("Error - usage:\n >>> python3 Calculate_edist_etc.py [Rosetta.csv] [n_threads(-1 for all)] [Out.csv]\n")
		exit()
	in_rosname, n_threads, out_fname = sys.argv[1:]
	n_threads = int(n_threads)
	global all_asvs
	
	max_cpus = cpu_count()-1
	if n_threads <= 0 or n_threads > max_cpus:
		n_threads = max_cpus
	
	ros = read_rosetta(in_rosname) #maps ASV ID to tuple (seq, tax, abund_vect)
	all_IDs = [ID for ID in ros]
	all_asvs = [ros[ID][0] for ID in all_IDs]
	
	with Pool(processes=n_threads) as pool:
		result = pool.map(helper, [i for i in range(len(all_asvs))])
	
	totals = [sum(ros[all_IDs[i]][2]) for i in range(len(all_asvs))]
	nonzeros = [len([e for e in ros[all_IDs[i]][2] if e!=0]) for i in range(len(all_asvs))]
	tot = sum(totals)
	
	Out = open(out_fname, "w+")
	Out.write('ASV_ID,Abund,Rel_abund,Num_samples,NN_dist,NN_ID(s),max_NN_abund,Ratio\n')
	for i in range(len(all_asvs)):
		temp = all_IDs[i]+","+str(totals[i])+"," #ID , Abund
		temp += str(totals[i]/tot)+"," #Rel_abund
		temp += str(nonzeros[i])+","  #Num_samples
		
		temp += str(result[i][0])+"," #NN dist
		
		NN_IDs = [all_IDs[j] for j in result[i][1]]
		temp += ";".join(NN_IDs)+"," #NN IDs
		
		max_NN_abund = max([sum(ros[all_IDs[j]][2]) for j in result[i][1]])
		temp += str(max_NN_abund)+"," #max_nn_abund
		
		temp += str(max_NN_abund/totals[i])+"\n" #ratio of nearest neighbor's abundance to own abundance
		Out.write(temp)
	Out.close()
		
		
		
		
		

	
	
	
