from __future__ import print_function

'''
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

import os
import click

from flask import Flask
from flask import render_template
from flask import jsonify
from flask import send_file

from ImageEchelon import __version__, __logo__
from ImageEchelon import IE

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__, message=__logo__)
def cli():
    '''
    ImageEchelon

    '''


app = Flask(__name__)


@app.errorhandler(500)
def internal_error(error):
    return '500 error'


@app.errorhandler(404)
def page_not_found(error):
    return '404 error', 404


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/getpair/', methods=['GET'])
def getpair():
    pair = IE.select_matchup(app.config['DB'])
    return jsonify(pair=pair)


@app.route('/update/winner=<winner>;loser=<loser>', methods=['GET'])
def update(winner, loser):
    json = IE.update_ranking(app.config['DB'], winner, loser)
    return jsonify(json)


@app.route('/report', methods=['GET'])
@app.route('/report/', methods=['GET'])
def report():
    csvfile = IE.get_ranking_report(app.config['DB'])
    return send_file(csvfile, attachment_filename='rank_report.csv',
                     as_attachment=True)


@app.route('/detail', methods=['GET'])
@app.route('/detail/', methods=['GET'])
def detail():
    csvfile = IE.get_detail_report(app.config['DB'])
    return send_file(csvfile, attachment_filename='detail_report.csv',
                     as_attachment=True)


@app.route('/image/<image_name>', methods=['GET'])
def image(image_name):
    filename = os.path.join(app.config['IMAGE_PATH'], image_name)
    return send_file(filename)


def fixpaths():
    if os.path.isabs(app.config['DB']):
        app.config['DB'] = os.path.abspath(app.config['DB'])
    else:
        app.config['DB'] = os.path.join(os.getcwd(), app.config['DB'])
        app.config['DB'] = os.path.abspath(app.config['DB'])

    if os.path.isabs(app.config['IMAGE_PATH']):
        app.config['IMAGE_PATH'] = os.path.abspath(app.config['IMAGE_PATH'])
    else:
        app.config['IMAGE_PATH'] = os.path.abspath(app.config['IMAGE_PATH'])

    print('DB={}'.format(app.config['DB']))
    print('IMAGE_PATH={}'.format(app.config['IMAGE_PATH']))


@cli.command('web', options_metavar='<options>',
             short_help='start the web server')
def web():
    '''
    Start the web server
    '''
    app.config.from_object('config')
    app.config.from_envvar('IMAGE_ECHELON_SETTINGS')
    fixpaths()

    app.run(host='0.0.0.0', port=app.config['PORT'])


@cli.command('initdb', options_metavar='<options>',
             short_help='create the database')
def initdb():
    '''
    Create the ImageEchelon database
    '''
    app.config.from_object('config')
    app.config.from_envvar('IMAGE_ECHELON_SETTINGS')
    fixpaths()

    IE.init(app.config['DB'], app.config['IMAGE_PATH'])


@cli.command('reports', options_metavar='<options>',
             short_help='create the database')
def reports():
    '''
    Generate reports
    '''
    app.config.from_object('config')
    app.config.from_envvar('IMAGE_ECHELON_SETTINGS')
    fixpaths()

    IE.stats()


if __name__ == "__main__":
    cli()