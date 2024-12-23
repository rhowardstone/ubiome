import sys
from skbio.stats.ordination import pcoa
from scipy.spatial.distance import braycurtis as BC
from multiprocessing import Pool, cpu_count


def helper(i):
	global vects
	return [BC(vects[i], vects[j]) for j in range(len(vects))]

if __name__ == "__main__":
	if len(sys.argv)!=7:
		print("Error - usage:\n >>> python3 Generate_PCoA.py [RosettaReport.csv] [day1,day2,...] [0/1 Norm(sample sum)] [n_threads(-1 for all)] [Out_emb.tsv] [Out_var_rat.tsv]\n")
		print("\tUses Bray-Curtis dissimilarity to construct the distance matrix.\n")
		exit()
	in_fname, days_to_include, toNorm, n_threads, out_fname, out_varname = sys.argv[1:]
	n_threads = int(n_threads)
	maxthreads = cpu_count()
	if n_threads == -1 or n_threads > maxthreads:
		n_threads = maxthreads
	elif n_threads < 1:
		n_threads = 1
	days_to_include = set(days_to_include.split(","))
	global vects
	
	#print("Reading data")
	In = open(in_fname)
	ros = [row.split(",") for row in In.read().split("\n") if row!=""]
	In.close()
	
	#print("Transposing")
	lbls = ros[0][9:]
	vects = list(zip(*[row[9:] for row in ros[1:]]))  #rows for samples
	vects = [[int(ele) for ele in row] for row in vects]
	
	
	
	#print(len(vects), len(lbls))
	
	tempvects, templbls = [], []
	for i in range(len(lbls)):
		#print(lbls[i][:15])
		if lbls[i] not in 'W1 W2'.split():
			if lbls[i].split("_")[1] in days_to_include:
				templbls.append(lbls[i])
				tempvects.append(vects[i])
	vects, lbls = tempvects.copy(), templbls.copy()
	del tempvects, templbls

	tempvects = []
	templbls = []
	if toNorm == '1':
		for i in range(len(vects)):
			tot = sum(vects[i])
			if tot != 0:
				tempvects.append([vects[i][j]/tot for j in range(len(vects[i]))])
				templbls.append(lbls[i])
	
	vects, lbls = tempvects.copy(), templbls.copy()
	del tempvects, templbls
	
	with Pool(processes=n_threads) as pool:
		dists = pool.map(helper, [i for i in range(len(vects))])
	
	result = pcoa(dists)
	emb = result.samples.to_numpy()
	
	print("Writing output to", out_fname)
	Out = open(out_fname, 'w+')
	for i in range(len(emb)):
		Out.write(lbls[i]+"\t" + "\t".join([str(ele) for ele in emb[i]])+"\n")
	Out.close()
	
	print("Writing output to", out_varname)
	Out = open(out_varname, 'w+')
	Out.write("\n".join([str(ele) for ele in result.proportion_explained.to_numpy()])+"\n")
	Out.close()
	
	temp = [ele for ele in result.proportion_explained.to_numpy()]
	print(*temp[:2])
	print()
	'''
	
	explained = [0.8, 0.9, 0.95, 0.99, 0.999, 0.9999][::-1]
	tot, temp = 0, [ele for ele in result.proportion_explained.to_numpy()]
	for i in range(len(temp)):
		tot += temp[i]
		if len(explained)!=0:
			if tot >= explained[-1]:
				print(tot, "percent of variation is explained by the first", i+1, "dimensions")
				explained.pop()
		elif i in [4, 9, 14, 19, 24, 29, 39, 49, 74, 99, 149, 199, 249, 299, 499]:
			print(tot, "percent of variation is explained by the first", i+1, "dimensions")

	print()
	'''
	
	
