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
Collector for record view history of the user

@undocumented: COLLECTOR
"""
from flask import url_for
from invenio.bibrank_model import RnkPAGEVIEWS
from invenio.sqlalchemyutils import db
from invenio.webhistory_collector import HistoryCollector
from invenio.webhistory_collector import get_record_title
from invenio.webhistory_config import CFG_SHARE_MSGS
from invenio.webhistory_config import CFG_WEBHISTORY_MSGS
from invenio.webinterface_handler_flask_utils import _
from sqlalchemy.sql import expression


class RecordViewHistory(HistoryCollector):
    """
    Collects record view history
    """
    icon = 'eye-open'
    label = 'Page Views'

    @staticmethod
    def get_date(x):
        return x.view_time

    @staticmethod
    def get_id(x):
        return x.id_bibrec

    @staticmethod
    def serialize(x):
        return [x.id_bibrec]

    def get_user_history(self, limit, offset, filter_from, filter_to):
        """
        Returns user's record view history.
        """
        records = (db.session
                   .query(RnkPAGEVIEWS.id_bibrec,
                          RnkPAGEVIEWS.view_time)
                   .filter(RnkPAGEVIEWS.id_user == self._uid))

        if filter_from:
            records = records.filter(RnkPAGEVIEWS.view_time >= filter_from)

        if filter_to:
            records = records.filter(RnkPAGEVIEWS.view_time <= filter_to)

        records = (records
                   .order_by(expression.desc(RnkPAGEVIEWS.view_time))
                   .limit(limit)
                   .offset(offset)
                   .all())

        return records

    @staticmethod
    def get_message(entry):
        """
        Returns a message to display record view history on web-interface.

        @see: L{HistoryElement.get_message}
        """
        title = get_record_title(entry.id_bibrec)
        recordurl = url_for('record.metadata', recid=entry.id_bibrec)
        return _(CFG_WEBHISTORY_MSGS[6]) % {'recordurl': recordurl,
                                            'title': title}

    @staticmethod
    def get_share_message(serialized_history_element):
        """
        Returns a message used while sharing record view history on
        web-interface.

        @see: L{HistoryElement.get_share_message}
        """
        title = get_record_title(serialized_history_element[0])
        recordurl = url_for('record.metadata',
                            recid=serialized_history_element[0])
        return _(CFG_SHARE_MSGS[6]) % {'recordurl': recordurl,
                                       'title': title}

COLLECTOR = RecordViewHistory
