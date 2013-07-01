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
Collector for user's history of records added into webbasket

@undocumented: COLLECTOR
"""
from flask import url_for
from invenio.config import CFG_SITE_SECURE_URL
from invenio.sqlalchemyutils import db
from invenio.webbasket_model import BskBASKET
from invenio.webbasket_model import BskREC
from invenio.webhistory_collector import HistoryCollector
from invenio.webhistory_collector import get_record_title
from invenio.webhistory_config import CFG_SHARE_MSGS
from invenio.webhistory_config import CFG_WEBHISTORY_MSGS
from invenio.webinterface_handler_flask_utils import _
from sqlalchemy.sql import expression


class BasketAddHistory(HistoryCollector):
    """
    Collects history of the records added into webbasket
    """
    icon = 'bookmark'
    label = 'Adding into Basket'

    @staticmethod
    def get_date(x):
        return x.date_added

    @staticmethod
    def get_id(x):
        return x.id_bibrec_or_bskEXTREC

    @staticmethod
    def serialize(x):
        return [x.id, x.name, x.id_bibrec_or_bskEXTREC]

    def get_user_history(self, limit, offset, filter_from, filter_to):
        """
        Returns user's history of records added into webbasket.
        """
        baskets = (db.session
                   .query(BskREC.id_bibrec_or_bskEXTREC,
                          BskREC.date_added,
                          BskBASKET.name,
                          BskBASKET.id)
                   .filter(BskREC.id_user_who_added_item == self._uid)
                   .filter(BskBASKET.id == BskREC.id_bskBASKET))

        if filter_from:
            baskets = baskets.filter(BskREC.date_added >= filter_from)

        if filter_to:
            baskets = baskets.filter(BskREC.date_added <= filter_to)

        baskets = (baskets
                   .order_by(expression.desc(BskREC.date_added))
                   .limit(limit)
                   .offset(offset)
                   .all())

        return baskets

    @staticmethod
    def get_message(entry):
        """
        Returns a message to display history of records added into
        webbasket on web-interface.

        @see: L{HistoryElement.get_message}
        """
        title = get_record_title(entry.id_bibrec_or_bskEXTREC)
        recordurl = url_for('record.metadata',
                            recid=entry.id_bibrec_or_bskEXTREC)
        basketurl = (CFG_SITE_SECURE_URL
                     + "/yourbaskets/display?bskid=%s" % entry.id)
        return _(CFG_WEBHISTORY_MSGS[19]) % {'title': title,
                                             'recordurl': recordurl,
                                             'basketname': entry.name,
                                             'basketurl': basketurl}

    @staticmethod
    def get_share_message(serialized_history_element):
        """
        Returns a message used while sharing history of records added into
        webbasket on web-interface.

        @see: L{HistoryElement.get_share_message}
        """
        title = get_record_title(serialized_history_element[2])
        recordurl = url_for('record.metadata',
                            recid=serialized_history_element[2])
        basketurl = (CFG_SITE_SECURE_URL
                     + "/yourbaskets/display?bskid=%s"
                     % serialized_history_element[0])
        return _(CFG_SHARE_MSGS[19]) % {'title': title,
                                        'recordurl': recordurl,
                                        'basketname':
                                        serialized_history_element[1],
                                        'basketurl': basketurl}

COLLECTOR = BasketAddHistory
