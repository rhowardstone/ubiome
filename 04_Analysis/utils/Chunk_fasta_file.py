import argparse
from Bio import SeqIO
import os

def split_fasta(fasta_file, output_dir, num_seqs_per_chunk):
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Initialize variables for processing sequences
    current_chunk = 1
    sequence_counter = 0
    chunk_sequences = []

    # Open the input FASTA file for streaming sequences
    for record in SeqIO.parse(fasta_file, 'fasta'):
        chunk_sequences.append(record)
        sequence_counter += 1

        # When reaching the specified number of sequences, write them to a file
        if sequence_counter >= num_seqs_per_chunk:
            chunk_filename = os.path.join(output_dir, f'chunk_{str(current_chunk).zfill(6)}.fasta')
            SeqIO.write(chunk_sequences, chunk_filename, 'fasta')
            print(f'Written {len(chunk_sequences)} sequences to {chunk_filename}')

            # Reset for the next chunk
            chunk_sequences = []
            sequence_counter = 0
            current_chunk += 1

    # Handle any remaining sequences in the last chunk
    if chunk_sequences:
        chunk_filename = os.path.join(output_dir, f'chunk_{str(current_chunk).zfill(6)}.fasta')
        SeqIO.write(chunk_sequences, chunk_filename, 'fasta')
        print(f'Written {len(chunk_sequences)} sequences to {chunk_filename}')

def main():
    parser = argparse.ArgumentParser(description='Split a FASTA file into chunks by number of sequences, without loading the entire file into memory.')
    parser.add_argument('fasta_file', type=str, help='Path to the input FASTA file.')
    parser.add_argument('output_dir', type=str, help='Directory to store the output FASTA files.')
    parser.add_argument('num_seqs_per_chunk', type=int, help='Number of sequences per output FASTA file.')
    args = parser.parse_args()

    split_fasta(args.fasta_file, args.output_dir, args.num_seqs_per_chunk)

if __name__ == "__main__":
    main()

