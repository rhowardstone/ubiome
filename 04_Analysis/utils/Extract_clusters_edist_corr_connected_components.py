import argparse
import networkx as nx

def parse_args():
    parser = argparse.ArgumentParser(description='Extract connected components from pairwise data based on thresholds.')
    parser.add_argument('input_file', type=str, help='Input TSV file with ID1, ID2, edit_distance, and correlation.')
    parser.add_argument('x', type=int, help='Threshold for edit distance.')
    parser.add_argument('y', type=float, help='Threshold for correlation.')
    parser.add_argument('t', type=int, choices=[0, 1], help='Logical flag (0 for OR, 1 for AND).')
    parser.add_argument('output_file', type=str, help='Output file to write the connected components.')
    return parser.parse_args()

def build_graph(input_file, x, y, t):
    graph = nx.Graph()
    with open(input_file, 'r') as file:
        for line in file:
            parts = line.strip().split('\t')
            id1, id2, edit_distance, correlation = parts[0], parts[1], int(parts[2]), float(parts[3])
            
            if t == 1:  # AND condition
                if correlation >= y and edit_distance <= x:
                    graph.add_edge(id1, id2)
            else:  # OR condition
                if correlation >= y or edit_distance <= x:
                    graph.add_edge(id1, id2)
    
    return graph

def write_output(output_file, components):
    with open(output_file, 'w') as file:
        for component in components:
            file.write('\t'.join(component) + '\n')

def main():
    args = parse_args()
    graph = build_graph(args.input_file, args.x, args.y, args.t)
    components = list(nx.connected_components(graph))
    write_output(args.output_file, components)

if __name__ == "__main__":
    main()

