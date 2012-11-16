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
Functions for rank method: "weighted average".
"""

from invenio.sqlalchemyutils import db
from invenio.webcomment_model import CmtRECORDCOMMENT
from sqlalchemy.sql import func


def weighted_average_to_index(minimum_review_number):
    """
    Returns a dictionary that contains record IDs as keys and
    their weighted average scores as values. Bayesian estimate is used to
    calculate weighted average.

    @param minimum_review_number: the number of reviews
    required to be indexed.
    """
    minimum_review_number = float(minimum_review_number)

    general_average = (db
                       .session
                       .query(func.avg(CmtRECORDCOMMENT.star_score))
                       .filter(CmtRECORDCOMMENT.star_score > 0)
                       .first()[0])

    if not general_average:
        return {}

    general_average = float(general_average)

    score_table = (db
                   .session
                   .query(CmtRECORDCOMMENT.id_bibrec,
                          func.avg(CmtRECORDCOMMENT.star_score),
                          func.count(CmtRECORDCOMMENT.star_score))
                   .filter(CmtRECORDCOMMENT.star_score > 0)
                   .group_by(CmtRECORDCOMMENT.id_bibrec)
                   .all())

    index_dict = {}

    for (record, avg_score, review_number) in score_table:
        if review_number < minimum_review_number:
            continue
        review_number = float(review_number)
        avg_score = float(avg_score)
        weighted_average = ((review_number / (review_number +
                                               minimum_review_number)) *
                              avg_score + (minimum_review_number /
                                           (review_number +
                                            minimum_review_number)) *
                              general_average)
        index_dict[record] = float("%.4f" % weighted_average)

    return index_dict
