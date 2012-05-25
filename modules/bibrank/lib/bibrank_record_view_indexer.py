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
    Functions for rank method: "record view".
"""

from invenio.bibrank_model import RnkPAGEVIEWS
from invenio.sqlalchemyutils import db


def record_view_to_index(unit_time):
    """
        Returns a dictionary that contains record IDs as keys and number of
        visits as values.
    """

    record_table = (db
                    .session
                    .query(RnkPAGEVIEWS.id_bibrec,
                           RnkPAGEVIEWS.client_host,
                           RnkPAGEVIEWS.view_time)
                    .order_by(RnkPAGEVIEWS.client_host)
                    .order_by(RnkPAGEVIEWS.id_bibrec)
                    .order_by(RnkPAGEVIEWS.view_time)
                    .all())

    index_dict = {}
    length = len(record_table)
    index = 0

    while index < length:
        if index == length - 1:
            count = index_dict.get(record_table[index].id_bibrec, 0)
            index_dict[record_table[index].id_bibrec] = count + 1
            break

        if (record_table[index].id_bibrec ==
            record_table[index + 1].id_bibrec
            and
            record_table[index].client_host ==
            record_table[index + 1].client_host
            and
            (record_table[index + 1].view_time -
            record_table[index].view_time).total_seconds() < unit_time):
            pass
        else:
            count = index_dict.get(record_table[index].id_bibrec, 0)
            index_dict[record_table[index].id_bibrec] = count + 1
        index += 1

    return index_dict
