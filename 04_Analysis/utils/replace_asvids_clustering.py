import csv
import argparse

def load_sums(file_path):
    """ Load the sums from the first file into a dictionary. """
    sums_dict = {}
    with open(file_path, 'r') as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            if len(row) == 2:
                sums_dict[row[0]] = row[1]
    return sums_dict

def replace_asvids(input_file, output_file, sums_dict):
    """ Replace ASVIDs in the second file with ASVID(sum) and write to a third file. """
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        content = infile.read()
        for asvid, sum_value in sums_dict.items():
            content = content.replace(asvid, f"{asvid}({sum_value})")
        outfile.write(content)

def main():
    parser = argparse.ArgumentParser(description='Replace ASVIDs with ASVID(sum) based on sums from a tab-separated file.')
    parser.add_argument('sums_file', type=str, help='File path for the tab-separated sums file (ASVID and sum).')
    parser.add_argument('input_file', type=str, help='File path for the input file where ASVIDs need to be replaced.')
    parser.add_argument('output_file', type=str, help='File path for the output file with ASVIDs replaced.')

    args = parser.parse_args()

    # Load sums from the first file
    sums_dict = load_sums(args.sums_file)

    # Replace ASVIDs in the second file and write to the third file
    replace_asvids(args.input_file, args.output_file, sums_dict)

if __name__ == "__main__":
    main()

