#Take all read assignments from the <= 1M run, 
#   and add to that ONLY read assignments in Chunks #1-8 from Lactobacillus and Unclassified ASVs.
import os
from utils.utils import read_fasta

wd = '03_Filtering/'
nproc = 80

if 1 == 1:
	rosettas = []
	
	#/data/shoreline/rerun/03_Filtering/Chunk_1/Lactobacillus_ASVs_only.fasta
	for i in range(1,9):
		print(f"Subsetting Chunk {i}")
		Target_ASVs = [ID for ID in read_fasta(f'{wd}Chunk_{i}/Lactobacillus_ASVs_only.fasta')]
		Target_ASVs += [ID for ID in read_fasta(f'{wd}Chunk_{i}/unclassified_ASVs_only.fasta')]
		Target_ASVs = list(dict.fromkeys(Target_ASVs))
		Out = open(f'{wd}Chunk_{i}/Target_ASVs.txt', 'w+')
		Out.write("\n".join(Target_ASVs))
		Out.close()
		
		os.system(f"grep -f {wd}Chunk_{i}/Target_ASVs.txt {wd}Chunk_{i}/Infix-dists.csv > {wd}Chunk_{i}/Infix-dists_target_ASVs.csv")
		
		os.system(f"head -1 {wd}Chunk_{i}/RosettaReport.csv > {wd}Chunk_{i}/temp1.csv")
		os.system(f"grep -f {wd}Chunk_{i}/Target_ASVs.txt {wd}Chunk_{i}/RosettaReport.csv > {wd}Chunk_{i}/temp2.csv")
		os.system(f"cat {wd}Chunk_{i}/temp1.csv {wd}Chunk_{i}/temp2.csv > {wd}Chunk_{i}/RosettaReport_target_ASVs.csv")
		os.system(f"rm {wd}Chunk_{i}/temp2.csv {wd}Chunk_{i}/temp1.csv")
		#rosettas.append(

	print("Merging distance files")
	os.system(f"python3 {wd}utils/Merge_distance_files.py {wd}Method1-dists.csv {wd}ALL/Infix-dists.csv " + " ".join([f"{wd}Chunk_{i}/Infix-dists_target_ASVs.csv" for i in range(1,9)]))

	print("Plotting distance distribution")
	os.system(f'python3 {wd}utils/Plot_distribution.py {wd}Method1-dists.csv "," 2 0 0 -1 -1 -1 "" "Minimum Infix Edit Distance" "Number of Reads" 1 0 {wd}Method1-dists_edit_dist_distr.png')


	print("Plotting thresholding curve")
	#Then, plot how many reads we would keep with various infix edit distance thresholds:
	os.system(f"cut -f3 -d',' {wd}Method1-dists.csv | sort -n > temp.txt") #sort distance numerically ascending
	thresholds_file = 'temp2.txt'
	In, X, Y = open('temp.txt'), [], []  #Y is how many reads you'd keep, X is the threshold applied 
	line = In.readline()
	last = line.strip()
	line = In.readline()
	tot = 1
	while line != "":
		curr = line.strip()
		if curr != last:
			X.append(curr)   
			Y.append(tot)
			
		tot += 1
		last = curr
		line = In.readline()
	In.close()
	Y = [y/tot for y in Y]

	Out = open(thresholds_file, 'w+')
	for i in range(len(X)):
		Out.write(str(X[i])+"\t"+str(Y[i])+"\n")
	Out.close()
	os.system(f"python3 {wd}utils/Plot_scatter.py {thresholds_file} 0 '\t' 0 1 -1 1 0 1 'Infix Edit Distance Threshold' 'Proportion of Reads' {wd}Method1-Infix-dists_combined_thresholds.png")
	os.system('rm temp.txt temp2.txt')

	#Then filter reads by infix edist distance up to a reasonable value, such as 30 BPs from assigned ASV:
	print("Filtering by 30 BPs")
	os.system(f"python3 {wd}utils/Extract_abundances_from_read_trace_dist_files.py {wd}Method1-dists.csv {wd}sid_to_name.txt 30 {wd}Method1-Rosetta_I30.csv {wd}ALL/RosettaReport.csv " + " ".join([f"{wd}Chunk_{i}/RosettaReport_target_ASVs.csv" for i in range(1,9)]))


		
	# Remove post-mortem samples (bandaid)
	Out = open(f'{wd}post_mortem_samples.txt', 'w+')
	Out.write('ABX10_d30_LJ_M_a28\nABX10_d30_LJ_F_a32\nABX10_d30_LJ_F_a38')
	Out.close()

	os.system(f'python {wd}utils/Subset_rosetta_columns.py {wd}Method1-Rosetta_I30.csv 0 {wd}post_mortem_samples.txt {wd}Method1-Rosetta_I30.csv') # (bandaid)



	# Then, observe that many ASVs are low abundance, occuring in few samples:
	os.system(f'python3 {wd}utils/Calculate_ASV_nReads_nSamples.py {wd}Method1-Rosetta_I30.csv temp.txt')
	print(f"Writing to {wd}/Rosetta_Infix-dist30_ASV-nReads-nSamples.png")
	os.system(f'python3 {wd}utils/Plot_scatter_marginal.py temp.txt 0 "\t" 1 2 -1 1 1 "Number of Reads" "Number of Samples" {wd}Method1-Rosetta_I30_ASV-nReads-nSamples.png')
	os.system("rm temp.txt")

	print('Filtering ASVs by number of reads and samples')
	os.system(f"python3 {wd}utils/Filter_rosetta_by_nreads.py {wd}Method1-Rosetta_I30.csv 10 {wd}Method1-Rosetta_I30_r10.csv")
	os.system(f"python3 {wd}utils/Filter_rosetta_by_nsamples.py {wd}Method1-Rosetta_I30_r10.csv 2 {wd}Method1-Rosetta_I30_r10_s2.csv")

	print('Calculating NN edit distances')
	os.system(f"python3 {wd}utils/Calculate_ASV_NN_edist.py {wd}Method1-Rosetta_I30_r10_s2.csv {nproc} {wd}Method1-Rosetta_I30_r10_s2_NNDists.csv")
	os.system(f"python3 {wd}utils/Plot_scatter_marginal.py {wd}Method1-Rosetta_I30_r10_s2_NNDists.csv 1 ',' 7 4 -1 1 1 '' '' {wd}Method1-Rosetta_I30_r10_s2_NNdists_scatter.png")

	print('NN Filtering')
	os.system(f"python3 {wd}utils/Filter_rosetta_final.py {wd}Method1-Rosetta_I30_r10_s2.csv {wd}Method1-Rosetta_I30_r10_s2_NNDists.csv 1 {wd}Method1-Rosetta_I30_r10_s2_L1.csv")

	print("Calculating number of reads per sample..")
	os.system(f"python {wd}utils/Calculate_nReads_perSample.py {wd}Method1-Rosetta_I30_r10_s2_L1.csv {wd}Method1-Rosetta_I30_r10_s2_L1_nReads_perSample.tsv")

	for g in 'UNTR ABX10 ABX3CMT CMT'.split():
		print("Plotting num reads/sample distribution for", g)
		os.system(f'grep "^{g}" {wd}Method1-Rosetta_I30_r10_s2_L1_nReads_perSample.tsv > {wd}Method1-Rosetta_I30_r10_s2_L1_nReads_perSample_{g}.tsv')
		os.system(f"python {wd}utils/Plot_distribution.py {wd}Method1-Rosetta_I30_r10_s2_L1_nReads_perSample_{g}.tsv '	' 1 0 1 50000 0 125 '{g}' '#/Reads' '#/Samples' 1 0 {wd}Method1-Rosetta_I30_r10_s2_L1_nReads_perSample_{g}.png")
	#python3 Plot_distribution.py [In.txt] [delimiter] [col-index(0-indexed)] [0/1:Headers] [min-x] [max-x(-1 for no max)] [title] [x-lbl] [y-lbl] [0/1:X-log] [0/1:Y-log] [Out.png]







if 1 == 0:  # Taken care of in 04_Analysis
	print('Discarding samples with fewer than 500 reads')
	os.system(f"python {wd}utils/Report_outlier_samples.py {wd}Method1-Rosetta_I30_r10_s2_L1.csv 500 {wd}outliers.txt") #Filter samples with fewer than 500 reads
	with open(f'{wd}outliers.txt') as f:
		print("Number of outliers:", len(f.readlines()))

	os.system(f"python {wd}utils/Subset_rosetta_columns.py {wd}Method1-Rosetta_I30_r10_s2_L1.csv 0 {wd}outliers.txt {wd}Method1-Rosetta_I30_r10_s2_L1_r500.csv")

print('Done')

