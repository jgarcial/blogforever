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
from flask import Blueprint, session, make_response, g, render_template, \
                  request, flash, jsonify, redirect, url_for, current_app
from invenio.jinja2utils import render_template_to_string
from invenio.jinja2utils import render_template_to_string
from invenio.settings import Settings, UserSettingsStorage, \
                             ModelSettingsStorageBuilder
from invenio.sqlalchemyutils import db
from invenio.webaccount_forms import ChangeUserEmailSettingsForm
from invenio.webinterface_handler_flask_utils import _
from invenio.websession_model import User
from invenio.webuser_flask import current_user
from invenio.webrecommend import get_recommended_content

"""WebBasket User Settings"""


class WebRecommendSettings(Settings):

    keys = []
    storage_builder = UserSettingsStorage

    def __init__(self):
        super(WebRecommendSettings, self).__init__()
        self.icon = 'thumbs-up'
        self.title = _('Recommended For You')

    def widget(self):
        uid = current_user.get_id()
        records = get_recommended_content(uid)

        template = """
<ul>
{%- for record in records -%}
<li>
    <a href="{{config.CFG_SITE_SECURE_URL}}/{{config.CFG_SITE_RECORD}}/{{record['id']}}">{{record['title']}}</a>
</li>
{%- endfor -%}
</ul>
"""
        return render_template_to_string(template, _from_string=True, records=records)

    widget.size = 4

    @property
    def is_authorized(self):
        return current_user.is_authenticated() and \
               current_user.is_authorized('usebaskets')

## Compulsory plugin interface
settings = WebRecommendSettings
#__all__ = ['WebBasketSettings']
