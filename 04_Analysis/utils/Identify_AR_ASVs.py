import sys
from Bio import SeqIO

def main(genomes_fname, asv_fasta, thresholds, out_basename, ijk_file):
	# Read ASV lengths from FASTA
	asv_lengths = {rec.id: len(rec.seq) for rec in SeqIO.parse(asv_fasta, "fasta")}
	
	# Prepare output files for each threshold
	outputs = {threshold: open(f"{out_basename}_{threshold}.tsv", "w+") for threshold in thresholds}
	
	genomes = set()
	with open(genomes_fname) as f:
		for line in f:
			genomes.add(line.strip().split('\t')[1])
	
	
	K = 0
	# Process the .ijk file
	with open(ijk_file, 'r') as ijk:
		for line in ijk:
			K += 1
			if K%10000 == 0:
				print(K)
			genome_id, asv_id, edit_distance = line.strip().split('\t')
			genome_id = genome_id.split(' ')[0]  # Extract genome ID
			
			AR = 'N'
			if genome_id in genomes:
				AR = 'Y'
		
			edit_distance = int(edit_distance)
			asv_length = asv_lengths.get(asv_id, 0)
			percent_identity = 100 * (1 - edit_distance / asv_length) if asv_length else 0
			
			# Check against each threshold and write to corresponding file
			for threshold, outfile in outputs.items():
				if percent_identity >= threshold:
					outfile.write(f"{genome_id}\t{asv_id}\t{edit_distance}\t{percent_identity}\t{AR}\n")
	
	# Close output files
	for outfile in outputs.values():
		outfile.close()
	
	print("Identification of AR ASVs completed successfully!")

if __name__ == "__main__":
	if len(sys.argv) != 6:
		print("Usage: python Identify_AR_ASVs.py <ARG_counts.tsv> <ASVs.fasta> <ijk_file> <thresholds> <out_basename>")
		print("Example: python Identify_AR_ASVs.py ARG_results_genomes_1.tsv asvs.fasta \"95,97,99\" output ijk_file.ijk\n")
		sys.exit(1)
	
	genomes_fname = sys.argv[1]
	asv_fasta = sys.argv[2]
	ijk_file = sys.argv[3]
	thresholds = list(map(float, sys.argv[4].split(',')))
	out_basename = sys.argv[5]
	
	
	main(genomes_fname, asv_fasta, thresholds, out_basename, ijk_file)

