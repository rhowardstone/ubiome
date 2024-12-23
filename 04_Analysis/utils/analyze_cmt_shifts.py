import pandas as pd
import numpy as np
from utils import read_rosetta_indexed, read_rosetta

def analyze_cmt_introductions(in_fname):
	"""
	Analyze ASVs uniquely introduced by CMT treatment.
	"""
	# Read the data two ways - one for the matrix/indices, one for taxonomy
	M, indices, sample_labels, ASV_IDs = read_rosetta_indexed(in_fname, relative=False, taxonomy=True)
	rosetta = read_rosetta(in_fname)  # Get full rosetta dictionary for taxonomy
	
	# Get donor ASVs
	donor_indices = {i for i, label in enumerate(sample_labels) if label in ['W1', 'W2']}
	donor_asvs = {i for i in range(len(ASV_IDs)) 
				  for di in donor_indices 
				  if M[di][i] > 0}
	
	results = []
	
	for site in ['LJ', 'GR']:
		# Get all pre-CMT indices for this site
		early_days = ['d-2', 'd1', 'd3']
		early_site_indices = set()
		for day in early_days:
			early_site_indices.update(indices[site].intersection(indices[day]))
			
		# Get indices for non-CMT treatments (to exclude their ASVs)
		non_cmt_indices = set()
		for treatment in ['UNTR', 'ABX10']:
			non_cmt_indices.update(indices[site].intersection(indices[treatment]))
		
		# Find ASVs that appear in non-CMT treatments
		non_cmt_asvs = {i for i in range(len(ASV_IDs))
					   for ni in non_cmt_indices
					   if M[ni][i] > 0}
		
		# Find ASVs present before CMT
		pre_cmt_asvs = {i for i in range(len(ASV_IDs))
					   for si in early_site_indices
					   if M[si][i] > 0}
		
		# Find truly new CMT-introduced ASVs
		new_cmt_asvs = donor_asvs - pre_cmt_asvs - non_cmt_asvs
		
		# For each new ASV, track when it first appears in CMT/ABX3CMT groups
		for asv_idx in new_cmt_asvs:
			asv_id = ASV_IDs[asv_idx]
			for treatment in ['CMT', 'ABX3CMT']:
				first_appearance = None
				abundance_at_appearance = 0
				
				for day in ['d5', 'd8', 'd10', 'd30', 'd60']:
					day_indices = indices[site].intersection(indices[treatment]).intersection(indices[day])
					day_abundances = [M[di][asv_idx] for di in day_indices]
					if any(abund > 0 for abund in day_abundances):
						first_appearance = day
						abundance_at_appearance = sum(day_abundances) / len(day_abundances)
						break
				
				if first_appearance:
					# Get taxonomy from rosetta dictionary
					taxonomy = rosetta[asv_id][1].split(';')
					genus = taxonomy[5] if len(taxonomy) > 5 else 'Unknown'
					species = taxonomy[6] if len(taxonomy) > 6 else 'Unknown'
					
					results.append({
						'Site': site,
						'Treatment': treatment,
						'ASV_ID': asv_id,
						'First_Appearance': first_appearance,
						'Abundance_At_Appearance': abundance_at_appearance,
						'Genus': genus,
						'Species': species,
						'Full_Taxonomy': rosetta[asv_id][1]
					})
	
	return pd.DataFrame(results)

if __name__ == "__main__":
	results = analyze_cmt_introductions("data/Filt.csv")
	
	# Print summary statistics
	print("\nSummary of CMT-specific introductions:")
	print("=" * 60)
	summary = results.groupby(['Site', 'Treatment']).agg({
		'ASV_ID': 'count',
		'First_Appearance': lambda x: x.value_counts().index[0]
	}).reset_index()
	summary.columns = ['Site', 'Treatment', 'Number_of_ASVs', 'Most_Common_First_Appearance']
	print(summary)
	
	# Print detailed species breakdown
	print("\nNewly introduced species by site and treatment:")
	print("=" * 60)
	
	for treatment in ['CMT', 'ABX3CMT']:
		for site in ['LJ', 'GR']:
			mask = (results['Site'] == site) & (results['Treatment'] == treatment)
			species_counts = results[mask]['Species'].value_counts()
			
			if len(species_counts) > 0:
				print(f"\n{site} - {treatment}:")
				for species, count in species_counts.items():
					# Get mean abundance for this species
					mean_abund = results[mask & (results['Species'] == species)]['Abundance_At_Appearance'].mean()
					print(f"  - {species}: {count} ASVs, mean abundance {mean_abund:.4f}")
	
	# Save full results
	results.to_csv("data/cmt_introductions.csv", index=False)
