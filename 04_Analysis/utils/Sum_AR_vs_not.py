import pandas as pd
import sys

def sum_asv_rows(matrix_file, asv_list_file, output_file):
    # Read the matrix into a DataFrame
    df = pd.read_csv(matrix_file, index_col=0)
    
    # Read the ASV IDs into a set for fast lookup
    with open(asv_list_file, 'r') as f:
        asv_list = {line.strip() for line in f}
    
    # Split the DataFrame into two: one for listed ASVs and one for the rest
    df_ar = df[df.index.isin(asv_list)]
    df_non_ar = df[~df.index.isin(asv_list)]
    
    # Sum the rows for each DataFrame
    ar_sum = df_ar.sum()
    non_ar_sum = df_non_ar.sum()
    
    # Prepare the output DataFrame
    output_df = pd.DataFrame([ar_sum, non_ar_sum], index=['AR', 'non-AR'])
    
    # Write the output DataFrame to a CSV, preserving the header
    output_df.to_csv(output_file, header=True)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python sum_ar_vs_not.py <matrix_file.csv> <asv_list_file.txt> <output_file.csv>")
    else:
        _, matrix_file, asv_list_file, output_file = sys.argv
        sum_asv_rows(matrix_file, asv_list_file, output_file)

