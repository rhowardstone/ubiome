import pandas as pd

# Categories and their corresponding files
categories = ['ARG', 'Ambiguous', 'non-ARG', 'Unmatched']
types = ['abund', 'ntaxa']

for T in types:
	files = [f'ARGs/AR_vs_not_98.0_{category}_{T}.csv' for category in categories]
	data = {}

	for file, category in zip(files, categories):
		try:
			# Assuming the first row is the header with sample names
			df = pd.read_csv(file)
			sample_names = df.columns[1:]  # skip the first column
			
			for sample_name in sample_names:
				match_count = int(df.loc[0, sample_name])  # first line after header
				non_match_count = int(df.loc[1, sample_name])  # second line after header

				if sample_name not in data:
					data[sample_name] = {cat: 0 for cat in categories}
					data[sample_name]['Total'] = 0

				data[sample_name][category] = match_count
				data[sample_name]['Total'] += match_count

		except FileNotFoundError:
			print(f"File not found: {file}")
		except Exception as e:
			print(f"Failed to process {file}: {e}")

	# Convert dictionary to DataFrame
	result_df = pd.DataFrame.from_dict(data, orient='index').reset_index()
	result_df.rename(columns={'index': 'Sample'}, inplace=True)
	result_df = result_df[['Sample'] + categories + ['Total']]  # reorder columns

	# Output file
	output_file = f'data/combined_ARG_counts_{T}.csv'
	result_df.to_csv(output_file, index=False)
	print(f"Output saved to {output_file}")

