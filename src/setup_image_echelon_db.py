#!/usr/bin/env python
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
"""
setup_image_echelon_db.py
March 9, 2015
Dave Walton - dave.walton@jax.org

Program intended for setting up the database based on the contents of an
image directory.

usage:
setup_image_echelon_db.py 

Config:
    setup_image_echelon_db.py uses a configuration file config.json which contains:
      "image_path":"../data/test-data/",
      "db_dir": "../data/db/",
      "db_file": "image-echelon.db"  
    You will want to update image_path to be the location of your image directory

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
    with open('src/config.json') as json_data_file:
        config = json.load(json_data_file)
    print(config)
    image_path = 'data/images/'
    if 'image_path' in config:
        image_path = config['image_path']
    print(image_path)
    db_dir = 'data/db/'
    if 'db_dir' in config:
        db_dir = config['db_dir']
    print(db_dir)
    if not os.path.isdir(db_dir):
        os.mkdir(db_dir)

    db_file = 'image-echelon.db'
    if 'db_file' in config:
        db_file = config['db_file']
    print(db_file)

    if not os.path.isdir(image_path):
        print("Image directory %s cannot be found", image_path)
        sys.exit(1)
    image_dir = image_path
    print(image_dir)

    conn = sqlite3.connect(os.path.join(db_dir, db_file))

    c = conn.cursor()

    c.execute('''drop table if exists images''')
    c.execute('''drop table if exists details''')
    print("tables dropped...")

    # Create tables
    c.execute('''CREATE TABLE images
                 (updated text, name text, location text, rank real,
                 matchups int)''')
    c.execute('''CREATE TABLE details
                 (name text, updated text, rating real)''')
    print("tables created...")

    # Currently only works with PNG images.  Should add regex to pick up
    # JPG/JPEG as well.
    for file in os.listdir(image_dir):
        extension = os.path.splitext(file)[1][1:]
        if extension in ["png","jpg","jpeg"]:
            now = time.strftime("%Y%m%d_%H%M%S%MS", time.localtime())
            fullpath = os.path.abspath(os.path.join(image_dir, file))

            c.execute("INSERT INTO images VALUES ('" + now + "', '" + file + "', '"
                      + fullpath + "', 1200.0, 0)")
        else:
            print("Skipping file {0} as file extension not supported.  Supported: {1}, {2}, {3}.".format(file, 'png', 'jpg', 'jpeg'))

    # Save (commit) the changes
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()


if __name__ == "__main__":
    main()
