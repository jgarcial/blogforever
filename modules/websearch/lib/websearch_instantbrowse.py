# -*- coding: utf-8 -*-

## This file is part of Invenio.
## Copyright (C) 2011 CERN.
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

from invenio.dbquery import run_sql

class InstantBrowseManager():
    """
    InstantBrowseManager is the responsible of
    manage the available plugins used to list the latest
    additions for each collection.
    """

    def set_instantbrowse_plugin(self, collection_id, instantbrowse_plugin, instantbrowse_optional_params=""):
        """
        Set given plugin and the given optional parameters
        for the corresponding collection to list its
        latest additions.
        @param collection_id: collection id
        @type: string
        @param instantbrowse_plugin: plugin name
        @type instantbrowse_plugin: string
        @param instantbrowse_optional_params: optional plugin parameters
        @type instantbrowse_optional_params: string
        """

        run_sql("REPLACE INTO collection_instantbrowse SET \
                    collection_id=%s, instantbrowse_plugin=%s, instantbrowse_optional_params=%s", \
                    (collection_id, "websearch_" + instantbrowse_plugin, instantbrowse_optional_params))

    def get_instantbrowse_plugin(self, collection_id):
        """
        Return the plugin that will be used for the
        given collection and the parameters needed to run it.
        @param collection_id: collection id
        @type collection_id: string
        @return: tuple (instantbrowse_plugin, instantbrowse_optional_params)
        @rtype: tuple
        """

        res = run_sql("SELECT instantbrowse_plugin,instantbrowse_optional_params \
                            FROM collection_instantbrowse \
                            WHERE collection_id=%s", (collection_id, ))
        if res:
            return res[0]
        return None

instantbrowse_manager = InstantBrowseManager()
