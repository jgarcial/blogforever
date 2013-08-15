# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2012 CERN.
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

"""WebSearch User Settings"""

from flask import Blueprint, session, make_response, g, render_template, \
                  request, flash, jsonify, redirect, url_for, current_app
from invenio.webinterface_handler_flask_utils import _
from invenio.sqlalchemyutils import db
from invenio.jinja2utils import render_template_to_string
from invenio.websearch_model import WebQuery, UserQuery
from invenio.websearch_forms import WebSearchUserSettingsForm
from invenio.webuser_flask import current_user
from invenio.settings import Settings, UserSettingsStorage, \
                             ModelSettingsStorageBuilder

class WebSearchSettings(Settings):

    keys = ['rg', 'websearch_hotkeys', 'c']
    form_builder = WebSearchUserSettingsForm
    storage_builder = UserSettingsStorage

    def __init__(self):
        super(WebSearchSettings, self).__init__()
        self.icon = 'search'
        self.title = _('Searches')
        self.view = url_for('webaccount.index')
        self.edit = url_for('webaccount.edit', name=__name__.split('.')[-1])

    def widget(self):
        uid = current_user.get_id()
        queries = db.session.query(db.func.count(UserQuery.id_query)).filter(
            UserQuery.id_user == uid
            ).scalar()

        template = """
{{ _('You have made %d queries. A detailed list is available with a possibility to
(a) view search results and (b) subscribe to an automatic email alerting service
for these queries.') | format(queries) }}
"""

        return render_template_to_string(template, _from_string=True,
                                         queries=queries)

    widget.size = 4

    @property
    def is_authorized(self):
        return not current_user.is_guest

## Compulsory plugin interface
settings = WebSearchSettings
#__all__ = ['WebSearchSettings']
