import pandas as pd
import numpy as np
import argparse

def main():
    # Setting up the command-line argument parsing
    parser = argparse.ArgumentParser(description='Convert IJK format file with string IDs to a tabular matrix CSV file.')
    parser.add_argument('ijk_file', help='Path to the input IJK file.')
    parser.add_argument('output_tsv', help='Path to the output TSV file.')
    parser.add_argument('--header', type=int, default=1, help='Number of header rows in the IJK file to skip (default is 1).')
    args = parser.parse_args()

    # Create data structures for recording matrix
    D = {}

    # Read the IJK file into a pandas DataFrame
    with open(args.ijk_file, 'r') as file:
        for _ in range(args.header):  # Skip header lines
            next(file)
        for line in file:
            i, j, k = line.strip().split("\t")
            if i not in D:
                D[i] = {}
            if j not in D:
                D[j] = {}
            D[i][j] = k
            D[j][i] = k  # If i and j should be symmetric

    # Ensure diagonal entries exist
    for A in D:
        D[A][A] = '0'  # Diagonal elements set to '0', ensure they are strings

    # Write to CSV
    All_IDs = list(D.keys())
    with open(args.output_tsv, 'w') as out:
        out.write("ID\t" + "\t".join(All_IDs) + "\n")
        for i in All_IDs:
            row = [D[i].get(j, '0') for j in All_IDs]  # Use '0' as default for missing values
            out.write(i + "\t" + "\t".join(map(str, row)) + "\n")  # Convert all to string

    print(f'Matrix saved to {args.output_tsv}')

if __name__ == '__main__':
    main()

