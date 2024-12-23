import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
import argparse

def main(input_file, output_file):
    # Activate the automatic conversion of rpy2
    pandas2ri.activate()

    # Load R's utility package
    ro.r('library(immunedeconv)')

    # Read the data in R using read.table for TSV files
    ro.r(f'gene_expression_matrix <- as.matrix(read.table("{input_file}", sep="\\t", header=TRUE, row.names=1))')

    # Perform deconvolution
    ro.r('deconv_results <- deconvolute_mouse(gene_expression_matrix, "mmcp_counter")')

    # Save the output in TSV format
    ro.r(f'write.table(deconv_results, "{output_file}", sep="\\t", quote=FALSE)')

if __name__ == "__main__":
    # Set up the argument parser
    parser = argparse.ArgumentParser(description='Deconvolute RNA-Seq data using R immunedeconv package from Python.')
    parser.add_argument('input_file', type=str, help='Input TSV file path containing RNA-Seq data.')
    parser.add_argument('output_file', type=str, help='Output TSV file path to save the deconvolution results.')

    # Parse the arguments
    args = parser.parse_args()

    # Run the main function
    main(args.input_file, args.output_file)

