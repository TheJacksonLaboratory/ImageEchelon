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
    image_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    updated TEXT NOT NULL, 
    rating REAL NOT NULL,
    num_wins INTEGER NOT NULL,
    num_losses INTEGER NOT NULL,
    PRIMARY KEY (image_id),
    CONSTRAINT images_ix1 UNIQUE (name)
)
'''

SQL_CREATE_TABLE_MATCHES = '''
CREATE TABLE matches (
    match_id INTEGER NOT NULL,
    winner_image_id INTEGER NOT NULL, 
    winner_rating_before REAL NOT NULL, 
    winner_rating_after REAL NOT NULL, 
    loser_image_id INTEGER NOT NULL,
    loser_rating_before REAL NOT NULL, 
    loser_rating_after REAL NOT NULL,
    updated TEXT NOT NULL, 
    PRIMARY KEY (match_id),
    FOREIGN KEY (winner_image_id) REFERENCES images(image_id),
    FOREIGN KEY (loser_image_id) REFERENCES images(image_id)
)
'''

SQL_INSERT_IMAGES = '''
INSERT 
  INTO images 
VALUES (NULL, ?, ?, ?, ?, ?, ?)
'''

SQL_SELECT_IMAGES_ALL = '''
SELECT * 
  FROM images
'''

SQL_SELECT_IMAGES_PAIR = '''
SELECT * 
  FROM images 
 ORDER BY RANDOM() LIMIT 2
'''

SQL_SELECT_IMAGES_ALL_BY_RANK = '''
SELECT * 
  FROM images 
ORDER BY num_wins DESC 
'''

SQL_SELECT_IMAGE_BY_ID = '''
SELECT * 
  FROM images 
 WHERE image_id = ?
'''

SQL_SELECT_MATCHES_ALL = '''
SELECT m.match_id, iw.name winner_name, m.winner_rating_after, il.name loser_name, m.loser_rating_after, m.updated match_time
  FROM matches m, images iw, images il
 WHERE m.winner_image_id = iw.image_id
   AND m.loser_image_id = il.image_id
 ORDER BY m.match_id
'''

SQL_UPDATE_IMAGE_WIN = '''
UPDATE images 
   SET updated = ?, rating = ?, num_wins = ?
 WHERE image_id = ?
'''

SQL_UPDATE_IMAGE_LOSS = '''
UPDATE images 
   SET updated = ?, rating = ?, num_losses = ?
 WHERE image_id = ?
'''

SQL_INSERT_MATCH = '''
INSERT 
  INTO matches
VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)
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

    for row in c.execute(SQL_SELECT_IMAGES_PAIR):
        images.append({
            'id': row[0],
            'name': row[1],
            'location': row[2],
            'updated': row[3],
            'rating': row[4],
            'num_wins': row[5],
            'num_losses': row[6]
        })

    conn.close()
    return images


def update_ranking(db, winner, loser):
    """
    Method to update the database ranking value for both the winner and loser
    based on an ELO algorithm

    :param db: contains the db directory/file name.
    :param winner: The image id selected by the user
    :param loser: The image id not selected by the user
    :return:  Returns a results map containing a "winner" and a "loser" with
    their new rankings.  Rankings include columns: name, updated, rating,
    matchups
    """
    #  Set up for sqlite db
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute(SQL_SELECT_IMAGE_BY_ID, (winner,))
    win_row = c.fetchone()
    win_num_matchups = win_row['num_wins'] + 1
    win_rating = Rating(win_row['rating'])

    c.execute(SQL_SELECT_IMAGE_BY_ID, (loser,))
    lose_row = c.fetchone()
    lose_num_matchups = lose_row['num_losses'] + 1
    lose_rating = Rating(lose_row['rating'])

    # update ratings
    win_rating_new, lose_rating_new = rate_1vs1(win_rating, lose_rating)
    now = time.strftime('%Y%m%d_%H%M%S%MS', time.localtime())

    c.execute(SQL_INSERT_MATCH, (winner, win_row['rating'], win_rating_new,
                                 loser, lose_row['rating'], lose_rating_new,
                                 now))

    c.execute(SQL_UPDATE_IMAGE_WIN, (now, win_rating_new, win_num_matchups, winner))
    c.execute(SQL_UPDATE_IMAGE_LOSS, (now, lose_rating_new, lose_num_matchups, loser))

    conn.commit()
    conn.close()

    return {'winner': {'id': winner,
                       'updated': now},
            'loser': {'id': loser,
                      'updated': now}}


def get_ranking_report(db, delimiter=','):
    '''
    Generates the CSV ranking report file

    :param db: contains the db directory/file name.
    :param delimiter: delimiter between fields
    :return: CSV file with the columns: image, rating, match-ups
    '''
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    query_results = c.execute(SQL_SELECT_IMAGES_ALL_BY_RANK)

    csvfile = StringIO()

    writer = csv.writer(csvfile, delimiter=delimiter)
    writer.writerow(['image', 'rating', 'matches', 'wins', 'losses'])

    for row in query_results:
        writer.writerow([row['name'], row['rating'],
                         row['num_wins'] + row['num_losses'],
                         row['num_wins'], row['num_losses']])

    csvfile.seek(0)
    conn.close()

    return csvfile


def get_detail_report(db, delimiter=','):
    '''
    Generates the CSV detail report file

    :param db: contains the db directory/file name.
    :param delimiter: delimiter between fields
    :return: CSV file with the columns: image, date, rating
    '''
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    query_results = c.execute(SQL_SELECT_MATCHES_ALL)

    csvfile = StringIO()

    writer = csv.writer(csvfile, delimiter=delimiter)

    writer.writerow(['match_number', 'winner_name', 'winner_rating', 'loser_name', 'loser_rating', 'match_time'])

    for row in query_results:
        writer.writerow([row['match_id'],
                         row['winner_name'], row['winner_rating_after'],
                         row['loser_name'], row['loser_rating_after'],
                         row['match_time']])

    csvfile.seek(0)
    conn.close()

    return csvfile


def init(db, image_dir):
    '''
    Generates the ImageEchelon database
    :param db: contains the db directory/file name.
    :param image_dir: directory to search for images
    :return: CSV file with the columns: image, date, rating
    '''
    print('Creating database: {}'.format(db))
    print('Looking for images in: {}'.format(image_dir))

    if os.path.exists(db):
        print('{} exists.  Please remove before proceeding.'.format(db))
        sys.exit(1)

    if not os.path.isdir(image_dir):
        print('Image directory {} cannot be found.'.format(image_dir))
        sys.exit(1)

    conn = sqlite3.connect(db)

    c = conn.cursor()

    # Create tables
    c.execute(SQL_CREATE_TABLE_IMAGES)
    c.execute(SQL_CREATE_TABLE_MATCHES)

    print('Tables created...')

    for file in os.listdir(image_dir):
        extension = os.path.splitext(file)[1][1:]
        if extension in ['png', 'jpg', 'jpeg']:
            now = time.strftime('%Y%m%d_%H%M%S%MS', time.localtime())
            fullpath = os.path.abspath(os.path.join(image_dir, file))
            c.execute(SQL_INSERT_IMAGES, (file, fullpath, now, 1200.0, 0, 0))
        else:
            print('Skipping file {}, extension not supported.'.format(file))

    # Save (commit) the changes
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()

    print('Database initialized')


def stats(db):
    with open('detail_results.tsv', 'w') as fd:
        fd.write(get_detail_report(db, '\t').getvalue())

    with open('rankings_report.tsv', 'w') as fd:
        fd.write(get_ranking_report(db, '\t').getvalue())

