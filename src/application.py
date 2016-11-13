"""
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

from flask import Flask
from flask import render_template
from flask import jsonify
from flask import send_file


SOURCE_DIR = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)
app.debug = True
application = app

class Config:
    pass

CONF = Config()

@app.errorhandler(500)
def internal_error(error):
    return "500 error"

@app.errorhandler(404)
def page_not_found(error):
    return "404 error", 404

@app.route("/", methods = ['GET'])
def index():
    return render_template('index.html', CONF=CONF)

@app.route("/getpair/", methods = ['GET'])
def getpair():
    return jsonify(pair=select_matchup())

@app.route("/update/winner=<winner>;loser=<loser>", methods = ['GET'])
def update(winner, loser):

    json = update_ranking(winner, loser)
    return jsonify(json)

@app.route("/report", methods=["GET"])
@app.route("/report/", methods = ['GET'])
def report():
    conn = sqlite3.connect(os.path.join(SOURCE_DIR, '../data/db/image-echelon.db'))
    csvfile = getRankingReport(conn)
    conn.close()

    return send_file(csvfile, attachment_filename='rank_report.csv', as_attachment=True)

@app.route("/detail", methods=["GET"])
@app.route("/detail/", methods = ['GET'])
def detail():
    conn = sqlite3.connect(os.path.join(SOURCE_DIR, '../data/db/image-echelon.db'))
    csvfile = getDetailReport(conn)
    conn.close()

    return send_file(csvfile, attachment_filename='detail_report.csv', as_attachment=True)

def select_matchup():
    #  Set up for sqlite db
    conn = sqlite3.connect(os.path.join(SOURCE_DIR, '../data/db/image-echelon.db'))
    c = conn.cursor()
    images = []

    for row in c.execute("select * from images"):
        image = {}
        image['name'] = row[1]
        image['location'] = row[2]
        image['updated'] = row[0]
        image['rating'] = row[3]
        image['used'] = row[4]
        images.append(image)

    random.seed()
    random.shuffle(images)
    pair = images[:2]

    conn.close()
    return pair

def update_ranking(winner, loser):

    #  Set up for sqlite db
    conn = sqlite3.connect(os.path.join(SOURCE_DIR, '../data/db/image-echelon.db'))
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
    win_res = {"name":winner, "updated": now, "rating": win_rating, "matchups": win_match}
    lose_res = {"name":loser, "updated": now, "rating": lose_rating, "matchups": lose_match}
    results = {"winner":win_res, "loser":lose_res}

    return results

def getRankingReport(conn):
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
    return csvfile

def getDetailReport(conn):
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
    return csvfile

if __name__ == "__main__":
    app.config.from_object('config')
    app.logger.debug("Starting...")
    app.debug = True

    CONF.STATIC = '/static'
    CONF.URL_BASE = app.config["URL_BASE"]
    CONF.URL_BASE_STATIC = app.config["URL_BASE_STATIC"]
    app.run(host='0.0.0.0', port=9766, processes=5)

