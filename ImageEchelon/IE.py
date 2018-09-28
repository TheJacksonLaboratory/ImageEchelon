from __future__ import print_function

'''
ImageEchelon is the service module that contains all the logic for getting 
match-ups, updating rankings, and generating ranking reports.  All database 
interactions are abstracted within this module.

 Copyright (c) 2018 The Jackson Laboratory
  
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
'''

import csv
import os
import random
import sqlite3
import sys
import time

try:
    # Python 2
    from cStringIO import StringIO
except ImportError:
    # Python 3
    from io import StringIO

from elo import Rating, rate_1vs1


SQL_CREATE_TABLE_IMAGES = '''
CREATE TABLE images (
    updated text, 
    name text, 
    location text, 
    rank real,
    matchups int
)
'''

SQL_CREATE_TABLE_DETAILS = '''
CREATE TABLE details(
    name text, 
    updated text, 
    rating real
)
'''

SQL_INSERT_IMAGES = '''
INSERT 
  INTO images 
VALUES (?, ?, ?, ?, ?)
'''

SQL_SELECT_IMAGES_ALL = '''
SELECT * 
  FROM images
'''

SQL_SELECT_IMAGES_ALL_BY_RANK = '''
SELECT * 
  FROM images 
ORDER BY rank DESC 
'''

SQL_SELECT_IMAGES_BY_NAME = '''
SELECT rank, matchups 
  FROM images 
 WHERE name = ?
'''

SQL_SELECT_DETAILS_BY_NAME = '''
SELECT * 
  FROM details 
ORDER BY name, updated
'''

SQL_UPDATE_IMAGES = '''
UPDATE images 
   SET updated = ?, rank = ?, matchups = ?
 WHERE name = ?
'''

SQL_INSERT_DETAILS = '''
INSERT 
  INTO details 
VALUES (?, ?, ?)
'''


def select_matchup(db):
    '''
    Method to select the next pair of images to be compared
    :param db: contains the db directory/file name.
    :return: returns a pair of image dictionaries, with the attributes:
    name, location, updated, rating and used
    '''
    conn = sqlite3.connect(db)
    c = conn.cursor()
    images = []

    for row in c.execute(SQL_SELECT_IMAGES_ALL):
        images.append({
            'name':     row[1],
            'location': row[2],
            'updated':  row[0],
            'rating':   row[3],
            'used':     row[4]
        })
    random.seed()
    random.shuffle(images)
    pair = images[:2]

    conn.close()
    return pair


def update_ranking(db, winner, loser):
    """
    Method to update the database ranking value for both the winner and loser
    based on an ELO algorithm
    :param db: contains the db directory/file name.
    :param winner: The image selected by the user
    :param loser: The image not selected by the user
    :return:  Returns a results map containing a "winner" and a "loser" with
    their new rankings.  Rankings include columns: name, updated, rating,
    matchups
    """
    #  Set up for sqlite db
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute(SQL_SELECT_IMAGES_BY_NAME, (winner, ))
    win_row = c.fetchone()
    win_rank = win_row[0]
    win_match = win_row[1] + 1
    win_rating = Rating(win_rank)

    c.execute(SQL_SELECT_IMAGES_BY_NAME, (loser, ))
    lose_row = c.fetchone()
    lose_rank = lose_row[0]
    lose_match = lose_row[1] + 1
    lose_rating = Rating(lose_rank)

    # update ratings
    win_rating, lose_rating = rate_1vs1(win_rating, lose_rating)
    now = time.strftime('%Y%m%d_%H%M%S%MS', time.localtime())

    c.execute(SQL_UPDATE_IMAGES, (now, win_rating, win_match, winner))
    c.execute(SQL_INSERT_DETAILS, (winner, now, win_rating))

    c.execute(SQL_UPDATE_IMAGES, (now, lose_rating, lose_match, loser))
    c.execute(SQL_INSERT_DETAILS, (loser, now, lose_rating))

    conn.commit()
    conn.close()

    return {'winner': {'name': winner,
                       'updated': now,
                       'rating': win_rating,
                       'matchups': win_match},
            'loser': {'name': loser,
                      'updated': now,
                      'rating': lose_rating,
                      'matchups': lose_match}}


