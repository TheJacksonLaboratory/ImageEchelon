# Image and Database configuration
DB='example/image-echelon.db'
IMAGE_PATH='example/images'

# Web Configuration
DEBUG=True
PORT=9767

# Text configuration
FULL_DESCRIPTION='Which image below more closely resembles the wild type?  Dendrites from wild type neurons evenly cover the field, while those from mutants bundle  together to form braided fascicles.  Once you click "Start Comparisons", select the image that is less fasciculated.'
HEAD_TEXT='Which image is less fasciculated?'

# Set to 0 to be full size images
IMG_1_WIDTH=400
IMG_1_HEIGHT=400
IMG_1_LABEL='Wild Type:'
IMG_1_TEXT='The dendrites evenly cover the entire field. GFP can fill individual dendrites, but is usually found in discrete puncta along their lengths.'
IMG_1_DEFAULT='example/1.png'

# Set to 0 to be full size images
IMG_2_WIDTH=400
IMG_2_HEIGHT=400
IMG_2_LABEL='Mutant:'
IMG_2_TEXT='The dendrites fasciculate, resulting in regions of dense labeling and regions of black space. GFP is less punctate in the dendrites.'
IMG_2_DEFAULT='example/2.png'
