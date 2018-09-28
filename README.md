# Image Echelon

## Overview

Image Echelon is a tool to quantify images where meaningful differences are 
discernible by eye, but difficult to quantify using traditional methods.  It 
was developed to quantify neuronal fasciculation in microscopy images, but can
be used to rank images based on any qualitative criteria.  Classical methods 
ask observers to score an image in isolation along a scale (e.g., 1-5), which 
can be difficult to control between observers, especially in a highly variable 
data set.  Image Echelon asks observers to compare two images and pick a 
“winner” and a “loser” along some criteria, an easier and more reliable task.

Users are presented with a landing page containing a written description of the
phenomenon to be quantified, along with two example images: one clear “winner” 
and one clear “loser”.  The software will then present two images randomly 
selected from the set, and the user is instructed to click on the “winner”.  
Immediately after clicking, a new random pair is presented.  This continues 
until the user terminates the program.  After every iteration of these forced 
choice head-to-head match-ups, the score for each image is updated according to
an Elo algorithm.  This algorithm adds to the “winner” score and deducts from 
the “loser” score.  The score held by each image entering the match-up 
determines the amount of points gained or lost: upsets (a low score image wins 
over a high score image) cause a greater point exchange than the converse.  
This results in efficient ranking of the images long before every potential 
head-to-head match-up occurs.  At any time, the researcher can extract a report
in .csv format listing each image filename, along with its current score and 
number of match-ups, as well as a detailed report listing the result of every 
match-up.  This detailed report lists the filename and score of both images 
after the match-up with the exact time the match-up was performed.

## In Literature

In the paper Garret et al, Replacing the PDZ-interacting C-termini of DSCAM and
DSCAML1 with epitope tags causes different phenotypic severity in different cell
populations, [eLife](https://elifesciences.org/articles/16144) 2016;5:e16144 
DOI: [10.7554/eLife.16144](https://doi.org/10.7554/eLife.16144) 
PMID: [27637097](https://www.ncbi.nlm.nih.gov/pubmed/27637097) 
PMCID: [PMC5026468](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5026468/), 
ImageEchelon was the software used for the ELO scoring mentioned under the 
Materials and methods section.
 
## Installation/Setup

In order to use Image Echelon, you'll need to clone this repository to your 
server.  An assumption is being made that you are either running from a linux 
environment (we use CentOS) or you are running on Mac OS X. We highly recommend 
running Image Echelon from a Python virtual environment.  Image Echelon was 
implemented using Python 2 and 3.  Before installing any other libraries
you should make sure you have Python 2.7.9 or better (I'm currently running 
Python 3.4).  The python package manager *pip* is included with this by default.
Next you'll want to install *virtualenv*.

```
pip install virtualenv
```

Once installed you'll want to create a specific virtual environment for 
Image Echelon, like:

```
virtualenv ImageEchelon
```

This will create a new working directory named *ImageEchelon* (or whatever you 
chose to call the virtual environment). You'll then want to activate the virtual
environment.

```
. ImageEchelon/bin/activate
```

Once your virtualenv is activated you will now use *pip* to install the required
Python libraries.  In the root directory of the project there is a 
*requirements.txt* file.  To install the required packages simply run:

```
pip install -r requirements.txt
```

### Configuration of ImageEchelon
The intent of ImageEchelon is to allow you to provide the service for comparing 
a set of images of your choosing.  With that the text on the page will need to 
vary based on the image set.

Image Echelon uses an SQLite database that you will want to set up next.  In 
order to setup a new database, first you need a directory of image files where 
the name of each file, prior to the extension (".png", "*.jpg", "*.jpeg") 
represents the name of the image.  
```
# Image and Database configuration
DB='example/image-echelon.db'
IMAGE_PATH='example/images'

# Web Configuration
DEBUG=True
PORT=9767

# Text configuration
FULL_DESCRIPTION='Which image below more closely resembles the wild type?  Dendrites from wild type neurons evenly cover the field, while those from mutants bundle  together to form braided fascicles.  Once you click "Start Comparisons", select the image that is less fasciculated.'
HEAD_TEXT='Which image is less fasciculated?'
IMG_1_LABEL='Wild Type:'
IMG_1_TEXT='The dendrites evenly cover the entire field. GFP can fill individual dendrites, but is usually found in discrete puncta along their lengths.'
IMG_2_LABEL='Mutant:'
IMG_2_TEXT='The dendrites fasciculate, resulting in regions of dense labeling and regions of black space. GFP is less punctate in the dendrites.'
```

An example configuration file and image directory is located under the *example*
directory.  

### Configuring and Setting up the database

You will need to change *IMAGE_PATH* to contain the location of your directory 
of images.  You will also need to change *DB* to contain the location of where
you would like your database to reside.

  
Once you have your configuration file you will need to set an environment 
variable called *IMAGE_ECHELON_SETTINGS* that will contain the location of the
file. Than issue the following command: 
```
IMAGE_ECHELON_SETTINGS=/etc/ImageEchelon.cfg python application.py initdb
```

You can reset the scores in the database at anytime by deleting the database and
re-running the above command. Note that this will eliminate all previous scores 
collected.

The data base columns created in image-echelon.db are include
```
    updated     text    last date record updated
    name        text    name of file
    location    text    full path to file
    rank        real    current rating score
    matchups    int     number of match-ups involving this image
```

### Configuring page text

The default text is specific to the the fasiculation of dendrites between wild 
type and mutant neurons.  Obviously this doesn't meet the needs of all image 
sets.

The configuration file contains fields that can be configured.  These fields 
include:
```
FULL_DESCRIPTION    -> This is the description under the ImageEchelon header.
HEAD_TEXT           -> This is the question text directly about the pair of images.
IMG_1_LABEL         -> The label below the example image on the left.
IMG_1_TEXT          -> The description below the example image on the left.
IMG_2_LABEL         -> The label below the example image on the right.
IMG_2_TEXT          -> The description below the example image on the right.
```

### Configuring and Launching the web-application
To configure your web-application you should edit the configuration file:
```
DEBUG=True
PORT=9766
```

The simplest way to launch the web application is as Python Flash application.  From the src directory use the command:
```
IMAGE_ECHELON_SETTINGS=/etc/ImageEchelon.cfg python application.py web
```

The application could also be run out of a separate web-server, but I will not 
detail how to do that here.

### Statistics and Reporting

Once you have collected data, you can access your results from the following 
two URLs:
```
http://localhost:9766/report
http://localhost:9766/detail
```

The first report returns a csv file containing the image file name, the rating
and the number of match-ups that image was involved in. The second report 
returns the image file name, the last update date and the rating.

You could also run via the command line:

```
IMAGE_ECHELON_SETTINGS=/etc/ImageEchelon.cfg python application.py reports
```

Two files will be created: `rankings_report.tsv` and `detail_results.tsv`.

