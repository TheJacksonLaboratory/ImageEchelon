from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

DEBUG=True
PORT=9766
URL_BASE='http://localhost:9766'
URL_BASE_STATIC=URL_BASE+'/static'
URL_BASE_DOWNLOAD='http://localhost:9766'
DB_DIR='../data/db/image-echelon.db'
FULL_DESCRIPTION='Which image below more closely resembles the wild type?  Dendrites from wild type neurons evenly cover the field, while those from mutants bundle  together to form braided fascicles.  Once you click "Start Comparisons", select the image that is less fasciculated.'
HEAD_TEXT='Which image is less fasciculated?'
IMG_1_LABEL='Wild Type:'
IMG_1_TEXT='The dendrites evenly cover the entire field. GFP can fill individual dendrites, but is usually found in discrete puncta along their lengths.'
IMG_2_LABEL='Mutant:'
IMG_2_TEXT='The dendrites fasciculate, resulting in regions of dense labeling and regions of black space. GFP is less punctate in the dendrites.'
