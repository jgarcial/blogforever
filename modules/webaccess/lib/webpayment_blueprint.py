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
The endpoints for the webpayment module.

Endpoints
=========
    - /
    - /complete
    - /display
    - /display/<int:collection_id>
    - /review
    - /upgrade

@note: Base endpoint is /webpayment
"""
from datetime import date
from datetime import datetime
from flask import request, redirect, flash, abort
from flask.helpers import url_for
from invenio.config import CFG_PREMIUM_SERVICE
from invenio.webinterface_handler_flask_utils import InvenioBlueprint
from invenio.webinterface_handler_flask_utils import _
from invenio.webpayment import get_membership_expiration_dates
from invenio.webpayment import get_package_collection_map
from invenio.webpayment import get_possible_packages
from invenio.webpayment_config import CFG_PAYMENT_METHODS
from invenio.webpayment_config import CFG_WEBPAYMENT_MSGS
from invenio.webpayment_forms import CreditCardForm
from invenio.webpayment_query import get_all_premium_packages
from invenio.webpayment_query import get_all_premium_restricted_collections
from invenio.webpayment_query import get_premium_package
from invenio.webpayment_query import get_premium_restricted_collections
from invenio.websearch_model import Collection
from invenio.webuser_flask import current_user
from urllib2 import URLError

blueprint = InvenioBlueprint('webpayment',
                             __name__,
                             url_prefix="/webpayment",
                             breadcrumbs=[(_("Your Account"),
                                           'youraccount.display'),
                                          ('Your Premium Memberships',
                                           'webpayment.display')],
                             menubuilder=(CFG_PREMIUM_SERVICE
                                          and
                                          [('personalize.webpayment',
                                          _('Your premium memberships'),
                                          'webpayment.index', 20)]
                                          or None))


def duration_formatter(x):
    """
    Formats the duration of the given premium package.

    @param x: premium package whose duration is formatted.
    @type x: L{Premium}

    @rtype: str
    """
    return ((x.unit_time.upper() == "UNLIMITED") and
            "Unlimited" or
            (str(x.duration) + " "
             + x.unit_time.capitalize()
             + (x.duration > 1 and "s" or "")))


@blueprint.route('/display/<int:collection_id>', methods=['GET'])
@blueprint.invenio_set_breadcrumb(_("Purchase a premium package"))
@blueprint.invenio_templated('webpayment_display.html')
def display(collection_id):
    """
    Displays the premium packages that allow the user access the collection
    with given id.

    @param collection_id: the ID of the collection
    @type collection_id: int
    """
    if not CFG_PREMIUM_SERVICE:
        return redirect(url_for('search.index'))

    premium_packages = get_possible_packages(collection_id)

    if not premium_packages:
        collection_name = (Collection.query
                           .filter(Collection.id == collection_id)
                           .first_or_404().name)
        flash(_(CFG_WEBPAYMENT_MSGS[3]) % collection_name, 'success')
        return redirect(url_for('search.index'))

    package_collection_map = get_package_collection_map()
    payment_methods = []
    for payment in CFG_PAYMENT_METHODS.keys():
        if CFG_PAYMENT_METHODS[payment]:
            payment_methods.append((payment,
                                    CFG_PAYMENT_METHODS[payment].
                                    get_button_img(payment)))

    return dict(premium_packages=premium_packages,
                duration_formatter=duration_formatter,
                package_collection_map=package_collection_map,
                payment_methods=payment_methods)


@blueprint.route('/upgrade', methods=['GET'])
@blueprint.route('/display', methods=['GET'])
@blueprint.route('/', methods=['GET'])
@blueprint.invenio_templated('webpayment_index.html')
def index():
    """
    Displays the current status of the premium packages of the users and
    displays all of the premium packages.
    """
    if not CFG_PREMIUM_SERVICE:
        return redirect(url_for('search.index'))

    uid = current_user.get_id()
    premium_collections = get_all_premium_restricted_collections()

    if not premium_collections:
        flash(_(CFG_WEBPAYMENT_MSGS[0]), 'success')
        return redirect(url_for('search.index'))

    expiration_dates = get_membership_expiration_dates(uid)
    user_memberships = {}
    for collection in premium_collections:
        user_memberships[collection.id] = {}
        user_memberships[collection.id]['collection_name'] = collection.name

    for date in expiration_dates:
        try:
            user_memberships[date[0]]['expiration_date'] = date[1]
        except:
            # Restriction of the collection is removed...
            pass

    for id_collection in user_memberships.keys():
        if user_memberships[id_collection].get('expiration_date', None):
            user_memberships[id_collection]['is_expired'] = (
                datetime.now() > user_memberships[id_collection]
                ['expiration_date'])
            user_memberships[id_collection]['has_purchased'] = True
        else:
            user_memberships[id_collection]['has_purchased'] = False

    premium_packages = get_all_premium_packages()
    package_collection_map = get_package_collection_map()
    payment_methods = []
    for payment in CFG_PAYMENT_METHODS.keys():
        if CFG_PAYMENT_METHODS[payment]:
            payment_methods.append((payment,
                                    CFG_PAYMENT_METHODS[payment].
                                    get_button_img(payment)))

    return dict(user_memberships=user_memberships,
                duration_formatter=duration_formatter,
                premium_packages=premium_packages,
                package_collection_map=package_collection_map,
                payment_methods=payment_methods,
                str=str)


@blueprint.route('/upgrade', methods=['POST'])
@blueprint.invenio_templated('webpayment_upgrade.html')
@blueprint.invenio_set_breadcrumb(_("Purchase a premium package"))
@blueprint.invenio_wash_urlargd({'payment_method': (unicode, "cc"),
                                 'id_package': (int, 0)})
def upgrade(payment_method, id_package):
    """
    Makes the credit card transaction or redirects the user to the 3rd party
    site.
    """
    if not CFG_PREMIUM_SERVICE:
        return redirect(url_for('search.index'))
    form = CreditCardForm(request.values)
    if (payment_method == 'cc'):
        form.additional = CFG_PAYMENT_METHODS['cc'].get_additional_form()
        premium_package = get_premium_package(id_package)
        restricted_collections = get_premium_restricted_collections(id_package)

        if not form.csrf_token.data or form.validate():
            return dict(duration_formatter=duration_formatter,
                        premium_package=premium_package,
                        form=form,
                        restricted_collections=restricted_collections)
        else:
            uid = current_user.get_id()
            payment_gateway = CFG_PAYMENT_METHODS['cc'](credit_card_form=form)
            try:
                result = payment_gateway.process()
                if result['success']:
                    payment_gateway.complete_payment(uid, "Credit Card")
                    flash(_(CFG_WEBPAYMENT_MSGS[1])
                          % str(result['id_transaction']),
                          "info")
                    return redirect(url_for('webpayment.index'))
                else:
                    return dict(duration_formatter=duration_formatter,
                                premium_package=premium_package,
                                form=form,
                                error_messages=result["error_messages"],
                                restricted_collections=restricted_collections)
            except URLError:
                flash(_("Payment gateway cannot be reached at the moment, "
                    "please try again later."), "error")
                return redirect(url_for('webpayment.index'))
    else:
        payment_gateway = CFG_PAYMENT_METHODS[payment_method](form=request
                                                              .values)
        try:
            res = payment_gateway.construct_checkout_url()
        except URLError:
            flash(_("%s cannot be reached at the moment, "
                    "please try again later.") % payment_method, "error")
            return redirect(url_for('webpayment.index'))

        return redirect(res['data'])


@blueprint.route('/review', methods=['GET', 'POST'])
@blueprint.invenio_templated('webpayment_review.html')
@blueprint.invenio_wash_urlargd({'payment_method': (unicode, "")})
@blueprint.invenio_set_breadcrumb(_("Confirm payment"))
def review(payment_method):
    """
    Display the review page before completing the transaction.

    @param payment_method: the name of the payment method.
    @type payment_method: str
    """
    if not CFG_PREMIUM_SERVICE:
        return redirect(url_for('search.index'))
    try:
        payment_method = CFG_PAYMENT_METHODS[payment_method](form=request.args)

        result = payment_method.get_transaction_details(request.args)
        if result['success']:
            return dict(result=result,
                        premium_package=payment_method.premium_package,
                        duration_formatter=duration_formatter)
        else:
            for msg in result.get('error_messages', []):
                flash(msg, "error")
            return redirect(url_for('webpayment.index'))
    except:
        return abort(404)


@blueprint.route('/complete', methods=['GET', 'POST'])
@blueprint.invenio_wash_urlargd({'payment_method': (unicode, "")})
def complete(payment_method):
    """
    Completes the transaction.

    @param payment_method: the name of the payment method.
    @type payment_method: str
    """
    if not CFG_PREMIUM_SERVICE:
        return redirect(url_for('search.index'))
    uid = current_user.get_id()
    payment_method = CFG_PAYMENT_METHODS[payment_method](form=request.args)

    result = payment_method.complete_transaction(request.args)

    if result['success']:
        payment_method.complete_payment(uid, payment_method.name)
        flash(_(CFG_WEBPAYMENT_MSGS[1]) % str(result['id_transaction']),
              "info")
        return redirect(url_for('webpayment.index'))
    else:
        flash(_(CFG_WEBPAYMENT_MSGS[2]), "error")
        for msg in result.get('error_messages', []):
            flash(msg, "error")
        return redirect(url_for('webpayment.index'))
