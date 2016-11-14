from __future__ import print_function

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
from flask import Flask
from flask import render_template
from flask import jsonify
from flask import send_file
import ImageEchelon


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
    pair = ImageEchelon.select_matchup(CONF)
    return jsonify(pair=pair)


@app.route("/update/winner=<winner>;loser=<loser>", methods = ['GET'])
def update(winner, loser):

    json = ImageEchelon.update_ranking(CONF, winner, loser)
    return jsonify(json)


@app.route("/report", methods=["GET"])
@app.route("/report/", methods = ['GET'])
def report():
    csvfile = ImageEchelon.get_ranking_report(CONF)
    return send_file(csvfile, attachment_filename='rank_report.csv', as_attachment=True)


@app.route("/detail", methods=["GET"])
@app.route("/detail/", methods = ['GET'])
def detail():
    csvfile = ImageEchelon.get_detail_report(CONF)
    return send_file(csvfile, attachment_filename='detail_report.csv', as_attachment=True)


if __name__ == "__main__":
    app.config.from_object('config')
    app.logger.debug("Starting...")
    app.debug = True

    CONF.STATIC = '/static'
    CONF.URL_BASE = app.config["URL_BASE"]
    CONF.URL_BASE_STATIC = app.config["URL_BASE_STATIC"]
    CONF.DB_DIR = app.config["DB_DIR"]
    app.run(host='0.0.0.0', port=9766, processes=5)

