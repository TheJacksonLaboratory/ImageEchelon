#!/usr/bin/env python
from __future__ import print_function

"""
setup_image_echelon_db.py
March 9, 2015
Dave Walton - dave.walton@jax.org

Program intended for setting up the database based on the contents of an
image directory.

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

  Copyright (c) 2015 The Jackson Laboratory

  This is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This software is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this software.  If not, see <http://www.gnu.org/licenses/>.


"""

import os
import sqlite3
import sys
import time
import json

SOURCE_DIR = os.path.dirname(os.path.realpath(__file__))


def main():
    with open('config.json') as json_data_file:
        config = json.load(json_data_file)
    image_path = '../data/images/'
    if config.has_key('image_path'):
        image_path = config['image_path']
    db_dir = '../data/db/'
    if config.has_key('db_dir'):
        db_dir = config['db_dir']
    if not os.path.isdir(db_dir):
        os.mkdir(db_dir)
    db_file = 'image-echelon.db'
    if config.has_key('db_file'):
        db_file = config['db_file']

    if not os.path.isdir(image_path):
        print("Image directory %s cannot be found", image_path)
        sys.exit(1)
    image_dir = image_path

    conn = sqlite3.connect(os.path.join(db_dir, db_file))

    c = conn.cursor()

    c.execute('''drop table if exists images''')
    c.execute('''drop table if exists details''')

    # Create tables
    c.execute('''CREATE TABLE images
                 (updated text, name text, location text, rank real,
                 matchups int)''')
    c.execute('''CREATE TABLE details
                 (name text, updated text, rating real)''')

    # Currently only works with PNG images.  Should add regex to pick up
    # JPG/JPEG as well.
    for file in os.listdir(image_dir):
        if file.lower().endswith(".png"):
            now = time.strftime("%Y%m%d_%H%M%S%MS", time.localtime())
            fullpath = os.path.abspath(os.path.join(image_dir, file))

            c.execute("INSERT INTO images VALUES ('" + now + "', '" + file + "', '"
                      + fullpath + "', 1200.0, 0)")

    # Save (commit) the changes
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()


if __name__ == "__main__":
    main()