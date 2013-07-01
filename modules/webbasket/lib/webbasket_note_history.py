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
Collector for basket note history of the user

@undocumented: COLLECTOR
"""
from flask import url_for
from invenio.config import CFG_SITE_SECURE_URL
from invenio.sqlalchemyutils import db
from invenio.webbasket_model import BskBASKET
from invenio.webbasket_model import BskREC
from invenio.webbasket_model import BskRECORDCOMMENT
from invenio.webhistory_collector import HistoryCollector
from invenio.webhistory_collector import get_record_title
from invenio.webhistory_config import CFG_SHARE_MSGS
from invenio.webhistory_config import CFG_WEBHISTORY_MSGS
from invenio.webinterface_handler_flask_utils import _
from sqlalchemy.sql import expression


class BasketNoteHistory(HistoryCollector):
    """
    Collects basket note history
    """
    icon = 'pencil'
    label = 'Notes on Baskets'

    @staticmethod
    def get_date(x):
        return x.date_creation

    @staticmethod
    def get_id(x):
        return x.id_BskRECORDCOMMENT

    @staticmethod
    def serialize(x):
        return [x.id, x.name, x.id_bibrec_or_bskEXTREC]

    def get_user_history(self, limit, offset, filter_from, filter_to):
        """
        Returns user's basket note history.
        """
        # pylint: disable=E1101
        baskets = (db.session
                   .query(BskRECORDCOMMENT.id_bibrec_or_bskEXTREC,
                          BskRECORDCOMMENT.date_creation,
                          BskBASKET.name,
                          BskBASKET.id,
                          BskRECORDCOMMENT.id.label("id_BskRECORDCOMMENT"))
                   .filter(BskREC.id_user_who_added_item == self._uid)
                   .filter(BskBASKET.id == BskRECORDCOMMENT.id_bskBASKET))
        # pylint: enable=E1101

        if filter_from:
            baskets = baskets.filter(BskRECORDCOMMENT.date_creation
                                     >= filter_from)

        if filter_to:
            baskets = baskets.filter(BskRECORDCOMMENT.date_creation
                                     <= filter_to)

        baskets = (baskets
                   .order_by(expression.desc(BskRECORDCOMMENT.date_creation))
                   .limit(limit)
                   .offset(offset)
                   .all())

        return baskets

    @staticmethod
    def get_message(entry):
        """
        Returns a message to display basket note history on web-interface.

        @see: L{HistoryElement.get_message}
        """
        title = get_record_title(entry.id_bibrec_or_bskEXTREC)
        recordurl = url_for('record.metadata',
                            recid=entry.id_bibrec_or_bskEXTREC)
        basketurl = (CFG_SITE_SECURE_URL
                     + "/yourbaskets/display?bskid=%s" % entry.id)
        noteurl = (CFG_SITE_SECURE_URL
                   + "/yourbaskets/display?bskid=%s&recid=%s"
                   % (entry.id, entry.id_bibrec_or_bskEXTREC))
        return _(CFG_WEBHISTORY_MSGS[20]) % {'title': title,
                                             'recordurl': recordurl,
                                             'basketname': entry.name,
                                             'basketurl': basketurl,
                                             'noteurl': noteurl}

    @staticmethod
    def get_share_message(serialized_history_element):
        """
        Returns a message used while sharing basket note history on
        web-interface.

        @see: L{HistoryElement.get_share_message}
        """
        title = get_record_title(serialized_history_element[2])
        recordurl = url_for('record.metadata',
                            recid=serialized_history_element[2])
        basketurl = (CFG_SITE_SECURE_URL
                     + "/yourbaskets/display?bskid=%s"
                     % serialized_history_element[0])
        noteurl = (CFG_SITE_SECURE_URL
                   + "/yourbaskets/display?bskid=%s&recid=%s"
                   % (serialized_history_element[0],
                      serialized_history_element[2]))
        return _(CFG_SHARE_MSGS[20]) % {'title': title,
                                        'recordurl': recordurl,
                                        'basketname':
                                        serialized_history_element[1],
                                        'basketurl': basketurl,
                                        'noteurl': noteurl}


COLLECTOR = BasketNoteHistory
