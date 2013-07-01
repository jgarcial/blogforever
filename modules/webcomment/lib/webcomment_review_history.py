# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013 CERN.
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
Collector for review history of the user

@undocumented: COLLECTOR
"""
from flask import url_for
from invenio.sqlalchemyutils import db
from invenio.webcomment_model import CmtRECORDCOMMENT
from invenio.webhistory_collector import HistoryCollector
from invenio.webhistory_collector import get_record_title
from invenio.webhistory_config import CFG_SHARE_MSGS
from invenio.webhistory_config import CFG_WEBHISTORY_MSGS
from invenio.webinterface_handler_flask_utils import _
from sqlalchemy.sql import expression


class ReviewHistory(HistoryCollector):
    """
    Collects review history
    """
    icon = 'star'
    label = 'Reviews'

    @staticmethod
    def get_date(x):
        return x.date_creation

    @staticmethod
    def get_id(x):
        return x.id

    @staticmethod
    def serialize(x):
        return [x.id_bibrec, x.star_score]

    def get_user_history(self, limit, offset, filter_from, filter_to):
        """
        Returns user's review history.
        """
        reviews = (db.session
                   .query(CmtRECORDCOMMENT.id,
                          CmtRECORDCOMMENT.id_bibrec,
                          CmtRECORDCOMMENT.date_creation,
                          CmtRECORDCOMMENT.star_score)
                   .filter(CmtRECORDCOMMENT.id_user == self._uid)
                   .filter(CmtRECORDCOMMENT.star_score > 0))

        if filter_from:
            reviews = reviews.filter(CmtRECORDCOMMENT.date_creation
                                     >= filter_from)

        if filter_to:
            reviews = reviews.filter(CmtRECORDCOMMENT.date_creation
                                     <= filter_to)

        reviews = (reviews
                   .order_by(expression.desc(CmtRECORDCOMMENT.date_creation))
                   .limit(limit)
                   .offset(offset)
                   .all())

        return reviews

    @staticmethod
    def get_message(entry):
        """
        Returns a message to display review history on web-interface.

        @see: L{HistoryElement.get_message}
        """
        title = get_record_title(entry.id_bibrec)
        recordurl = url_for('record.metadata', recid=entry.id_bibrec)
        reviewurl = url_for('webcomment.reviews', recid=entry.id_bibrec)

        return _(CFG_WEBHISTORY_MSGS[8]) % {'recordurl': recordurl,
                                            'title': title,
                                            'reviewurl': reviewurl,
                                            'stars': entry.star_score
                                            * '<i class="icon-star"></i>'}

    @staticmethod
    def get_share_message(serialized_history_element):
        """
        Returns a message used while sharing review history on
        web-interface.

        @see: L{HistoryElement.get_share_message}
        """
        title = get_record_title(serialized_history_element[0])
        recordurl = url_for('record.metadata',
                            recid=serialized_history_element[0])
        reviewurl = url_for('webcomment.reviews',
                            recid=serialized_history_element[0])
        return _(CFG_SHARE_MSGS[8]) % {'recordurl': recordurl,
                                       'title': title,
                                       'reviewurl': reviewurl,
                                       'stars':
                                       int(serialized_history_element[1])
                                       * '<i class="icon-star"></i>'}

COLLECTOR = ReviewHistory
