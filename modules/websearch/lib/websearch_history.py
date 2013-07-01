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
Collector for search history of the user

@undocumented: COLLECTOR
"""
from cgi import parse_qs
from invenio.config import CFG_SITE_SECURE_URL
from invenio.sqlalchemyutils import db
from invenio.webhistory_collector import HistoryCollector
from invenio.webhistory_config import CFG_SHARE_MSGS
from invenio.webhistory_config import CFG_WEBHISTORY_MSGS
from invenio.webinterface_handler_flask_utils import _
from invenio.websearch_model import UserQuery
from invenio.websearch_model import WebQuery
from sqlalchemy.sql import expression


class SearchHistory(HistoryCollector):
    """
    Collects search history
    """
    icon = 'search'
    label = 'Your Searches'

    @staticmethod
    def get_date(x):
        return x.date

    @staticmethod
    def get_id(x):
        return x.id_query

    @staticmethod
    def serialize(x):
        return x.urlargs

    def get_user_history(self, limit, offset, filter_from, filter_to):
        """
        Returns user's search history.
        """
        searches = (db.session
                    .query(UserQuery.date,
                           WebQuery.urlargs,
                           UserQuery.id_query)
                    .filter(UserQuery.id_user == self._uid)
                    .filter(UserQuery.id_query == WebQuery.id))

        if filter_from:
            searches = searches.filter(UserQuery.date >= filter_from)

        if filter_to:
            searches = searches.filter(UserQuery.date <= filter_to)

        searches = (searches
                    .order_by(expression.desc(UserQuery.date))
                    .limit(limit)
                    .offset(offset)
                    .all())

        return searches

    @staticmethod
    def get_message(entry):
        """
        Returns a message to display search history on web-interface.

        @see: L{HistoryElement.get_message}
        """
        pattern = parse_qs(entry.urlargs)
        if 'p' in pattern.keys():
            pattern = pattern['p'][0]
        else:
            pattern = ''

        searchurl = (CFG_SITE_SECURE_URL + "/search?"
                     + entry.urlargs.replace(' ', '%20'))

        if pattern:
            return _(CFG_WEBHISTORY_MSGS[22]) % {'searchurl': searchurl,
                                                 'pattern': pattern}
        else:
            return _(CFG_WEBHISTORY_MSGS[23]) % {'searchurl': searchurl}

    @staticmethod
    def get_share_message(serialized_history_element):
        """
        Returns a message used while sharing search history on
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

        if pattern:
            return _(CFG_SHARE_MSGS[22]) % {'searchurl': searchurl,
                                            'pattern': pattern}
        else:
            return _(CFG_SHARE_MSGS[23]) % {'searchurl': searchurl}

COLLECTOR = SearchHistory
