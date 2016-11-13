#H1  Image Echelon

#H2  Overview

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
head-to-head matchups, the score for each image is updated according to an Elo algorithm.  This algorithm adds to the
“winner” score and deducts from the “loser” score.  The score held by each image entering the matchup determines the
amount of points gained or lost: upsets (a low score image wins over a high score image) cause a greater point exchange
than the converse.  This results in efficient ranking of the images long before every potential head-to-head matchup
occurs.  At any time, the researcher can extract a report in .csv format listing each image filename, along with its
current score and number of matchups, as well as a detailed report listing the result of every matchup.  This detailed
report lists the filename and score of both images after the matchup with the exact time the matchup was performed.

#H2  Installation/Setup

To use Image Echelon, you must first setup a database.  Create a "data" folder and place the images to be compared there.
Note: at this time the program only supports "png" format images.  You must need to
direct Image Echelon to that folder somehow.  I get my reports from levon.jax.org/report or levon.jax.org/detail , but
that probably won’t work for you.  You can reset the scores by running setup_image_echelon_db.py, but we probably need to
change that name.  Okay, I don’t know how to do this.

Setting up a new database
In order to setup a new database, first you need a directory of png files where the name of each file, prior to the ".png" represents the name of the image.

Then you run the script data/db/setup_image_echelon_db.py

After you run the script update the src/static/images/data symbolic link to point to the new image directory you used in setup_image_echelon_db.py.

Instructions for running this (from the script header comment) are as follows:

usage:
setup_image_echelon_db.py [OPTIONS] -i <image directory>

OPTIONS:
    -i, --image-dir the directory where images to be loaded in db reside
    -h, --help      this message

Generates a database named image-echelon.db

DB Columns include:
    updated text    last date record updated
    name text       name of file
    location text   full path to file
    rank real       current rating score
    matchups int    number of matchups involving this image

The web application assumes the database to be found in and named: (from the src dir) "../data/db/image_echelon.db"