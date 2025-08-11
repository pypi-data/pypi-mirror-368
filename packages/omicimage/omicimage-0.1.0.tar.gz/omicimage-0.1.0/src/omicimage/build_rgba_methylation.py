from omicimage.cli import parse_methylation_arguments
from omicimage.methylation_loader import load_scaled_cpg_methylation_data
from omicimage.sam_parser import parse_nucleotide_base_from_sam_methylation
from omicimage.utils import make_timestamped_output_directory, run_rgba_pipeline

# Main pipeline which calls the helper functions to ultimately create the pixel image.
# Parse the user input from the command line, and pass information to respective functions.
def main():
    
    cli_arguments = parse_methylation_arguments()
    methylation_data = load_scaled_cpg_methylation_data(cli_arguments.cpg_report)
    output_directory = make_timestamped_output_directory(cli_arguments.output_prefix)
    run_rgba_pipeline(parse_nucleotide_base_from_sam_methylation, cli_arguments.sam,[methylation_data, not cli_arguments.full_read, cli_arguments.mapq], cli_arguments.width, output_directory)


if __name__ == "__main__":
    main()
