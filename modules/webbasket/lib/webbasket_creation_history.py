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
Collector for basket creation history of the user

@undocumented: COLLECTOR
"""
from invenio.config import CFG_SITE_SECURE_URL
from invenio.sqlalchemyutils import db
from invenio.webbasket_model import BskBASKET
from invenio.webbasket_model import UserBskBASKET
from invenio.webhistory_collector import HistoryCollector
from invenio.webhistory_config import CFG_SHARE_MSGS
from invenio.webhistory_config import CFG_WEBHISTORY_MSGS
from invenio.webinterface_handler_flask_utils import _
from sqlalchemy.sql import expression


class BasketCreationHistory(HistoryCollector):
    """
    Collects basket creation history
    """
    icon = 'plus'
    label = 'Basket Creation/Subscription'

    @staticmethod
    def get_date(x):
        return x.creation_date

    @staticmethod
    def get_id(x):
        return x.id

    @staticmethod
    def serialize(x):
        return [x.id, x.name, x.action_code]

    def get_user_history(self, limit, offset, filter_from, filter_to):
        """
        Returns user's basket note history.
        """
        baskets = (db.session
                   .query(UserBskBASKET.creation_date,
                          UserBskBASKET.action_code,
                          BskBASKET.name,
                          BskBASKET.id)
                   .filter(UserBskBASKET.id_user == self._uid)
                   .filter(BskBASKET.id == UserBskBASKET.id_bskBASKET))

        if filter_from:
            baskets = baskets.filter(UserBskBASKET.creation_date
                                     >= filter_from)

        if filter_to:
            baskets = baskets.filter(UserBskBASKET.creation_date <= filter_to)

        baskets = (baskets
                   .order_by(expression.desc(UserBskBASKET.creation_date))
                   .limit(limit)
                   .offset(offset)
                   .all())

        return baskets

    @staticmethod
    def get_message(entry):
        """
        Returns a message to display basket creation history on web-interface.

        @see: L{HistoryElement.get_message}
        """
        basketurl = (CFG_SITE_SECURE_URL
                     + "/yourbaskets/display?bskid=%s" % entry.id)
        if entry.action_code == 'C':
            return _(CFG_WEBHISTORY_MSGS[17]) % {'basketname': entry.name,
                                                 'basketurl': basketurl}
        else:
            return _(CFG_WEBHISTORY_MSGS[18]) % {'basketname': entry.name,
                                                 'basketurl': basketurl}

    @staticmethod
    def get_share_message(serialized_history_element):
        basketurl = (CFG_SITE_SECURE_URL
                     + "/yourbaskets/display?bskid=%s"
                     % serialized_history_element[0])
        if serialized_history_element[2] == 'C':
            return _(CFG_SHARE_MSGS[17]) % {'basketname':
                                            serialized_history_element[1],
                                            'basketurl': basketurl}
        else:
            return _(CFG_SHARE_MSGS[18]) % {'basketname':
                                            serialized_history_element[1],
                                            'basketurl': basketurl}

COLLECTOR = BasketCreationHistory
