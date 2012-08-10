# -*- coding: utf-8 -*-
##s
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
"""
WebPayment User Settings
"""

from flask import url_for
from invenio.jinja2utils import render_template_to_string
from invenio.settings import Settings, UserSettingsStorage
from invenio.webinterface_handler_flask_utils import _
from invenio.webmessage_forms import WebMessageUserSettingsForm
from invenio.webpayment import get_user_premium_membership
from invenio.webuser_flask import current_user
from invenio.config import CFG_PREMIUM_SERVICE


class WebPaymentSettings(Settings):

    keys = ['payment_premium']
    storage_builder = UserSettingsStorage
    form_builder = WebMessageUserSettingsForm

    def __init__(self):
        super(WebPaymentSettings, self).__init__()
        self.icon = 'money'
        self.title = _('Premium Memberships')
        self.view = url_for('webpayment.index')

    def widget(self):
        uid = current_user.get_id()
        total, user = get_user_premium_membership(uid)
        template = """You are able to display {{user}} of
total {{total}} premium collection{{'' if total==1 else 's'}}."""
        return render_template_to_string(template,
                                         total=total,
                                         user=user,
                                         _from_string=True)

    widget.size = 4

    @property
    def is_authorized(self):
        return current_user.is_authenticated()

## Compulsory plugin interface
if CFG_PREMIUM_SERVICE:
    settings = WebPaymentSettings
else:
    settings = None
#__all__ = ['WebMessageSettings']
