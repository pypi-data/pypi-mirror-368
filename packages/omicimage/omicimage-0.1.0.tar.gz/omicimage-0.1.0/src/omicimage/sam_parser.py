import pysam
from tqdm import tqdm

from omicimage.shared import nucleotide_base_to_grayscale, check_strand, pixel_to_base_coordinates, phred_score_to_uint8, MAX_BASE_QUALITY

# Using the pysam library to open the SAM file.
# This allows for the iteration over the sequencing reads.
def open_sam_file(path):

    return pysam.AlignmentFile(path, "r")

# Calculates the height of the image, if there is a remainder we add an additional row to accomodate it.
def calculate_image_height(image_dictionary, image_width):

    number_of_pixels = len(image_dictionary)
    image_height = number_of_pixels // image_width
    
    if number_of_pixels % image_width != 0:
        image_height += 1
    return image_height

# Inserts an RGBA pixel into the image dictionary, and appends the metadata into the read_alignment_coordinates list.
def insert_pixel(image_dictionary, read_alignment_coordinates, row, col, rgba, chromosome, ref_pos, base, methylation_value, strand, base_quality):
   
    image_dictionary[(row, col)] = rgba
    strand_symbol = '+' if strand == 255 else '-'
    read_alignment_coordinates.append((row, col, chromosome, ref_pos, base, methylation_value, strand_symbol, base_quality))

# Construct a single RGBA pixel, with base_quality and methylation_value beig set to default values.
# Clamp each channel to the range of 0–255
def construct_pixel(base, strand, methylation_value=128, base_quality=0):

    base_val = nucleotide_base_to_grayscale(base)
    strand_val = strand

    rgba = [base_val, methylation_value, base_quality, strand_val]
    
    clamped_value = []
    for channel in rgba:
        clamped_value.append(max(0, min(255, int(channel))))
    rgba = clamped_value
    return rgba

# Parses the SAM file extracting either the first or full nucleotide base/s from each aligned read.
# Extracts and stores additional metadata including the strand orientation and a placeholder methylation value.
# Encodes this information into an RGBA pixel
# Calculates the final height of the image based on the number of encoded pixels.
def parse_nucleotide_base_from_sam(sam_path, first_base_only=True, mapq_filter=None, image_width=2500):

    sam_file = open_sam_file(sam_path)
    image_dictionary = {}
    read_alignment_coordinates = []

    for read in sam_file.fetch():
        if read.is_unmapped:
            continue

        if mapq_filter is not None and read.mapping_quality < mapq_filter:
            continue

        chromosome = sam_file.get_reference_name(read.reference_id)
        strand = check_strand(read)

        # Either extract the first nucleotide from each read or extract every nucleotide base from each read within the SAM file.
        if first_base_only:
            base_index = 0
            reference_position = read.reference_start
            base_positions = [(base_index, reference_position)]
        else:
            base_positions = []
            read_length = len(read.query_sequence)
            for base_index in range(read_length):
                base_positions.append((base_index, read.reference_start + base_index))
            
            # Loop through all base in the current read.
            # Get the indexed nucleotide base in the read sequence.
            # Convert the values to a pixel and determine the position in the image.
        for base_index, ref_pos in base_positions:
            try:
                nucleotide_base = read.query_sequence[base_index].upper()
                base_quality = read.query_qualities[base_index]
                scaled_base_quality = phred_score_to_uint8(base_quality)
            except (IndexError, TypeError):
                continue  
        
            methylation_value = 128  # Default to 128 for non-methylation
            rgba = construct_pixel(nucleotide_base, strand, methylation_value, scaled_base_quality)

            image_length = len(image_dictionary)
            row, col = pixel_to_base_coordinates(image_length, image_width)

            insert_pixel(image_dictionary, read_alignment_coordinates, row, col, rgba, chromosome, ref_pos, nucleotide_base, methylation_value,strand, scaled_base_quality)

    image_height = calculate_image_height(image_dictionary, image_width)
    return image_dictionary, read_alignment_coordinates, image_height

# Parses the SAM file extracting either the first or full nucleotide base/s from each aligned read.
# Extracts and stores additional metadata including the strand orientation methylation value for the base.
# Encodes this information into an RGBA pixel
# Calculates the final height of the image based on the number of encoded pixels.

def parse_nucleotide_base_from_sam_methylation(sam_path, methylation_data, first_base_only=True, mapq_filter=None, image_width=2500):
    
    sam_file = open_sam_file(sam_path)
    image_dictionary = {}
    read_alignment_coordinates = []

    match_count = 0
    total_checked = 0

    for read in sam_file.fetch():
        if read.is_unmapped:
            continue

        if mapq_filter is not None and read.mapping_quality < mapq_filter:
            continue

        chromosome = sam_file.get_reference_name(read.reference_id)
        strand = check_strand(read)

        # Either extract the first nucleotide from each read or extract every nucleotide base from each read within the SAM file.
        if first_base_only:
            base_indices = [0]
        else:
            base_indices = range(len(read.query_sequence))

            # Loop through all base in the current read.
            # Get the indexed nucleotide base in the read sequence.
            # Convert the values to a pixel and determine the position in the image.
        for base_index in base_indices:
            try:
                nucleotide_base = read.query_sequence[base_index].upper()
                base_quality = read.query_qualities[base_index]
                scaled_base_quality = phred_score_to_uint8(base_quality)
                ref_pos = read.reference_start + base_index
            except (IndexError, TypeError):
                continue

            total_checked += 1

            # Look up methylation for this genomic position
            methylation_value = methylation_data.get((chromosome, ref_pos), 128)
            if methylation_value != 128:
                match_count += 1

            rgba = construct_pixel(nucleotide_base, strand, methylation_value, scaled_base_quality)

            image_length = len(image_dictionary)
            row, col = pixel_to_base_coordinates(image_length, image_width)

            insert_pixel(image_dictionary,read_alignment_coordinates,row, col,rgba,chromosome, ref_pos,nucleotide_base,methylation_value,strand,scaled_base_quality)

    percent_match = (match_count / total_checked * 100) if total_checked else 0
    print(f"Methylation matches: {match_count} / {total_checked} bases checked ({percent_match:.2f}%)")

    image_height = calculate_image_height(image_dictionary, image_width)
    return image_dictionary, read_alignment_coordinates, image_height

