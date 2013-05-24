## This file is part of Invenio.
## Copyright (C) 2012 CERN.
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
from invenio.bibedit_model import Bibrec
from invenio.bibrank_model import RnkPAGEVIEWS
from invenio.bibrank_record_sorter import rank_records
from invenio.config import CFG_MOST_FREQUENT_TERM_NUMBER
from invenio.config import CFG_RECOMMENDATION_RANK_METHOD
from invenio.config import CFG_RECOMMENDED_CONTENT_NUMBER
from invenio.intbitset import intbitset
from invenio.search_engine_utils import get_fieldvalues
from invenio.sqlalchemyutils import db
from invenio.websearch_model import QueryTerm
from invenio.websearch_model import UserQueryTerm
from sqlalchemy.sql import expression
from sqlalchemy.sql import operators
"""Functions for recommendation system"""


def get_recommended_content(uid):
    """
    Get the list of the recommended content for the user

    @param uid: The ID of the user
    @type uid: int

    @rtype: [{"id": int, "title": str}]
    """
    most_frequent_terms = get_query_terms(uid)
    unread_records = intbitset(get_unread_records(uid))
    recommended = {}

    limit = 0
    for (term, count) in most_frequent_terms:
        if limit == CFG_MOST_FREQUENT_TERM_NUMBER:
            break
        similars = rank_records(CFG_RECOMMENDATION_RANK_METHOD,
                                10,
                                unread_records,
                                [term])

        if similars[0]:
            for index in range(len(similars[0])):
                if similars[1][index]:
                    current_score = recommended.get(similars[0][index], 0)
                    recommended[similars[0][index]] = (current_score
                                                       + similars[1][index]
                                                       * count)
                    limit += 1

    recommended_record_ids = sorted(recommended,
                                    key=lambda y: recommended[y],
                                    reverse=True)

    return [{"id": record_id,
             "title": get_fieldvalues(record_id, "245___")[0]
                      .decode("utf-8", "replace")}
            for record_id
            in recommended_record_ids[:CFG_RECOMMENDED_CONTENT_NUMBER]
            if recommended[record_id]]


def get_query_terms(uid):
    """
    Returns the list of the query terms that user searched

    @param uid: The ID of the user
    @type uid: int

    @rtype: [(str, int)]
    """

    return (db
            .session
            .query(QueryTerm.term, UserQueryTerm.count)
            .filter(QueryTerm.id == UserQueryTerm.id_term)
            .filter(UserQueryTerm.id_user == uid)
            .order_by(expression.desc(UserQueryTerm.count))
            .all())


def get_unread_records(uid):
    """
    Returns the the record IDs that have not seen by the user

    @param uid: The ID of the user
    @type uid: int

    @rtype: [(int)]
    """

    records = (db
               .session
               .query(Bibrec.id)
               .filter(operators
                       .notin_op(Bibrec.id,
                              db
                              .session
                              .query(RnkPAGEVIEWS.id_bibrec)
                              .filter(RnkPAGEVIEWS.id_user == uid)))
               .all())

    return [record.id for record in records]
