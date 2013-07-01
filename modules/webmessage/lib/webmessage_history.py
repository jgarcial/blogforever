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
Collector for message history of the user

@undocumented: COLLECTOR
"""
from flask import url_for
from invenio.webhistory_collector import HistoryCollector
from invenio.webhistory_config import CFG_SHARE_MSGS
from invenio.webhistory_config import CFG_WEBHISTORY_MSGS
from invenio.webinterface_handler_flask_utils import _
from invenio.webmessage_model import MsgMESSAGE
from sqlalchemy.sql import expression


class MessageHistory(HistoryCollector):
    """
    Collects message history
    """
    icon = 'envelope'
    label = 'Messages'

    @staticmethod
    def get_date(x):
        return x.sent_date

    @staticmethod
    def get_id(x):
        return x.id

    @staticmethod
    def serialize(x):
        return x.id

    def get_user_history(self, limit, offset, filter_from, filter_to):
        """
        Returns user's message history.
        """
        # pylint: disable=E1101
        messages = (MsgMESSAGE
                    .query
                    .filter(MsgMESSAGE.id_user_from == self._uid))
        # pylint: enable=E1101

        if filter_from:
            messages = messages.filter(MsgMESSAGE.sent_date >= filter_from)

        if filter_to:
            messages = messages.filter(MsgMESSAGE.sent_date <= filter_to)

        messages = (messages
                    .order_by(expression.desc(MsgMESSAGE.sent_date))
                    .limit(limit)
                    .offset(offset)
                    .all())

        return messages

    @staticmethod
    def get_message(entry):
        """
        Returns a message to display message history on web-interface.

        @see: L{HistoryElement.get_message}
        """
        msgurl = url_for('webmessage.view', msgid=entry.id)
        usernames = entry.sent_to_user_nicks
        groupnames = entry.sent_to_group_names
        if usernames and groupnames:
            if entry.subject:
                return _(CFG_WEBHISTORY_MSGS[2]) % {'msgurl': msgurl,
                                                    'usernames': usernames,
                                                    'subject': entry.subject,
                                                    'groupnames': groupnames}
            else:
                return _(CFG_WEBHISTORY_MSGS[5]) % {'msgurl': msgurl,
                                                    'usernames': usernames,
                                                    'groupnames': groupnames}
        elif usernames:
            if entry.subject:
                return _(CFG_WEBHISTORY_MSGS[0]) % {'msgurl': msgurl,
                                                    'usernames': usernames,
                                                    'subject': entry.subject}
            else:
                return _(CFG_WEBHISTORY_MSGS[3]) % {'msgurl': msgurl,
                                                    'usernames': usernames}
        else:
            if entry.subject:
                return _(CFG_WEBHISTORY_MSGS[1]) % {'msgurl': msgurl,
                                                    'subject': entry.subject,
                                                    'groupnames': groupnames}
            else:
                return _(CFG_WEBHISTORY_MSGS[4]) % {'msgurl': msgurl,
                                                    'groupnames': groupnames}

    @staticmethod
    def get_share_message(serialized_history_element):
        """
        Returns a message used while sharing message history on
        web-interface.

        @see: L{HistoryElement.get_share_message}
        """
        # pylint: disable=E1101
        entry = MsgMESSAGE.query.get(serialized_history_element)
        # pylint: enable=E1101
        usernames = entry.sent_to_user_nicks
        groupnames = entry.sent_to_group_names
        if usernames and groupnames:
            if entry.subject:
                return _(CFG_SHARE_MSGS[2]) % {'usernames': usernames,
                                               'subject': entry.subject,
                                               'groupnames': groupnames}
            else:
                return _(CFG_SHARE_MSGS[5]) % {'usernames': usernames,
                                               'groupnames': groupnames}
        elif usernames:
            if entry.subject:
                return _(CFG_SHARE_MSGS[0]) % {'usernames': usernames,
                                               'subject': entry.subject}
            else:
                return _(CFG_SHARE_MSGS[3]) % {'usernames': usernames}
        else:
            if entry.subject:
                return _(CFG_SHARE_MSGS[1]) % {'subject': entry.subject,
                                               'groupnames': groupnames}
            else:
                return _(CFG_SHARE_MSGS[4]) % {'groupnames': groupnames}

COLLECTOR = MessageHistory
