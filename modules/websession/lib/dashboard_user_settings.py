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

"""Dashboard User Settings"""

from flask import Blueprint, session, make_response, g, render_template, \
                  request, flash, jsonify, redirect, url_for, current_app
from invenio.websession_model import User
from invenio.webinterface_handler_flask_utils import _
from invenio.webuser_flask import current_user
from invenio.jinja2utils import render_template_to_string
from invenio.settings import Settings, UserSettingsStorage, \
                             ModelSettingsStorageBuilder, \
                             UserSettingsAttributeStorage
from invenio.websession_model import User
from invenio.webaccount_forms import ChangeUserEmailSettingsForm

class DashboardSettings(Settings):

    keys = ['orderLeft', 'orderMiddle', 'orderRight']
    storage_builder = UserSettingsAttributeStorage('dashboard_settings')
    widget = None
    def __init__(self):
        super(DashboardSettings, self).__init__()
        self.icon = 'user'
        self.title = _('Dashboard')


    @property
    def is_authorized(self):
        return current_user.is_authenticated()

## Compulsory plugin interface
settings = DashboardSettings
#__all__ = ['DashboardSettings']
