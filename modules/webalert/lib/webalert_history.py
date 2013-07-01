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
Collector for alert history.

@undocumented: COLLECTOR
"""
from cgi import parse_qs
from invenio.config import CFG_SITE_SECURE_URL
from invenio.sqlalchemyutils import db
from invenio.webalert_model import UserQueryBasket
from invenio.webhistory_collector import HistoryCollector
from invenio.webhistory_config import CFG_SHARE_MSGS
from invenio.webhistory_config import CFG_WEBHISTORY_MSGS
from invenio.webinterface_handler_flask_utils import _
from invenio.websearch_model import WebQuery
from sqlalchemy.sql import expression


class AlertHistory(HistoryCollector):
    """
    Collects alert history
    """
    icon = 'time'
    label = 'Alerts'

    @staticmethod
    def get_date(entry):
        return entry.date_creation

    @staticmethod
    def get_id(entry):
        return entry.id_query

    @staticmethod
    def serialize(entry):
        return entry.urlargs

    def get_user_history(self, limit, offset, filter_from, filter_to):
        """
        Returns user's alert history.
        """
        alerts = (db.session
                  .query(UserQueryBasket.date_creation,
                         WebQuery.urlargs,
                         UserQueryBasket.id_query)
                  .filter(UserQueryBasket.id_user == self._uid)
                  .filter(UserQueryBasket.id_query == WebQuery.id))

        if filter_from:
            alerts = alerts.filter(UserQueryBasket.date_creation
                                   >= filter_from)

        if filter_to:
            alerts = alerts.filter(UserQueryBasket.date_creation <= filter_to)

        alerts = (alerts
                  .order_by(expression.desc(UserQueryBasket.date_creation))
                  .limit(limit)
                  .offset(offset)
                  .all())

        return alerts

    @staticmethod
    def get_message(entry):
        """
        Returns a message to display alert history on web-interface.

        @see: L{HistoryElement.get_message}
        """
        pattern = parse_qs(entry.urlargs)
        if 'p' in pattern.keys():
            pattern = pattern['p'][0]
        else:
            pattern = ''

        alerturl = CFG_SITE_SECURE_URL + "/youralerts/list"

        return _(CFG_WEBHISTORY_MSGS[21]) % {'alerturl': alerturl,
                                             'pattern': pattern}

    @staticmethod
    def get_share_message(serialized_history_element):
        """
        Returns a message used while sharing alert history on
        web-interface.

        @see: L{HistoryElement.get_share_message}
        """
        pattern = parse_qs(serialized_history_element[0])
        if 'p' in pattern.keys():
            pattern = pattern['p'][0]
        else:
            pattern = ''

        searchurl = (CFG_SITE_SECURE_URL + "/search?"
                     + serialized_history_element[0].replace(' ', '%20'))

        return _(CFG_SHARE_MSGS[21]) % {'searchurl': searchurl,
                                        'pattern': pattern}

COLLECTOR = AlertHistory
