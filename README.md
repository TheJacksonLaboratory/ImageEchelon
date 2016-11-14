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

## Installation/Setup

In order to use Image Echelon, you'll need to clone this repository to your server.  An assumption is being made that you
are either running from a linux environment (we use CentOS) or you are running on Mac OS X. We highly recommend running Image Echelon
from a Python virtual environment.  Image Echelon was implemented using Python 2.  Before installing any other libraries
you should make sure you have Python 2.7.9 or better (I'm currently running Python 2.7.12).  The python package manager
*pip* is included with this by default.  Next you'll want to install *virtualenv*.

'''
pip install virtualenv
'''

Once installed you'll want to create a specific virtual environment for Image Echelon, like:

'''
virtualenv ImageEchelon
'''

This will create a new working directory named *ImageEchelon* (or whatever you chose to call the virtual environment).
You'll then want to activate the virtual environment.

'''
. ImageEchelon/bin/activate
'''

Once your virtualenv is activated you will now use *pip* to install the required Python libraries.  In the root directory
of the project there is a *requirements.txt* file.  To install the required packages simply run:

'''
pip install -r requirements.txt
'''

### Setting up a new database
Image Echelon uses an SQLite database that you will want to set up next.  In order to setup a new database, first you need
a directory of png files where the name of each file, prior to the ".png" represents the name of the image.  You will then
generate the database using the program *setup_image_echelon_db.py*.  Usage for this program is below, and also available by typing
'''
    setup_image_echelon_db.py -h
'''

You will need to direct Image Echelon to the image folder you created using the -i (or --image-dir) option.

Once your database has been created, you will also want to either create a symbolic link from *src/static/images/data* to
the actual folder where the original images are housed, or copy the images to that location.  This is the where the web
interface will find the images to pull for display.

You can reset the scores in the database at anytime by re-running *setup_image_echelon_db.py*.  Note that this will
eliminate all previous scores collected

Instructions for running *setup_image_echelon_db.py* are as follows:
'''
usage:
    setup_image_echelon_db.py [OPTIONS]

OPTIONS:
    -i, --image-dir the directory where images to be loaded in db reside
    -h, --help      this message

Generates a database named image-echelon.db

DB Columns include:
    updated     text    last date record updated
    name        text    name of file
    location    text    full path to file
    rank        real    current rating score
    matchups    int     number of match-ups involving this image
'''

The locations of the image directory, the database directory and the database file name, can also be controlled by providing a
config.json file in the same directory as the program.  Example content for config.json includes:

'''
{
  "image_path":"../data/test-set/",
  "db_dir": "../data/db/",
  "db_file": "image-echelon.db"
}
'''

### Launching the web-application
To configure your web-application you should edit the config.py file:
'''
DEBUG=True
PORT=9766
URL_BASE='http://localhost:9766'
URL_BASE_STATIC=URL_BASE+'/static'
URL_BASE_DOWNLOAD='http://localhost:9766'
'''

The simplest way to launch the web application is as Python Flash application.  From the src directory use the command:
'''
    python application.py
'''

The application could also be run out of a separate web-server, but I will not detail how to do that here.

Once you have collected data, you can access your results from the following two URLs:
'''
http://localhost:9766/report
http://localhost:9766/detail
'''

The first report returns a csv file containing the image file name, the rating and the number of match-ups that image was involved in.
The second report returns the image file name, the last update date and the rating.