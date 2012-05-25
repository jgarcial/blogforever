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
    Functions for rank method: "average score".
"""

from invenio.sqlalchemyutils import db
from invenio.webcomment_model import CmtRECORDCOMMENT
from sqlalchemy.sql import func


def average_score_to_index():
    """
        Returns a dictionary that contains record IDs as keys and
        their average scores as values.
    """

    score_table = (db
                   .session
                   .query(CmtRECORDCOMMENT.id_bibrec,
                          func.avg(CmtRECORDCOMMENT.star_score))
                   .filter(CmtRECORDCOMMENT.star_score > 0)
                   .group_by(CmtRECORDCOMMENT.id_bibrec)
                   .all())

    index_dict = {}

    for (record, score) in score_table:
        index_dict[record] = float(score)

    return index_dict
