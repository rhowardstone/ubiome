import pandas as pd
import sys

def count_nonzero_asv_rows(matrix_file, asv_list_file, output_file):
    # Read the matrix into a DataFrame
    df = pd.read_csv(matrix_file, index_col=0)
    
    # Read the ASV IDs into a set for fast lookup
    with open(asv_list_file, 'r') as f:
        asv_list = {line.strip() for line in f}
    
    # Split the DataFrame into two: one for listed ASVs and one for the rest
    df_ar = df[df.index.isin(asv_list)]
    df_non_ar = df[~df.index.isin(asv_list)]
    
    # Count the number of nonzero entries for each DataFrame
    ar_nonzero_count = df_ar.apply(lambda x: (x > 0).sum())
    non_ar_nonzero_count = df_non_ar.apply(lambda x: (x > 0).sum())
    
    # Prepare the output DataFrame
    output_df = pd.DataFrame([ar_nonzero_count, non_ar_nonzero_count], index=['AR', 'non-AR'])
    
    # Write the output DataFrame to a CSV, preserving the header
    output_df.to_csv(output_file, header=True)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python Sum_AR_vs_not_numASVs.py <matrix_file.csv> <asv_list_file.txt> <output_file.csv>")
    else:
        _, matrix_file, asv_list_file, output_file = sys.argv
        count_nonzero_asv_rows(matrix_file, asv_list_file, output_file)

