# Image Echelon

## Overview

Image Echelon is a tool to quantify images where meaningful differences are discernible by eye, but difficult to
quantify using traditional methods.  It was developed to quantify neuronal fasciculation in microscopy images, but can
be used to rank images based on any qualitative criteria.  Classical methods ask observers to score an image in
isolation along a scale (e.g., 1-5), which can be difficult to control between observers, especially in a highly
variable data set.  Image Echelon asks observers to compare two images and pick a “winner” and a “loser” along some
criteria, an easier and more reliable task.

Users are presented with a landing page containing a written description of the phenomenon to be quantified, along with
two example images: one clear “winner” and one clear “loser”.  The software will then present two images randomly
selected from the set, and the user is instructed to click on the “winner”.  Immediately after clicking, a new random
pair is presented.  This continues until the user terminates the program.  After every iteration of these forced choice
head-to-head match-ups, the score for each image is updated according to an Elo algorithm.  This algorithm adds to the
“winner” score and deducts from the “loser” score.  The score held by each image entering the match-up determines the
amount of points gained or lost: upsets (a low score image wins over a high score image) cause a greater point exchange
than the converse.  This results in efficient ranking of the images long before every potential head-to-head match-up
occurs.  At any time, the researcher can extract a report in .csv format listing each image filename, along with its
current score and number of match-ups, as well as a detailed report listing the result of every match-up.  This detailed
report lists the filename and score of both images after the match-up with the exact time the match-up was performed.

## In Literature

In the paper Garret et al, Replacing the PDZ-interacting C-termini of DSCAM and DSCAML1 with epitope tags causes different phenotypic severity in different cell populations, [eLife](https://elifesciences.org/articles/16144) 2016;5:e16144 DOI: [10.7554/eLife.16144](https://doi.org/10.7554/eLife.16144) PMID: [27637097](https://www.ncbi.nlm.nih.gov/pubmed/27637097) PMCID: [PMC5026468](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5026468/), 
ImageEchelon was the software used for the ELO scoring mentioned under the Materials and methods section.
 
## Installation/Setup

In order to use Image Echelon, you'll need to clone this repository to your server.  An assumption is being made that you
are either running from a linux environment (we use CentOS) or you are running on Mac OS X. We highly recommend running Image Echelon
from a Python virtual environment.  Image Echelon was implemented using Python 2. The most recent version has been 
upgraded to work with Python 3.  I found that the ELO library will break with Python 3.9, so I'm recommending 
Python 3.7.11 (works both on the Mac and CentOS. One additional thing I discovered on CENTOS was for it to work with
sqlite, I needed to install *libsqlite3x-devel* before installing python.  I used the following command:

```
sudo yum install libsqlite3x-devel
```

Next you'll want to install *virtualenv*.  From the project root directory I ran:

```
python3.7 -m venv imageech-env
```

Once installed with virtual env created I loaded it with:

```
source imageech-env/bin/activate
```

Once the virtualenv is activated, using *pip* install the required Python libraries.  In the root directory
of the project there is a *requirements.txt* file.  To install the required packages simply run:

```
pip install -r requirements.txt
```

### Setting up a new database
Image Echelon uses an SQLite database that you will want to set up next.  In order to setup a new database, first you need
a directory of png files where the name of each file, prior to the ".png" represents the name of the image.  You will then
need to update the src/config.json file which has the following content:

```
{
  "image_path":"../data/test-data/",
  "db_dir": "../data/db/",
  "db_file": "image-echelon.db"
}
```

You will need to changet *image_path* to contain the location of your directory of images. Once that is set you need to generate the database using the program *setup_image_echelon_db.py*.  Usage for this program is below (not it needs to be run from the *src* directory): 
```
python src/setup_image_echelon_db.py 
```

Once your database has been created, you will also want to either create a symbolic link from *src/static/images/data* to
the actual folder where the original images are housed, or copy the images to that location.  This is the where the web
interface will find the images to pull for display.

You can reset the scores in the database at anytime by re-running *setup_image_echelon_db.py*.  Note that this will
eliminate all previous scores collected

The database columns created in image-echelon.db are include
```
    updated     text    last date record updated
    name        text    name of file
    location    text    full path to file
    rank        real    current rating score
    matchups    int     number of match-ups involving this image
```

### Configuring page text
The intent of ImageEchelon is to allow you to provide the service for comparing a set of images of your choosing.  With that the text on the page will need to vary based on the image set.  The default text is specific to the the fasiculation of dendrites between wild type and mutant neurons.  Obviously this doesn't meet the needs of all image sets.
The `config.py` file contains fields that can be configured.  These fields include:
```
FULL_DESCRIPTION    -> This is the description under the ImageEchelon header.
HEAD_TEXT           -> This is the question text directly about the pair of images.
IMG_1_LABEL         -> The label below the example image on the left.
IMG_1_TEXT          -> The description below the example image on the left.
IMG_2_LABEL         -> The label below the example image on the right.
IMG_2_TEXT          -> The description below the example image on the right.
```

### Replace example images
The initial page in ImageEchelon has two example images with description that will appear below them.  You will need to provide example images to use for this page to provide the user with an example of the kind of difference they are looking for.
These images can be found in `src/static/images`.  The one that will appear on the left is named `wildtype.png` the one that will appear on the right is named `mutant.png`. 


### Launching the web-application
To configure your web-application you should edit the config.py file:
```
DEBUG=True
PORT=9766
URL_BASE='http://localhost:9766'
URL_BASE_STATIC=URL_BASE+'/static'
URL_BASE_DOWNLOAD='http://localhost:9766'
```

The simplest way to launch the web application is as Python Flash application.  From the src directory use the command:
```
    python application.py
```

The application could also be run out of a separate web-server, but I will not detail how to do that here.

Once you have collected data, you can access your results from the following two URLs:
```
http://localhost:9766/report
http://localhost:9766/detail
```

The first report returns a csv file containing the image file name, the rating and the number of match-ups that image was involved in.
The second report returns the image file name, the last update date and the rating.
