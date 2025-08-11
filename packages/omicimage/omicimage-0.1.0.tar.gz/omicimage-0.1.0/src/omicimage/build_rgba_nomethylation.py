from omicimage.cli import parse_nomethylation_arguments
from omicimage.sam_parser import parse_nucleotide_base_from_sam
from omicimage.utils import make_timestamped_output_directory, run_rgba_pipeline

# Main pipeline which calls the helper functions to ultimately create the pixel image.
# Parse the user input from the command line, and pass information to respective functions.
def main():
    
    cli_arguments = parse_nomethylation_arguments()
    output_directory = make_timestamped_output_directory(cli_arguments.output_prefix)
    run_rgba_pipeline(parse_nucleotide_base_from_sam, cli_arguments.sam, [not cli_arguments.full_read, cli_arguments.mapq], cli_arguments.width, output_directory)

if __name__ == "__main__":
    main()
