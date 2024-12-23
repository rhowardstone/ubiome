import sys
import os
from scipy.spatial.distance import braycurtis as BC
from utils import read_rosetta
from multiprocessing import Pool, cpu_count, current_process

def worker(task): #This should be taking way less time now - pls test --check
	inverted, sample_labels, start, temp_folder = task
	temp_file_path = os.path.join(temp_folder, f"temp_{current_process().pid}_{start}.tsv")
	
	with open(temp_file_path, 'w') as temp_file:
		i = start
		for j in range(i + 1, len(inverted)):
			if sample_labels[i] not in 'W1 W2'.split() and sample_labels[j] not in 'W1 W2'.split():
				grp1, day1, loc1 = sample_labels[i].split("_")[:3]
				grp2, day2, loc2 = sample_labels[j].split("_")[:3]
				if loc1 != loc2 and grp1 == grp2 and day1 == day2:
					temp_file.write("\t".join([grp1, day1[1:], 'btwn', 'Between', str(BC(inverted[i], inverted[j]))]) + "\n")
				elif loc1 == loc2 and grp1 == grp2 and grp1 == 'UNTR' and day1 == day2:
					temp_file.write("\t".join(['UNTR', day1[1:], loc1, 'Within', str(BC(inverted[i], inverted[j]))]) + "\n")
	return temp_file_path

def calculate_braycurtis_distances_parallel(input_file, output_file, nthreads, temp_folder):
	sample_labels, ros = read_rosetta(input_file, cols=True)
	inverted = [ [row[i] / sum(row) for i in range(len(row))] for row in zip(*[ros[ID][2] for ID in ros]) ]
	
	# Ensure the temporary folder exists
	os.makedirs(temp_folder, exist_ok=True)
	print("Chunking data..")
	# Prepare data for multiprocessing
	tasks = [(inverted, sample_labels, i, temp_folder) for i in range(len(inverted))]
	print("Beginning multiprocessing")
	# Parallel execution
	with Pool(processes=nthreads) as pool:
		tempfiles = pool.map(worker, tasks)
	
	# Combine results into the final output file
	with open(output_file, 'w') as out_file:
		for temp_file_path in tempfiles:
			#temp_file_path = os.path.join(temp_folder, temp_file_name)
			with open(temp_file_path, 'r') as temp_file:
				out_file.write(temp_file.read())
			os.remove(temp_file_path)  # Clean up temporary file

if __name__ == "__main__":
	if len(sys.argv) != 5:
		print("Error - usage:\n >>> python calculate_bc_distances.py [Rosetta.csv] [Output_file.tsv] [n_threads (-1 for all)] [Temp_folder]\n")
		sys.exit()

	in_fname, out_fname, nthreads, temp_folder = sys.argv[1:]
	if nthreads == '-1':
		nthreads = cpu_count()-1
	else:
		nthreads = int(nthreads)
	calculate_braycurtis_distances_parallel(in_fname, out_fname, nthreads, temp_folder)

