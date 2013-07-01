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
"""WebHistory Flask Blueprint"""

from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from invenio.webhistory import HISTORY_COLLECTORS
from invenio.webhistory import HISTORY_FILTER_NAMES
from invenio.webhistory import HistoryManager
from invenio.webhistory_config import CFG_WEBHISTORY_DATEPICKER_DATETIME
from invenio.webhistory_user_settings import WebHistorySettings
from invenio.webinterface_handler_flask_utils import _, InvenioBlueprint
from invenio.webmessage_forms import AddMsgMESSAGEForm
from invenio.webuser_flask import current_user

blueprint = InvenioBlueprint('webhistory',
                             __name__,
                             url_prefix="/youractivities",
                             breadcrumbs=[(_("Your Activities"),
                                           'webhistory.index')],
                             menubuilder=[('personalize.history',
                                           _('Your activites'),
                                           'webhistory.index', 30)])


@blueprint.route('/')
@blueprint.route('/index', methods=['GET', 'POST'])
@blueprint.route('/display', methods=['GET', 'POST'])
@blueprint.invenio_wash_urlargd({'filter_from': (unicode, None),
                                 'filter_to': (unicode, None)})
@blueprint.invenio_authenticated
def index(filter_from=None, filter_to=None):
    """
    The main page of the "Your Activities".

    @param filter_from: The initial date to collect user history
    @type filter_from: unicode

    @param filter_to: The final date to collect user history
    @type filer_to: unicode
    """
    filter_labels = {}
    for item in HISTORY_COLLECTORS:
        filter_labels[item.__name__] = {'icon': item.icon,
                                        'label': item.label}

    history_settings = current_user.get('history_settings', {})
    active_filters = history_settings.get('active_filters',
                                          HISTORY_FILTER_NAMES)

    try:
        per_page = int(history_settings.get('per_page'))
    except:
        per_page = 10

    share_form = AddMsgMESSAGEForm()

    return render_template('webhistory_index.html',
                           share_form=share_form,
                           per_page=per_page,
                           filter_from=filter_from,
                           filter_to=filter_to,
                           active_filters=active_filters,
                           filter_labels=filter_labels,
                           datepicker_fmt=CFG_WEBHISTORY_DATEPICKER_DATETIME)


@blueprint.route('/filter', methods=['GET', 'POST'])
@blueprint.invenio_authenticated
def filteractivities():
    """
    Stores the filter preferences of the user to the database.
    """
    plugin = WebHistorySettings()
    plugin.store(request.form)
    plugin.save()
    return redirect(url_for('webhistory.index',
                            filter_from=request.form.get("filter_from"),
                            filter_to=request.form.get("filter_to")))


@blueprint.route('/getmore', methods=['GET', 'POST'])
@blueprint.invenio_wash_urlargd({'oldest': (unicode, None),
                                 'filter_from': (unicode, None),
                                 'filter_to': (unicode, None),
                                 'after_id': (unicode, None)})
@blueprint.invenio_authenticated
def getmore(oldest=None, filter_from=None, filter_to=None, after_id=0):
    """
    Returns the entries which are older than the oldest displayed one to user
    as JSON.

    @param oldest: The date of the oldest displayed history entry to the user.
    @type oldest: unicode

    @param filter_from: The initial date to collect user history
    @type filter_from: unicode

    @param filter_to: The final date to collect user history
    @type filter_to: unicode

    @param after_id: The id of the oldest displayed history entry to the user.
    @type after_id: unicode
    """
    history_settings = current_user.get('history_settings', {})
    active_filters = history_settings.get('active_filters',
                                          HISTORY_FILTER_NAMES)

    try:
        per_page = int(history_settings.get('per_page'))
    except:
        per_page = 10

    if oldest and filter_to:
        if filter_to + " 23:59:59" > oldest:
            filter_to = oldest
    elif oldest:
        filter_to = oldest

    try:
        after_id = int(after_id)
    except:
        after_id = None

    history_manager = HistoryManager(total_nb=per_page,
                                     filters=active_filters,
                                     filter_from=filter_from,
                                     filter_to=filter_to,
                                     after_id=after_id)

    return history_manager.get_user_history_json()


@blueprint.route('/getsharemessage', methods=['GET', 'POST'])
@blueprint.invenio_wash_urlargd({'history_type': (unicode, None)})
@blueprint.invenio_authenticated
def getsharemessage(history_type=None):
    """
    Returns the share message for the given serialized L{HistoryElement}.

    @param history_type: The type of the history.
        (i.e. class name of the history collector)
    @type history_type: unicode
    """
    serialized = request.values.getlist('serialized')
    return HistoryManager.get_share_message(history_type, serialized)
