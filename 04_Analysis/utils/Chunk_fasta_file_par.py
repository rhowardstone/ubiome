import argparse
import os

def split_fasta(fasta_file, output_dir, mb_per_chunk):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    os.system(f"rm {output_dir}/*")  # Clear output dir first

    # Run the parallel command to split the file
    command = f"parallel -a {fasta_file} --block {mb_per_chunk}M --pipe-part --recend '\n' --recstart '>' 'cat > {output_dir}/chunk_{{#}}.fa'"
    os.system(command)

    # Find out how many files there are
    num_files = len([f for f in os.listdir(output_dir) if f.startswith('chunk_') and f.endswith('.fa')])
    print(f"Total files created: {num_files}")

    # Post-process files to adjust format   #PARALLELIZE THIS BEFORE RUNNING AGAIN - CHECK 'BANDAID.py'....
    for i in range(1, num_files + 1):
        file_path = os.path.join(output_dir, f"chunk_{i}.fa")
        if i < num_files:
            # Remove the last line from the current file
            os.system(f"sed -i '$d' {file_path}")
        if i > 1:
            # Prepend '>' to the next files
            os.system(f"sed -i '1s/^/>/' {file_path}")

def main():
    parser = argparse.ArgumentParser(description='Split a FASTA file into chunks by file size using parallel processing, with post-adjustment.')
    parser.add_argument('fasta_file', type=str, help='Path to the input FASTA file.')
    parser.add_argument('output_dir', type=str, help='Directory to store the output FASTA files.')
    parser.add_argument('mb_per_chunk', type=int, help='Number of MB (approx) per output FASTA file.')
    args = parser.parse_args()

    split_fasta(args.fasta_file, args.output_dir, args.mb_per_chunk)

if __name__ == "__main__":
    main()

