# Load the CpG report and parse the tab delimited fields.
# Extract relevant information such as the chromosome, position and methylation percentage. 
# Scale the methylation percentage (0–100) to an 8-bit value (0–255).
# Return a dictionary mapping of the chromosome and position to the scaled methylation values.
def load_scaled_cpg_methylation_data(cpg_report_path):

    scale_multiplier = 2.55
    scaled_cpg_methylation_dict = {}

    with open(cpg_report_path) as cpg_file:
        for line in cpg_file:
            if not line.strip():
                continue

            fields = line.strip().split('\t')
            if len(fields) < 4:
                continue

            chromosome = fields[0]

            try:
                cpg_position = int(fields[1])
                methylation_percent = float(fields[3])
            except ValueError:
                print("Error: Incorrect file provided.")
                print(f"Line in question: {line.strip()}")
                exit(1)  

            scaled_methylation_percentage = int(methylation_percent * scale_multiplier)
            scaled_cpg_methylation_dict[(chromosome, cpg_position)] = scaled_methylation_percentage 
    return scaled_cpg_methylation_dict
