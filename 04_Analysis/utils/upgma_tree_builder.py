import numpy as np
import argparse
from scipy.cluster.hierarchy import linkage, to_tree
from Bio import Phylo
from io import StringIO

def read_distance_file(filename):
    """Read the pairwise distances from a file and return a square distance matrix."""
    with open(filename, 'r') as file:
        data = file.read().splitlines()
    labels = set()
    distances = {}

    for line in data:
        id1, id2, dist = line.split()
        dist = float(dist)
        labels.update([id1, id2])
        distances[(id1, id2)] = dist
        distances[(id2, id1)] = dist
    
    # Create a full list of labels
    labels = sorted(labels)
    label_index = {label: idx for idx, label in enumerate(labels)}
    
    # Create a square matrix
    matrix_size = len(labels)
    dist_matrix = np.zeros((matrix_size, matrix_size))
    
    for (id1, id2), dist in distances.items():
        idx1, idx2 = label_index[id1], label_index[id2]
        dist_matrix[idx1][idx2] = dist
        dist_matrix[idx2][idx1] = dist
    
    return labels, dist_matrix

def perform_upgma(dist_matrix):
    """Perform UPGMA clustering on the distance matrix and return the tree in Newick format."""
    linkage_matrix = linkage(dist_matrix, method='average')
    tree = to_tree(linkage_matrix, rd=False)
    newick_tree = Phylo.to_string(tree, 'newick')
    return newick_tree

def main(input_file, output_file):
    labels, dist_matrix = read_distance_file(input_file)
    newick_tree = perform_upgma(dist_matrix)
    
    with open(output_file, 'w') as f:
        f.write(newick_tree)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build a UPGMA tree from a pairwise distance matrix.")
    parser.add_argument("input_file", type=str, help="Input file path containing pairwise distances.")
    parser.add_argument("output_file", type=str, help="Output file path for the Newick format tree.")
    
    args = parser.parse_args()
    main(args.input_file, args.output_file)

