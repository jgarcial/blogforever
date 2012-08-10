#-*- coding: utf-8 -*-
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

"""WebAccess Admin Flask Blueprint"""

from flask import redirect, url_for, request
from invenio.webaccess_model import AccACTION, AccROLE
from invenio.webpayment_model import Premium, HstPAYMENT
from invenio.websession_model import User, UserUsergroup, Usergroup
from invenio.webinterface_handler_flask_utils import _, InvenioBlueprint

from invenio.webuser_flask import current_user
from sqlalchemy.sql import operators, expression, functions
from sqlalchemy.orm import exc
from invenio.websearch_model import Collection, CollectionCollection
from invenio.webpayment_forms import PremiumPackageForm, GiftPremiumPackageForm
from invenio import webpayment_query as webpayment_db
from invenio import webpayment

from invenio.access_control_config import \
    WEBACCESSACTION

blueprint = InvenioBlueprint('webaccess_admin', __name__,
                             url_prefix="/admin/webaccess",
                             config='invenio.access_control_config',
                             breadcrumbs=[(_('Administration'), 'help.admin'),
                                          (_('WebAccess'), 'webaccesss_admin.index')],
                             menubuilder=[('main.admin.webaccess',
                                          _('Configure WebAccess'),
                                          'webaccess_admin.index', 90)])


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.invenio_authenticated
@blueprint.invenio_authorized(WEBACCESSACTION)
@blueprint.invenio_templated('webaccess_admin_index.html')
def index():
    actions = [
        dict(url=url_for('.rolearea'),
             title=_('Role Area'),
             description=_('Main area to configure administration rights and authorization rules.')),
        dict(url=url_for('.actionarea'),
             title=_('Action Area'),
             description=_('Configure administration rights with the actions as starting point.')),
        dict(url=url_for('.userarea'),
             title=_('User Area'),
             description=_('Configure administration rights with the users as starting point.')),
        dict(url=url_for('.resetarea'),
             title=_('Reset Area'),
             description=_('Reset roles, actions and authorizations.')),
        dict(url=url_for('.manageaccounts'),
             title=_('Manage Accounts Area'),
             description=_('Manage user accounts.')),
        dict(url=url_for('.delegate_startarea'),
             title=_('Delegate Rights - With Restrictions'),
             description=_('Delegate your rights for some roles.')),
        dict(url=url_for('.managerobotlogin'),
             title=_('Manage Robot Login'),
             description=_('Manage robot login keys and test URLs.')),
        dict(url=url_for('.premiumarea'),
             title=_('Premium Area'),
             description=_('Manage premium packages'))
        ]
    return dict(actions=actions)


@blueprint.route('/actionarea', methods=['GET', 'POST'])
@blueprint.invenio_authenticated
@blueprint.invenio_authorized(WEBACCESSACTION)
@blueprint.invenio_sorted(AccACTION)
@blueprint.invenio_templated('webaccess_admin_actionarea.html')
def actionarea(sort=False, filter=None):
    if sort is False:
        sort = AccACTION.name
    actions = AccACTION.query.order_by(sort).filter(filter).all()
    return dict(actions=actions)


@blueprint.route('/rolearea', methods=['GET', 'POST'])
@blueprint.invenio_authenticated
@blueprint.invenio_authorized(WEBACCESSACTION)
@blueprint.invenio_sorted(AccROLE)
@blueprint.invenio_templated('webaccess_admin_rolearea.html')
def rolearea(sort=False, filter=None):
    if sort is False:
        sort = AccROLE.name
    roles = AccROLE.query.order_by(sort).filter(filter).all()
    return dict(roles=roles)


@blueprint.route('/showroledetails/<int:id_role>', methods=['GET', 'POST'])
@blueprint.invenio_authenticated
@blueprint.invenio_authorized(WEBACCESSACTION)
@blueprint.invenio_templated('webaccess_admin_showroledetails.html')
def showroledetails(id_role):
    return dict(role=AccROLE.query.get_or_404(id_role))


@blueprint.route('/userarea', methods=['GET', 'POST'])
@blueprint.invenio_authenticated
@blueprint.invenio_authorized(WEBACCESSACTION)
@blueprint.invenio_sorted(User)
@blueprint.invenio_templated('webaccess_admin_userarea.html')
def userarea(sort=False, filter=None):
    if sort is False:
        sort = User.nickname
    users = User.query.order_by(sort).filter(filter).all()
    return dict(users=users)


