import sys, os
from utils import read_fasta, separate_fasta
from edlib import align
from multiprocessing import Pool, cpu_count



def helper(args):
	ID, seq, i = args
	global ID_list1, seqlist1, temp_dir
	
	temp_out = temp_dir+str(i)+"_"+str(os.getpid())+".ijk"

	Out = open(temp_out, 'w+')
	for j in range(len(ID_list1)):
		Out.write(ID_list1[j]+"\t"+ID+"\t"+str(align(seq, seqlist1[j])['editDistance'])+"\n")
	Out.close()

	return temp_out


if __name__ == "__main__":
	if len(sys.argv)!=6:
		print("Error - usage:\n >>> python3 utils/Get_all_PW_edit_distances_par.py [In1.fasta] [In2.fasta] [n_threads (-1 for all)] [temp_dir] [Out.ijk]\n")
		print("\tIf one file has many more sequences, please place that one as [In1.fasta]\n")
		exit()
	global ID_list1, seqlist1, ID_list2, seqlist2, temp_dir
	in_fname1, in_fname2, n_threads, temp_dir, out_fname = sys.argv[1:]
	n_threads = int(n_threads)
	if n_threads < 1 or n_threads > cpu_count()-1:
		n_threads = cpu_count()-1
	if temp_dir[-1] != '/':
		temp_dir += '/'
	
	ID_list1, seqlist1 = separate_fasta(read_fasta(in_fname1))
	ID_list2, seqlist2 = separate_fasta(read_fasta(in_fname2))
	
	data = zip(ID_list2, seqlist2, range(len(ID_list2)))

	with Pool(processes=n_threads) as pool:
		fnames = pool.map(helper, data)

	#os.system("ulimit -n 99999999")

	os.system('cat '+' '.join(fnames)+' > '+out_fname)

	#os.system('rm '+' '.join(fnames))



