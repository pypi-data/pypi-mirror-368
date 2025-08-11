
import argparse

# Import argument parser in order to accurately handle user input from the command line.
# Add required and optional arguments.
# A default width is set if one is not provided.
# Default to extracting only one base from each read.
def parse_nomethylation_arguments():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("sam", help="Input SAM file")
    parser.add_argument("output_prefix", help="Prefix for naming the output folder")
    parser.add_argument("--width", type=int, default=2500, help="Image width")
    parser.add_argument("--full-read", action="store_true", help="Extract all bases from each read, the default is only the first base")
    parser.add_argument("--mapq", type=int, default=None, help="Filter for mapping quality (MAPQ). If no value is provided the filtering is not applied.")
    args = parser.parse_args()

    if args.mapq is not None and args.mapq < 0:
        parser.error("--mapq must be non-negative value")

    return args

def parse_methylation_arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument("sam", help="Input SAM file")
    parser.add_argument("cpg_report", help="Bisulfite Sequencing CpG report")
    parser.add_argument("output_prefix", help="Prefix for naming the output folder")
    parser.add_argument("--width", type=int, default=2500, help="Image width")
    parser.add_argument("--full-read", action="store_true", help="Extract all bases from each read, the default is only the first base")
    parser.add_argument("--mapq", type=int, default=None, help="Filter for mapping quality (MAPQ). If no value is provided the filtering is not applied.")

    args = parser.parse_args()

    if args.mapq is not None and args.mapq < 0:
        parser.error("--mapq must be non-negative value")

    return args
