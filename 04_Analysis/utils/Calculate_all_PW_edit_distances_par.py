import sys, os
from utils import read_fasta, separate_fasta
from edlib import align
from multiprocessing import Pool, cpu_count



def helper(i):
    global ID_list, seqlist, temp_dir
    
    temp_out = temp_dir+str(i)+"_"+str(os.getpid())+".ijk"

    Out = open(temp_out, 'w+')
    for j in range(i+1, len(ID_list)):
        Out.write(ID_list[i]+"\t"+ID_list[j]+"\t"+str(align(seqlist[i], seqlist[j])['editDistance'])+"\n")
    Out.close()

    return temp_out


if __name__ == "__main__":
    if len(sys.argv)!=5:
        print("Error - usage:")
        print(" >>> python3 utils/Get_all_PW_edit_distances_par.py [In.fasta] [n_threads (-1 for all)] [temp_dir] [Out.ijk]\n")
        exit()
    global ID_list, seqlist, temp_dir
    in_fname, n_threads, temp_dir, out_fname = sys.argv[1:]
    n_threads = int(n_threads)
    if n_threads < 1 or n_threads > cpu_count()-1:
        n_threads = cpu_count()-1
    if temp_dir[-1] != '/':
        temp_dir += '/'
    
    ID_list, seqlist = separate_fasta(read_fasta(in_fname))
    

    with Pool(processes=n_threads) as pool:
        fnames = pool.map(helper, [i for i in range(len(ID_list)-1)])

    os.system('cat '+' '.join(fnames)+' > '+out_fname)

    #os.system('rm '+' '.join(fnames))

    #Out = open(out_fname, "w+")
    #for i in range(len(ID_list)-1):
    #    for j in range(i+1,len(ID_list)):
    #        Out.write(ID_list[i]+"\t"+ID_list[j]+"\t"+str(align(seqlist[i], seqlist[j])['editDistance'])+"\n")
    #Out.close()