@blueprint.route('/resetarea', methods=['GET', 'POST'])
def resetarea():
    #FIXME reimplement this function
    return redirect('/admin/webaccess/webaccessadmin.py/resetarea')


@blueprint.route('/manageaccounts', methods=['GET', 'POST'])
def manageaccounts():
    #FIXME reimplement this function
    return redirect('/admin/webaccess/webaccessadmin.py/manageaccounts')


@blueprint.route('/delegate_startarea', methods=['GET', 'POST'])
def delegate_startarea():
    #FIXME reimplement this function
    return redirect('/admin/webaccess/webaccessadmin.py/delegate_startarea')


@blueprint.route('/managerobotlogin', methods=['GET', 'POST'])
def managerobotlogin():
    #FIXME reimplement this function
    return redirect('/admin/webaccess/webaccessadmin.py/managerobotlogin')


@blueprint.route('/premiumarea', methods=['GET', 'POST'])
@blueprint.invenio_authenticated
@blueprint.invenio_authorized(WEBACCESSACTION)
@blueprint.invenio_templated('webaccess_admin_premiumarea.html')
def premiumarea():
    form = PremiumPackageForm(request.values)
    gift_form = GiftPremiumPackageForm(request.values)

    if request.method == 'POST':
        if request.args.get('page', None) == 'packages' and form.validate():
            if not form.package_id.data:  # Add new one
                webpayment.add_new_premium_package(form)
            else:  # Update existing one
                webpayment.edit_premium_package(form)
        if request.args.get('page', None) == 'users' and gift_form.validate():
            webpayment.gift_premium_package(gift_form)

    premium_packages = webpayment_db.get_all_premium_packages()
    package_collection_map = webpayment.get_package_collection_map()
    history = webpayment_db.get_payment_history()
    transaction_number = webpayment_db.get_total_transaction_number()
    total_revenue = webpayment_db.get_total_revenue()
    premium_user_number = webpayment_db.get_premium_user_number()
    users = webpayment_db.get_premium_users()

    return dict(premium_packages=premium_packages,
                package_collection_map=package_collection_map,
                history=history,
                users=users,
                premium_user_number=premium_user_number,
                transaction_number=transaction_number,
                total_revenue=total_revenue,
                form=form,
                gift_form=gift_form,
                page=request.args.get('page', None))


@blueprint.route('/premiumarea/delete', methods=['POST'])
@blueprint.invenio_authenticated
@blueprint.invenio_authorized(WEBACCESSACTION)
@blueprint.invenio_wash_urlargd({'id_package': (int, 0)})
def delete_premium_package(id_package):
    if id_package <= 0:
        return "Could not found premium package with id %s" % id_package, 404

    try:
        webpayment.delete_premium_package(id_package)
        return ""
    except:
        return "Could not delete the premium package with id %s" % id_package, 404


@blueprint.route('/premiumarea/movedown', methods=['PUT'])
@blueprint.invenio_authenticated
@blueprint.invenio_authorized(WEBACCESSACTION)
@blueprint.invenio_wash_urlargd({'id_package': (int, 0)})
def move_premium_package_down(id_package):
    if id_package <= 0:
        return "Could not found premium package with id %s" % id_package, 404

    try:
        webpayment_db.move_package_down(id_package)
        return ""
    except exc.NoResultFound:
        return "The package is already last", 404


@blueprint.route('/premiumarea/moveup', methods=['PUT'])
@blueprint.invenio_authenticated
@blueprint.invenio_authorized(WEBACCESSACTION)
@blueprint.invenio_wash_urlargd({'id_package': (int, 0)})
def move_premium_package_up(id_package):
    if id_package <= 0:
        return "Could not found premium package with id %s" % id_package, 404

    try:
        webpayment_db.move_package_up(id_package)
        return ""
    except exc.NoResultFound:
        return "The package is already first", 404


@blueprint.route('/premiumarea/gift', methods=['POST'])
@blueprint.invenio_authenticated
@blueprint.invenio_authorized(WEBACCESSACTION)
@blueprint.invenio_wash_urlargd({'username': (unicode, ''),
                                 'premium_package': (int, 0)})
def gift_premium_package(username, premium_package):
    webpayment.gift_premium_package(username, premium_package)
    return redirect(url_for('.premiumarea'))
