# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2012, 2013 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""
Functions for rank method: "recently archived content".
"""

from datetime import datetime, timedelta
from invenio.bibedit_model import Bibrec
from invenio.dateutils import SECOND_CONVERSION
from invenio.dateutils import strptime
from invenio.sqlalchemyutils import db
from sqlalchemy.sql import expression


def records_in_time_interval_to_index(date_type='creation',
                                      limit=10,
                                      start_from=None,
                                      end_to=None,
                                      interval=None):
    """
    Sorts records with respect to creation or modification date.

    @param date_type: Field to be sorted on. Possible values are 'creation'
        and 'modification'.
    @type date_type: str

    @param limit: Number of records in the output.
    @type limit: int

    @param start_from: Start point.
    @type start_from: str

    @param end_to: End point.
    @type end_to: str

    @param interval: A time interval like in MySQL. (i.e. "1 HOUR", "3 DAY",
        "2 YEAR")
    @type interval: str

    @rtype: {int: str}
    """
    if date_type == "creation":
        sorting_column = Bibrec.creation_date
    else:
        sorting_column = Bibrec.modification_date

    query = db.session.query(Bibrec.id, sorting_column)

    if interval:
        try:
            interval = interval.strip().split(" ")
            total_seconds = (int(interval[0]) *
                             SECOND_CONVERSION.get(interval[1], 0))
            interval = datetime.now() - timedelta(seconds=total_seconds)
            query = query.filter(sorting_column >= interval)
        except:
            pass
    else:
        if start_from:
            if len(start_from) <= 10:
                start_date = strptime(start_from, "%Y-%m-%d")
            else:
                start_date = strptime(start_from, "%Y-%m-%d %H:%M:%S")

            query = query.filter(sorting_column > start_date)
        if end_to:
            if len(end_to) < 10:
                end_date = strptime(end_to, "%Y-%m-%d")
            else:
                end_date = strptime(end_to, "%Y-%m-%d %H:%M:%S")

            query = query.filter(sorting_column < end_date)

    query = query.order_by(expression.desc(sorting_column))

    if limit:
        query = query.limit(limit)

    records = query.all()

    dic = {}

    for record in records:
        dic[record[0]] = record[1].strftime("%Y-%m-%d %H:%M")

    return dic
