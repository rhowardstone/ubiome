import sys, os
from utils import read_rosetta
from edlib import align
from multiprocessing import Pool, cpu_count
from scipy.stats import pearsonr


def helper(i):
	global ID_list, ros, temp_dir
	
	temp_out = temp_dir+str(i)+"_"+str(os.getpid())+".ijk"
	
	ID_i = ID_list[i]
	Out = open(temp_out, 'w+')
	for j in range(i+1, len(ID_list)):
		ID_j = ID_list[j]
		edist = align(ros[ID_i][0], ros[ID_j][0])['editDistance'] # A lot is excluded here - we could look at cigar strings, homopolymer insertions etc
		corr = pearsonr(ros[ID_i][2], ros[ID_j][2])[0]  # We also totally ignore the p-value..
		Out.write("\t".join([ID_i, ID_j, str(edist), str(corr)])+"\n") 
	Out.close()

	return temp_out


if __name__ == "__main__":
	if len(sys.argv)!=5:
		print("Error - usage:")
		print(" >>> python3 utils/Calculate_all_Rosetta_PW_edit_distances_and_corr_par.py [Rosetta.csv] [n_threads (-1 for all)] [temp_dir] [Out.tsv]\n")
		exit()
	global ID_list, ros, temp_dir
	in_fname, n_threads, temp_dir, out_fname = sys.argv[1:]
	n_threads = int(n_threads)
	if n_threads < 1 or n_threads > cpu_count()-1:
		n_threads = cpu_count()-1
	if temp_dir[-1] != '/':
		temp_dir += '/'
	
	ros = read_rosetta(in_fname)   #ASVID:(seq, tax, abund_vector)
	ID_list = [ID for ID in ros]
	
	with Pool(processes=n_threads) as pool:
		fnames = pool.map(helper, [i for i in range(len(ID_list)-1)])

	os.system('cat '+' '.join(fnames)+' > '+out_fname)

	os.system('rm '+' '.join(fnames))

	#Out = open(out_fname, "w+")
	#for i in range(len(ID_list)-1):
	#	for j in range(i+1,len(ID_list)):
	#		Out.write(ID_list[i]+"\t"+ID_list[j]+"\t"+str(align(seqlist[i], seqlist[j])['editDistance'])+"\n")
	#Out.close()


