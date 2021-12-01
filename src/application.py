from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from builtins import object
from io import BytesIO
import logging

from flask import Flask
from flask import render_template
from flask import jsonify
from flask import make_response
from flask import send_file
from flask import stream_with_context
from src import ImageEchelon

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

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.debug = True
application = app


class Config(object):
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


@app.route("/loadtext/", methods = ['GET'])
def load_text():
    text_fields = {
        "full_description": app.config['FULL_DESCRIPTION'],
        "head_text": app.config['HEAD_TEXT'],
        "img_1_label": app.config['IMG_1_LABEL'],
        "img_1_text": app.config['IMG_1_TEXT'],
        "img_2_label": app.config['IMG_2_LABEL'],
        "img_2_text": app.config['IMG_1_TEXT'],
    }
    return jsonify(text_fields=text_fields)


@app.route("/update/winner=<winner>;loser=<loser>", methods = ['GET'])
def update(winner, loser):
    json = ImageEchelon.update_ranking(CONF, winner, loser)
    return jsonify(json)


@app.route("/report/", methods=["GET"], strict_slashes=False)
def report():
    csvfile = ImageEchelon.get_ranking_report(CONF)
    mem = BytesIO()
    mem.write(csvfile.getvalue().encode())
    # seeking was necessary. Python 3.5.2, Flask 0.12.2
    mem.seek(0)
    return send_file(mem, attachment_filename='rank_report.csv', as_attachment=True, cache_timeout=-1)


@app.route("/detail/", methods=["GET"], strict_slashes=False)
def detail():
    csvfile = ImageEchelon.get_detail_report(CONF)
    mem = BytesIO()
    mem.write(csvfile.getvalue().encode())
    # seeking was necessary. Python 3.5.2, Flask 0.12.2
    mem.seek(0)
    return send_file(mem, attachment_filename='detail_report.csv', as_attachment=True, cache_timeout=-1)


if __name__ == "__main__":
    app.config.from_object('config')
    app.logger.debug("Starting...")
    app.debug = True

    CONF.STATIC = '/static'
    CONF.URL_BASE = app.config["URL_BASE"]
    CONF.URL_BASE_STATIC = app.config["URL_BASE_STATIC"]
    CONF.DB_DIR = app.config["DB_DIR"]
    app.run(host='0.0.0.0', port=9766, processes=1, threaded=False)

