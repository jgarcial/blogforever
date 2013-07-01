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
Collector for report history of the user

@undocumented: COLLECTOR
"""
from flask import url_for
from invenio.sqlalchemyutils import db
from invenio.webcomment_model import CmtACTIONHISTORY
from invenio.webcomment_model import CmtRECORDCOMMENT
from invenio.webhistory_collector import HistoryCollector
from invenio.webhistory_collector import get_record_title
from invenio.webhistory_config import CFG_SHARE_MSGS
from invenio.webhistory_config import CFG_WEBHISTORY_MSGS
from invenio.webinterface_handler_flask_utils import _
from sqlalchemy.sql import expression


class ReportHistory(HistoryCollector):
    """
    Collects report history
    """
    icon = 'exclamation-sign'
    label = 'Reports'

    @staticmethod
    def get_date(x):
        return x.action_time

    @staticmethod
    def get_id(x):
        return x.id_cmtRECORDCOMMENT

    @staticmethod
    def serialize(x):
        return [x.id_cmtRECORDCOMMENT,
                x.id_bibrec,
                x.star_score]

    def get_user_history(self, limit, offset, filter_from, filter_to):
        """
        Returns user's review history.
        """
        reports = (db.session
                   .query(CmtACTIONHISTORY.id_bibrec,
                          CmtACTIONHISTORY.id_user,
                          CmtACTIONHISTORY.action_time,
                          CmtACTIONHISTORY.id_cmtRECORDCOMMENT,
                          CmtRECORDCOMMENT.star_score)
                   .filter(CmtACTIONHISTORY.id_user == self._uid)
                   .filter(CmtACTIONHISTORY.action_code == 'A')
                   .filter(CmtACTIONHISTORY.id_cmtRECORDCOMMENT
                           == CmtRECORDCOMMENT.id))

        if filter_from:
            reports = reports.filter(CmtACTIONHISTORY.action_time
                                     >= filter_from)

        if filter_to:
            reports = reports.filter(CmtACTIONHISTORY.action_time <= filter_to)

        reports = (reports
                   .order_by(expression.desc(CmtACTIONHISTORY.action_time))
                   .limit(limit)
                   .offset(offset)
                   .all())

        return reports

    @staticmethod
    def get_message(entry):
        """
        Returns a message to display report history on web-interface.

        @see: L{HistoryElement.get_message}
        """
        title = get_record_title(entry.id_bibrec)
        recordurl = url_for('record.metadata', recid=entry.id_bibrec)
        if entry.star_score == 0:
            discussionurl = (url_for('webcomment.comments',
                                     recid=entry.id_bibrec)
                             + "#collapse-%s" % entry.id_cmtRECORDCOMMENT)
            return _(CFG_WEBHISTORY_MSGS[11]) % {'recordurl': recordurl,
                                                 'title': title,
                                                 'discussionurl': discussionurl
                                                 }

        else:
            reviewurl = url_for('webcomment.reviews', recid=entry.id_bibrec)
            return _(CFG_WEBHISTORY_MSGS[12]) % {'recordurl': recordurl,
                                                 'title': title,
                                                 'reviewurl': reviewurl}

    @staticmethod
    def get_share_message(serialized_history_element):
        """
        Returns a message used while sharing report history on
        web-interface.

        @see: L{HistoryElement.get_share_message}
        """
        title = get_record_title(serialized_history_element[1])
        recordurl = url_for('record.metadata',
                            recid=serialized_history_element[1])
        if int(serialized_history_element[2]) == 0:
            discussionurl = (url_for('webcomment.comments',
                                     recid=serialized_history_element[1])
                             + "#collapse-%s" % serialized_history_element[0])
            return _(CFG_SHARE_MSGS[11]) % {'recordurl': recordurl,
                                            'title': title,
                                            'discussionurl': discussionurl}

        else:
            reviewurl = url_for('webcomment.reviews',
                                recid=serialized_history_element[1])
            return _(CFG_SHARE_MSGS[12]) % {'recordurl': recordurl,
                                            'title': title,
                                            'reviewurl': reviewurl}

COLLECTOR = ReportHistory
