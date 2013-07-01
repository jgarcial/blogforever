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
Collector for download history of the user

@undocumented: COLLECTOR
"""
from flask import url_for
from invenio.bibrank_model import RnkDOWNLOADS
from invenio.sqlalchemyutils import db
from invenio.webhistory_collector import HistoryCollector
from invenio.webhistory_collector import get_record_title
from invenio.webhistory_config import CFG_SHARE_MSGS
from invenio.webhistory_config import CFG_WEBHISTORY_MSGS
from invenio.webinterface_handler_flask_utils import _
from sqlalchemy.sql import expression


class DownloadHistory(HistoryCollector):
    """
    Collects download history
    """
    icon = 'download'
    label = 'Downloads'

    @staticmethod
    def get_date(x):
        return x.download_time

    @staticmethod
    def get_id(x):
        return x.id

    @staticmethod
    def serialize(x):
        return [x.id_bibrec, x.file_format]

    def get_user_history(self, limit, offset, filter_from, filter_to):
        """
        Returns user's download history.
        """
        downloads = (db.session
                     .query(RnkDOWNLOADS.id,
                            RnkDOWNLOADS.id_bibrec,
                            RnkDOWNLOADS.file_format,
                            RnkDOWNLOADS.download_time)
                     .filter(RnkDOWNLOADS.id_user == self._uid)
                     .filter(RnkDOWNLOADS.id_bibrec != 0))

        if filter_from:
            downloads = downloads.filter(RnkDOWNLOADS.download_time
                                         >= filter_from)

        if filter_to:
            downloads = downloads.filter(RnkDOWNLOADS.download_time
                                         <= filter_to)

        downloads = (downloads
                     .order_by(expression.desc(RnkDOWNLOADS.download_time))
                     .limit(limit)
                     .offset(offset)
                     .all())

        return downloads

    @staticmethod
    def get_message(entry):
        """
        Returns a message to display download history on web-interface.

        @see: L{HistoryElement.get_message}
        """
        title = get_record_title(entry.id_bibrec)
        recordurl = url_for('record.metadata', recid=entry.id_bibrec)
        return _(CFG_WEBHISTORY_MSGS[16]) % {'title': title,
                                             'recordurl': recordurl,
                                             'format': entry.file_format}

    @staticmethod
    def get_share_message(serialized_history_element):
        """
        Returns a message used while sharing download history on
        web-interface.

        @see: L{HistoryElement.get_share_message}
        """
        title = get_record_title(serialized_history_element[0])
        recordurl = url_for('record.metadata',
                            recid=serialized_history_element[0])
        return _(CFG_SHARE_MSGS[16]) % {'title': title,
                                        'recordurl': recordurl,
                                        'format': serialized_history_element[1]
                                        }

COLLECTOR = DownloadHistory
