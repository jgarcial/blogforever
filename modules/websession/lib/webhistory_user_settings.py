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
from flask import url_for
from invenio.jinja2utils import render_template_to_string
from invenio.settings import Settings
from invenio.settings import UserSettingsAttributeStorage
from invenio.webhistory import HISTORY_FILTER_NAMES
from invenio.webhistory import HistoryManager
from invenio.webinterface_handler_flask_utils import _
from invenio.webuser_flask import current_user
"""
WebHistory User Settings

@undocumented: settings
"""


class WebHistorySettings(Settings):
    keys = ['active_filters', 'per_page']
    storage_builder = UserSettingsAttributeStorage('history_settings')

    def __init__(self):
        super(WebHistorySettings, self).__init__()
        self.icon = 'calendar'
        self.title = _('Your Activities')
        self.view = url_for('webhistory.index')

    def widget(self):
        history_settings = current_user.get('history_settings', {})
        active_filters = history_settings.get('active_filters',
                                              HISTORY_FILTER_NAMES)

        history_manager = HistoryManager(total_nb=10,
                                         filters=active_filters)

        history = history_manager.get_user_history()

        template = """
<table class="table table-striped table-bordered">
    {%- for h in history -%}
        <tr>
            <td><i class="icon-{{h.icon}}"></i></td>
            <td>{{ h.msg | safe }}</td>
        </tr>
    {%- endfor -%}
</table>
        """

        return render_template_to_string(template,
                                         history=history,
                                         _from_string=True)

    @property
    def is_authorized(self):
        return current_user.is_authenticated()

## Compulsory plugin interface
settings = WebHistorySettings