def get_ranking_report(db):
    '''
    Generates the CSV ranking report file
    :param config: contains the db directory/file name.
    :return: CSV file with the columns: image, rating, match-ups
    '''
    conn = sqlite3.connect(db)
    c = conn.cursor()
    query_results = c.execute(SQL_SELECT_IMAGES_ALL_BY_RANK)

    csvfile = StringIO()

    headers = [
        'image',
        'rating',
        'match-ups'
    ]
    rows = []
    for row in query_results:
        rows.append(
            {
                'image': row[1],
                'rating': row[3],
                'match-ups': row[4]
            }
        )
    writer = csv.DictWriter(csvfile, headers)
    writer.writeheader()
    for row in rows:
        writer.writerow(
            dict(
                (k, v.encode('utf-8') if type(v) is unicode else v) for k, v in row.iteritems()
            )
        )
    csvfile.seek(0)
    conn.close()

    return csvfile


def get_detail_report(db):
    '''
    Generates the CSV detail report file
    :param config: contains the db directory/file name.
    :return: CSV file with the columns: image, date, rating
    '''
    conn = sqlite3.connect(db)
    c = conn.cursor()
    query_results = c.execute(SQL_SELECT_DETAILS_BY_NAME)

    csvfile = StringIO()

    headers = ['image', 'date', 'rating']
    rows = []
    for row in query_results:
        rows.append({
            'image': row[0],
            'date': row[1],
            'rating': row[2]
        })
    writer = csv.DictWriter(csvfile, headers)
    writer.writeheader()
    for row in rows:
        writer.writerow(
            dict(
                (k, v.encode('utf-8') if type(v) is unicode else v) for k, v in row.iteritems()
            )
        )
    csvfile.seek(0)
    conn.close()

    return csvfile


def init(db, image_dir):
    print(db)
    print(image_dir)
    if os.path.exists(db):
        print('{} exists.  Please remove before proceeding.')
        sys.exit(1)

    if not os.path.isdir(image_dir):
        print('Image directory {} cannot be found.'.format(image_dir))
        sys.exit(1)

    conn = sqlite3.connect(db)

    c = conn.cursor()

    # Create tables
    c.execute(SQL_CREATE_TABLE_IMAGES)
    c.execute(SQL_CREATE_TABLE_DETAILS)

    print('Tables created...')

    for file in os.listdir(image_dir):
        extension = os.path.splitext(file)[1][1:]
        if extension in ['png', 'jpg', 'jpeg']:
            now = time.strftime('%Y%m%d_%H%M%S%MS', time.localtime())
            fullpath = os.path.abspath(os.path.join(image_dir, file))
            c.execute(SQL_INSERT_IMAGES, (now, file, fullpath, 1200.0, 0))
        else:
            print('Skipping file {}, extension not supported.'.format(file))

    # Save (commit) the changes
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()


def stats(db):
    fd = open('rankings_report.tsv', 'w')
    dd = open('detail_results.tsv', 'w')
    conn = sqlite3.connect(db)
    c = conn.cursor()
    fd.write('image\trating\tmatch-ups\n')

    for row in c.execute(SQL_SELECT_IMAGES_ALL_BY_RANK):
        fd.write('{0}\t{1:.1f}\t{2}\n'.format(row[1], row[3], row[4]))

    dd.write('name\tupdated\trating\n')

    for row in c.execute(SQL_SELECT_DETAILS_BY_NAME):
        dd.write('{0}\t{1}\t{2:.1f}\n'.format(row[0], row[1], row[2]))

    conn.close()
    fd.close()
    dd.close()

