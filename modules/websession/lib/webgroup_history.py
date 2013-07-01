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
Collector for group history of the user

@undocumented: COLLECTOR
"""
from flask import url_for
from invenio.sqlalchemyutils import db
from invenio.webhistory_collector import HistoryCollector
from invenio.webhistory_config import CFG_SHARE_MSGS
from invenio.webhistory_config import CFG_WEBHISTORY_MSGS
from invenio.webinterface_handler_flask_utils import _
from invenio.websession_model import UserUsergroup
from invenio.websession_model import Usergroup
from sqlalchemy.sql import expression


class GroupHistory(HistoryCollector):
    """
    Collects joining/creating groups history
    """
    icon = 'tags'
    label = 'Groups'

    @staticmethod
    def get_date(x):
        return x.user_status_date

    @staticmethod
    def get_id(x):
        return x.id

    @staticmethod
    def serialize(x):
        return [x.user_status, x.name]

    def get_user_history(self, limit, offset, filter_from, filter_to):
        """
        Returns the joining/creating groups history of the user with given id

        @see: L{HistoryCollector.get_user_history}
        """
        group_history = (db.session
                         .query(Usergroup.id,
                                Usergroup.name,
                                UserUsergroup.user_status,
                                UserUsergroup.user_status_date)
                         .filter(Usergroup.id == UserUsergroup.id_usergroup)
                         .filter(UserUsergroup.id_user == self._uid))

        if filter_from:
            group_history = group_history.filter(UserUsergroup.user_status_date
                                                 >= filter_from)

        if filter_to:
            group_history = group_history.filter(UserUsergroup.user_status_date
                                                 <= filter_to)

        group_history = (group_history
                         .order_by(expression.desc(UserUsergroup
                                                   .user_status_date))
                         .limit(limit)
                         .offset(offset)
                         .all())

        return group_history

    @staticmethod
    def get_message(entry):
        """
        Returns a message to display group history on web-interface.

        @see: L{HistoryElement.get_message}
        """
        groupurl = url_for('webgroup.index')
        if entry.user_status == 'A':
            return _(CFG_WEBHISTORY_MSGS[14]) % {'groupname': entry.name,
                                                 'groupurl': groupurl}
        else:
            return _(CFG_WEBHISTORY_MSGS[15]) % {'groupname': entry.name,
                                                 'groupurl': groupurl}

    @staticmethod
    def get_share_message(serialized_history_element):
        """
        Returns a message used while sharing group history on
        web-interface.

        @see: L{HistoryElement.get_share_message}
        """
        groupurl = url_for('webgroup.index')
        if serialized_history_element[0] == 'A':
            return _(CFG_SHARE_MSGS[14]) % {'groupname':
                                            serialized_history_element[1],
                                            'groupurl': groupurl}
        else:
            return _(CFG_SHARE_MSGS[15]) % {'groupname':
                                            serialized_history_element[1],
                                            'groupurl': groupurl}

COLLECTOR = GroupHistory
