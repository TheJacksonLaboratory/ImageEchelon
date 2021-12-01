from __future__ import absolute_import
from __future__ import division
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

__author__ = 'dow'

import random
import sqlite3
import time
from elo import Rating, quality_1vs1, rate_1vs1


def main():
    fd = open("rankings_report.tsv",'w')
    dd = open("detail_results.tsv",'w')
    conn = sqlite3.connect('data/db/image-echelon.db')
    c = conn.cursor()
    fd.write("image\trating\tmatch-ups\n")
    for row in c.execute("select * from images order by rank desc"):
        fd.write('{0}\t{1:.1f}\t{2}\n'.format(row[1], row[3], row[4]))

    for row in c.execute("select * from details order by name, updated"):
        dd.write('{0}\t{1}\t{2:.1f}\n'.format(row[0], row[1], row[2]))
    conn.close()
    fd.close()
    dd.close()

if __name__ == "__main__":
    main()
