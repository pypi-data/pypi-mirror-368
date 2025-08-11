import os
from datetime import datetime
from omicimage.image_encoder import create_rgba_array, convert_rgba_array_to_image

# Writes the read alignment coordinates associated with each nucleotide base (pixel)
# read alignment position is a list tuples wihch contain - (row, col, chromosome, ref_pos, nucleotide_base, methylation_value, strand, base quality).
def write_read_alignment_coordinates(read_alignment_coordinates, path):
    
    with open(path, "w") as coordinates_file:
        coordinates_file.write("row\tcol\tchrom\tref_pos\tbase\tmethylation\tstrand\tbase_quality\n")
        for read_alignment in read_alignment_coordinates:
            coordinates_file.write("\t".join(map(str, read_alignment)) + "\n")

# Writes the height and width metadata on the generated image.
def write_image_metadata(path, image_width, image_height):

    with open(path, "w") as metadata_file:
        metadata_file.write(f"width: {image_width}\nheight: {image_height}\n")

# Creates an output directory and prefix the name with a user defined label and timestamp.
# The timestamp format is predefined.
def make_timestamped_output_directory(prefix):

    time_string = "Date%d_%m_%y_Time%H%M"
    timestamp = datetime.now().strftime(time_string)
    timestamp_prefix = f"{prefix}_{timestamp}"

    output_directory = os.path.join("output", timestamp_prefix)
    os.makedirs(output_directory, exist_ok=True)
    return output_directory

# Executes the full image generation pipeline using the parsed SAM data.
# Calls the specified parsing function, which returns the image dictionary, read alignment coordinates and calculated image height. 
# Construct a NumPy array which is the RGBA data for the image based on the information in the image_dictionary.
# Saves the image, read alignment position and metadata for interpreting and converting the 
# image back to the original reads in the output folder.
def run_rgba_pipeline(parsing_function, sam_path, parsing_arguments, image_width, output_directory):
    
    image_dictionary, read_alignment_coordinates, image_height = parsing_function(sam_path, *parsing_arguments, image_width=image_width)

    image_array = create_rgba_array(image_dictionary, image_height, image_width)

    convert_rgba_array_to_image(image_array, os.path.join(output_directory, "image.png"))
    write_read_alignment_coordinates(read_alignment_coordinates, os.path.join(output_directory, "readalignmentcoordinates.tsv"))
    write_image_metadata(os.path.join(output_directory, "metadata"), image_width, image_height)
