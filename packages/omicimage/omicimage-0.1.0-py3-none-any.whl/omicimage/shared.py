# Shared constants and functions.

MAX_BASE_QUALITY = 40

# Maps the nucleotide bases to 8-bit grayscale values.
nucleotide_BASE_TO_GRAYSCALE_MAPPER = {
    
    'A': 32,
    'T': 96,
    'C': 160,
    'G': 224,
    'N': 255
}

# Convert a Phred quality score to an 8-bit integer (0–255), 
# Clipping is used at the maximum Phred Score. 
def phred_score_to_uint8(phred_score, max_phred_score=MAX_BASE_QUALITY):

    if phred_score is None:
        return 0
    if phred_score < 0:
        phred_score = 0
    if phred_score > max_phred_score:
        phred_score = max_phred_score
    return int(round(255.0 * phred_score / max_phred_score))

# Converts a nucleotide base to its corresponding grayscale value.
# Defaults to 255 for unknown or invalid bases.
def nucleotide_base_to_grayscale(base):

    return nucleotide_BASE_TO_GRAYSCALE_MAPPER.get(base, 255)

# Checks if the read is on the reverse strand.
# Currently strand information is stored in the alpha channel: 0 for reverse, 255 for forward.
def check_strand(read):

    return 0 if read.is_reverse else 255

# Calculates the row and column in order to convert the pixel index back to its nucleotide position.
def pixel_to_base_coordinates(pixel_index, image_width):

    calculated_row = pixel_index // image_width
    calculated_column = pixel_index % image_width
    return calculated_row, calculated_column

