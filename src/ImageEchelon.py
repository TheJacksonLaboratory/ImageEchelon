from __future__ import print_function

"""
ImageEchelon is the service module that contains all the logic for getting match-ups, updating rankings,
and generating ranking reports.  All database interactions are abstracted within this module.


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
import random
import sqlite3
import time
from elo import  Rating, quality_1vs1, rate_1vs1
import cStringIO
import csv

SOURCE_DIR = os.path.dirname(os.path.realpath(__file__))


def select_matchup(config):
    """
    Method to select the next pair of images to be compared
    :param config: A config object that contains the db directory/file name.
    :return: returns a pair of image dictionaries, with the attributes: name, location, updated, rating and used
    """
    #  Set up for sqlite db
    conn = sqlite3.connect(os.path.join(SOURCE_DIR, config.DB_DIR))
    c = conn.cursor()
    images = []

    for row in c.execute("select * from images"):
        image = {
            'name':     row[1],
            'location': row[2],
            'updated':  row[0],
            'rating':   row[3],
            'used':     row[4]
        }
        images.append(image)
    random.seed()
    random.shuffle(images)
    pair = images[:2]

    conn.close()
    return pair


def update_ranking(config, winner, loser):
    """
    Method to update the database ranking value for both the winner and loser based on an ELO algorithm
    :param config: A config object that contains the db directory/file name.
    :param winner: The image selected by the user
    :param loser: The image not selected by the user
    :return:  Returns a results map containing a "winner" and a "loser" with their new rankings.  Rankings include
                columns: name, updated, rating, matchups
    """
    #  Set up for sqlite db
    conn = sqlite3.connect(os.path.join(SOURCE_DIR, config.DB_DIR))
    c = conn.cursor()
    c.execute("select rank, matchups from images where name = '" + winner + "'")
    win_row = c.fetchone()
    win_rank = win_row[0]
    win_match = win_row[1] + 1
    win_rating = Rating(win_rank)

    c.execute("select rank, matchups from images where name = '" + loser + "'")
    lose_row = c.fetchone()
    lose_rank = lose_row[0]
    lose_match = lose_row[1] + 1
    lose_rating = Rating(lose_rank)

    # update ratings
    win_rating, lose_rating = rate_1vs1(win_rating, lose_rating)
    now = time.strftime("%Y%m%d_%H%M%S%MS", time.localtime())

    c.execute("UPDATE images " +
              "set updated = '" + now + "', rank = " + str(win_rating) + ", matchups = " + str(win_match) +
              " where name = '" + winner + "'")
    c.execute("INSERT INTO details VALUES ('" + winner + "', '" + now + "', " + str(win_rating) + ")")

    c.execute("UPDATE images " +
              "set updated = '" + now + "', rank = " + str(lose_rating) + ", matchups = " + str(lose_match) +
              " where name = '" + loser + "'")
    c.execute("INSERT INTO details VALUES ('" + loser + "', '" + now + "', " + str(lose_rating) + ")")

    conn.commit()
    conn.close()
    win_res = {"name":winner, "updated": now, "rating": win_rating, "matchups": win_match}
    lose_res = {"name":loser, "updated": now, "rating": lose_rating, "matchups": lose_match}
    results = {"winner":win_res, "loser":lose_res}

    return results


def get_ranking_report(config):
    """
    Generates the CSV ranking report file
    :param config: A config object that contains the db directory/file name.
    :return: CSV file with the columns: image, rating, match-ups
    """
    conn = sqlite3.connect(os.path.join(SOURCE_DIR, config.DB_DIR))
    c = conn.cursor()
    query_results = c.execute("select * from images order by rank desc")

    csvfile = cStringIO.StringIO()
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


def get_detail_report(config):
    """
    Generates the CSV detail report file
    :param config: A config object that contains the db directory/file name.
    :return: CSV file with the columns: image, date, rating
    """
    conn = sqlite3.connect(os.path.join(SOURCE_DIR, config.DB_DIR))
    c = conn.cursor()
    query_results = c.execute("select * from details order by name, updated")

    csvfile = cStringIO.StringIO()
    headers = [
        'image',
        'date',
        'rating'
    ]
    rows = []
    for row in query_results:
        rows.append(
            {
                'image': row[0],
                'date': row[1],
                'rating': row[2]
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


