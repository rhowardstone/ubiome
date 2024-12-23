import pandas as pd
import sys

def normalize_data(rosetta_file, totals_file, output_file):
    # Read the Rosetta file
    rosetta_df = pd.read_csv(rosetta_file, header=0)
    
    # Read the Totals file
    totals_df = pd.read_csv(totals_file, header=None, sep='\t', names=['SampleID', 'Total'])
    
    # Ensure the index matches for easy lookup
    totals_df.set_index('SampleID', inplace=True)
    
    # Normalize the counts in Rosetta.csv by the totals in Totals.tsv
    for col in rosetta_df.columns[9:]:  # Adjust index if necessary
        if col in totals_df.index:
            rosetta_df[col] = rosetta_df[col].astype(float) / totals_df.loc[col, 'Total']
    
    # Save the normalized data
    rosetta_df.to_csv(output_file, index=False)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Error - usage:\n >>> python script.py [Rosetta.csv] [Totals.tsv] [Output.csv]\n")
        sys.exit()
    
    rosetta_file, totals_file, output_file = sys.argv[1:]
    normalize_data(rosetta_file, totals_file, output_file)

