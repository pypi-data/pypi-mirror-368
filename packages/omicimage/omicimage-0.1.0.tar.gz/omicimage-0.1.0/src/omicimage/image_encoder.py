import numpy as np
from PIL import Image

# Takes the separate RGBA values and combines them into a single list of four elements.
def encode_pixel_rgba(base_val, meth_val, coverage_val, strand_val):
    return [base_val, meth_val, coverage_val, strand_val]

# Creates a NumPy array which respresents the image in RGBA format, the value 4 corresponds to the four color channels: Red, Green, Blue, and Alpha.
# The height and width correspond to the number of image rows and columns.
# Each "rgba" value is a list which consist of four elements [R, G, B, A]
# Returns a 3D array which respresents the full image as a Numpy array.
def create_rgba_array(image_dictionary, height, width):

    image_array = np.zeros((height, width, 4), dtype=np.uint8)

    for (row, col), rgba in image_dictionary.items():
        image_array[row, col] = rgba
    return image_array

# Convert the RGBA array into the image using the python PIL library.
def convert_rgba_array_to_image(img_array, output_path):
   
    img = Image.fromarray(img_array, mode="RGBA")
    img.save(output_path)
