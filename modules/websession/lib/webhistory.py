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
Contains HistoryManager class.
"""
from datetime import datetime
from datetime import timedelta
from flask import jsonify
from invenio.config import CFG_PYLIBDIR
from invenio.config import CFG_WEBHISTORY_DATETIME_FORMAT
from invenio.pluginutils import PluginContainer
from invenio.webhistory_collector import HistoryCollector
from invenio.webhistory_config import CFG_WEBHISTORY_JSON_DATETIME_FORMAT
from invenio.webhistory_config import CFG_WEBHISTORY_JSON_DATE_FORMAT
import os


def _invenio_history_collector_plugin_builder(plugin_name, plugin_code):
    """
    Handy function to bridge pluginutils with (Invenio) history collectors.
    """
    if 'COLLECTOR' in dir(plugin_code):
        candidate = getattr(plugin_code, 'COLLECTOR')
        if not candidate:
            return None
        if issubclass(candidate, HistoryCollector):
            return candidate
    raise ValueError('%s is not a valid collector plugin' % plugin_name)


#: All of the history collector plugins.
#: @type: L{PluginContainer}
_COLLECTOR_PLUGINS = PluginContainer(
    os.path.join(CFG_PYLIBDIR, 'invenio', '*_history.py'),
    plugin_builder=_invenio_history_collector_plugin_builder)

#: The list of the available L{HistoryCollector}s.
#: @type: list
HISTORY_COLLECTORS = []

#: The list of the names of the available L{HistoryCollector}s.
#: @type: list
HISTORY_FILTER_NAMES = []


def _gather_history_collectors():
    """
    Fills the HISTORY_COLLECTORS and HISTORY_FILTER_NAMES global variables.
    """
    global HISTORY_COLLECTORS
    global HISTORY_FILTER_NAMES
    HISTORY_COLLECTORS = [collector
                          for (dummy, collector) in _COLLECTOR_PLUGINS.items()
                          if collector]

    HISTORY_FILTER_NAMES = [collector.__name__
                            for collector in HISTORY_COLLECTORS
                            if collector]
_gather_history_collectors()


class HistoryManager:
    """
    Collects and sorts the history of the user.
    """

    #: @ivar: The list of the L{HistoryCollector}s containing at least one
    #: history element
    #: @type: list
    _active_collectors = None

    #: @ivar: The number of history elements to be collected.
    #: @type: int
    _total_nb = 0

    #: @ivar: The final date to collect user history
    #: @type: L{datetime}
    _filter_to = None

    #: @ivar: The history elements collected.
    #: @type: [L{HistoryElement}]
    _history_elems = None

    #: @ivar: The ID of the last L{HistoryElement} displayed.
    #: @type: int
    _after_id = None

    def __init__(self, total_nb=10, filters=None, filter_from=None,
                 filter_to=None, after_id=0):
        """
        @param total_nb: The number of L{HistoryElement}s to be gathered.
        @type total_nb: int

        @param filters: The list of the class names of L{HistoryCollector}s
            that will be used.
        @type filters: [str]

        @param filter_from: The initial date to collect user history
        @type filter_from: str

        @param filter_to: The final date to collect user history
        @type filter_to: str

        @param after_id: Some tables contains entries with the same dates. If
            this one and filter_to parameters are given, tries to find the
            L{HistoryElement} with this id and date, removes more recent
            L{HistoryElement}s if found.
        @type after_id: int
        """
        self._active_collectors = []
        self._total_nb = total_nb
        try:
            self._after_id = int(after_id)
        except:
            self._after_id = None
        if filter_from:
            try:
                fmt = CFG_WEBHISTORY_JSON_DATE_FORMAT
                filter_from = datetime.strptime(filter_from, fmt)
            except (ValueError, TypeError):
                filter_from = None

        try:
            if filter_to and len(filter_to) == 10:
                fmt = CFG_WEBHISTORY_JSON_DATE_FORMAT
                self._filter_to = datetime.strptime(filter_to, fmt)
                self._filter_to += timedelta(seconds=59, minutes=59, hours=23)
            elif filter_to:
                fmt = CFG_WEBHISTORY_JSON_DATETIME_FORMAT
                self._filter_to = datetime.strptime(filter_to, fmt)
        except (ValueError, TypeError):
            filter_to = None

        for collector in HISTORY_COLLECTORS:
            if not filters or collector.__name__ in filters:
                instance = collector(limit=total_nb,
                                     filter_from=filter_from,
                                     filter_to=self._filter_to)
                if instance.check():
                    self._active_collectors.append(instance)

    def get_user_history(self):
        """
        Returns the list of the L{HistoryElement}s of the user.

        @rtype: [L{HistoryElement}]
        """
        if self._history_elems:
            return self._history_elems

        self._history_elems = []
        recent_index = 0
        index = 1
        remove_necessary = self._after_id
        collector_nb = len(self._active_collectors)

        while (collector_nb and len(self._history_elems) < self._total_nb
               or remove_necessary):

            # Get the most recent HistoryElement.
            while index < collector_nb:
                if (self._active_collectors[index].check().date
                    > (self._active_collectors[recent_index]
                       .check()
                       .date)):
                    recent_index = index
                index += 1

            history_elem = (self._active_collectors[recent_index]
                            .check())

            # If the history element has the same date with the recent history
            # element shown, it appends the found list.
            # Otherwise, it finds and removes the history elements that are
            # already shown. Makes this operation only once since there is no
            # need to check after the first remove operation.
            if (remove_necessary and history_elem.date != self._filter_to):
                self._remove_displayed()
                remove_necessary = False
                if len(self._history_elems) >= self._total_nb:
                    break

            self._history_elems.append(self._active_collectors[recent_index]
                                       .use())

            # If there is no history left on the collector, removes it from the
            # active collector list.
            if not self._active_collectors[recent_index].check():
                self._active_collectors.pop(recent_index)
                collector_nb -= 1

                # If there is no collector left and still need to remove
                # displayed history elements, remove them and finalize
                # collecting operation.
                if not collector_nb and remove_necessary:
                    self._remove_displayed()
                    break

            recent_index = 0
            index = 1

        return self._history_elems[0:self._total_nb]

    def has_more_history(self):
        """
        Returns if the user has more L{HistoryElement}s.

        @rtype: bool
        """
        for collector in self._active_collectors:
            if collector.check():
                return True

        return False

    def _remove_displayed(self):
        """
        Removes history elements that are returned before.
        """
        for index in range(len(self._history_elems)):
            if self._after_id == self._history_elems[index].id:
                for dummy in range(index + 1):
                    self._history_elems.pop(0)
                return

    def get_user_history_json(self):
        """
        Returns user history as JSON format.
        """
        if not self._history_elems:
            self.get_user_history()

        ret = {}

        json_fmt = CFG_WEBHISTORY_JSON_DATETIME_FORMAT
        fmt = CFG_WEBHISTORY_DATETIME_FORMAT

        for i in range(len(self._history_elems)):
            ret[str(i)] = {'type': self._history_elems[i].history_type,
                           'serialized': (self._history_elems[i]
                                                .serialized),
                           'icon': self._history_elems[i].icon,
                           'msg': self._history_elems[i].msg,
                           'serialized_date': (datetime
                                               .strftime(self._history_elems[i]
                                                         .date,
                                                         json_fmt)),
                           'date': datetime.strftime(self._history_elems[i]
                                                     .date,
                                                     fmt)}

        if len(self._history_elems) < self._total_nb:
            ret['has_more'] = 0
        else:
            ret['has_more'] = self.has_more_history() and 1 or 0

        if self._history_elems:
            ret['last_id'] = self._history_elems[-1].id

        return jsonify(**ret)

    @staticmethod
    def get_share_message(history_type, serialized_share_message):
        """
        Returns a message for sharing an activity. If history type is not
        valid, returns an empty string.

        @param history_type: The class name of the history collector.
        @type history_type: str

        @param serialized_share_message: The list consisting of the identifiers
            to be used to construct the message.
        @type serialized_share_message: list

        @rtype: str
        """
        for collector in HISTORY_COLLECTORS:
            if collector.__name__ == history_type:
                return collector.get_share_message(serialized_share_message)
        return ""
