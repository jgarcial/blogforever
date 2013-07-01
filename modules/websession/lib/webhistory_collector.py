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
# pylint: disable=E1111
"""
Base class for history collectors.
"""
from invenio.search_engine_utils import get_fieldvalues
from invenio.webinterface_handler_flask_utils import _
from invenio.webuser_flask import current_user


def get_record_title(recid):
    """
    Returns the the title of the record with given id. If the title cannot be
    found, returns "a page".

    @param recid: The ID of the record
    @type recid: int

    @rtype: str
    """
    try:
        return get_fieldvalues(recid, "245___")[0].decode("utf-8", "replace")
    except Exception:
        return _("a page")


class HistoryElement:
    """
    Represents a history entry that is displayed on web-interface.
    """
    def __init__(self, date, entry):
        """
        @param date: The date of the entry.
        @type date: L{datetime}

        @param entry: The database entry represented by this L{HistoryElement}
        @type entry: L{sqlalchemy.util._collections.NamedTuple}
        """

        #: @ivar: The date of the entry.
        #: @type: L{datetime}
        self.date = date

        #: @ivar: The database entry represented by this L{HistoryElement}
        #: @type: L{sqlalchemy.util._collections.NamedTuple}
        self.entry = entry

        #: @ivar: The ID of the entry
        #: @type: int
        self.id = None

        #: @ivar: The type of the history.
        #: @type: str
        self.history_type = None

        #: @ivar: The icon that will be displayed near the history message on
        #: the web-interface.
        #: @type: str
        #: @see: U{http://twitter.github.io/bootstrap/base-css.html#icons}
        self.icon = "error"

        #: @ivar: The message that is displayed on the web-interface.
        #: type: str
        self.msg = ""

        #: @ivar: Serialized history element
        #: type: list
        self.serialized = []


class HistoryCollector:
    """
    The base class for the history collector plugins.

    All of the plugins should be inherited from this class.
    """

    #: @ivar: Retrieved L{HistoryElement}§
    #: @type: [L{HistoryElement}]
    _history_elems = None

    #: @ivar: The number of times the database entries are retrieved.
    #: @type: int
    _round = 0

    #: @ivar: the number of entries to be retrieved at a time.
    #: @type: int
    _limit = 10

    #: @ivar: the id of the user
    #: @type: int
    _uid = 0

    #: @ivar: The initial date to collect user history
    #: @type: L{datetime}
    _filter_from = None

    #: @ivar: The final date to collect user history
    #: @type: L{datetime}
    _filter_to = None

    #: @ivar: Index of the first unused entry.
    #: @type: int
    _current_history_elem = 0

    #: The icon that will be displayed near the history message in the
    #: webinterface.
    #: @type: str
    #: @see: U{http://twitter.github.io/bootstrap/base-css.html#icons}
    icon = "error"

    #: The label for filtering the corresponding collector.
    #: @type: str
    label = 'No Label'

    def __init__(self, limit=10, filter_from=None, filter_to=None):
        """
        @param limit: The number of entries to be retrieved at a time.
        @type: int

        @param filter_from: The initial date to collect user history
        @type: L{datetime}

        @param filter_to: The final date to collect user history
        @type: L{datetime}
        """
        self._limit = limit
        self._filter_from = filter_from
        self._filter_to = filter_to
        self._uid = current_user.get_id()

        self._history_elems = []
        self._extend_history_elems()

    def _extend_history_elems(self):
        """
        Gets more entries from database
        """
        history = self.get_user_history(self._limit,
                                        self._limit * self._round,
                                        self._filter_from,
                                        self._filter_to)
        for hst in history:
            self._history_elems.append(HistoryElement(self.__class__
                                                      .get_date(hst),
                                                      entry=hst))
        self._round += 1

    def check(self):
        """
        Returns the most recent L{HistoryElement}. If not found, returns None

        @rtype: L{HistoryElement} or None
        """
        try:
            return self._history_elems[self._current_history_elem]
        except IndexError:
            self._extend_history_elems()
            try:
                return self._history_elems[self._current_history_elem]
            except IndexError:
                return None

    def use(self):
        """
        Fills the required attributes of the most recent L{HistoryElement} and
        returns it.

        @rtype: L{HistoryElement}
        """
        elem = self._history_elems[self._current_history_elem]
        elem.id = self.__class__.get_id(elem.entry)
        elem.history_type = self.__class__.__name__
        elem.icon = self.icon
        elem.msg = self.__class__.get_message(elem.entry)
        elem.serialized = self.__class__.serialize(elem.entry)
        self._current_history_elem += 1
        return elem

    def get_user_history(self, limit, offset, filter_from, filter_to):
        """
        Retrieves and returns entries from database.

        @param uid: The ID of the user.
        @type uid: int

        @param limit: The number of entries to be retrieved.
        @type limit: int

        @param offset: The offset of the entries to be retrieved.
        @type offset: int

        @param filter_from: The initial date to retrieve database entries.
        @type filter_from: L{datetime}

        @param filter_to: The final date to retrieve database entries.
        @type filter_to: L{datetime}

        @rtype: [L{sqlalchemy.util._collections.NamedTuple}]
        """
        pass

    @staticmethod
    def get_id(entry):
        """
        Returns the ID of the given entry.

        @type entry: L{sqlalchemy.util._collections.NamedTuple}

        @rtype: int or str
        """
        pass

    @staticmethod
    def serialize(entry):
        """
        Serializes the given entry as a list to used it later.
        (e.g. constructing share message)

        @type entry: L{sqlalchemy.util._collections.NamedTuple}

        @rtype: list
        """
        pass

    @staticmethod
    def get_date(entry):
        """
        Returns the date of the given entry.

        @type entry: L{sqlalchemy.util._collections.NamedTuple}

        @rtype: L{datetime}
        """
        pass

    @staticmethod
    def get_message(entry):
        """
        Returns the message displayed on "Your Activities" page.

        @type entry: L{sqlalchemy.util._collections.NamedTuple}

        @rtype: str
        """
        pass

    @staticmethod
    def get_share_message(serialized_history_element):
        """
        Returns a message for sharing an activity.

        @param serialized_history_element: L{HistoryElement} serialized by
            L{serialize} method.
        @type serialized_history_element: list

        @rtype: str
        """
        pass
