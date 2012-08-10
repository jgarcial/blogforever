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
Configuration variables for webpayment modules.
"""

from invenio.config import CFG_CREDIT_CARD_PAYMENT_GATEWAY
from invenio.config import CFG_USE_PAYPAL_EXPRESS_CHECKOUT
from invenio.webpayment_ogone import Ogone
from invenio.webpayment_paypal import PayPal

CFG_CREDIT_CARD_PAYMENT_METHODS = {
    'PAYPAL': PayPal,
    'OGONE': Ogone
}
"""
Payment gateways to use checking out with credit card

@note: use only upper case characters in keys
@type: dict
"""


CFG_PAYMENT_METHODS = {
    'cc': CFG_CREDIT_CARD_PAYMENT_METHODS.get(CFG_CREDIT_CARD_PAYMENT_GATEWAY
                                              .upper(), None),
    PayPal.name: PayPal if int(CFG_USE_PAYPAL_EXPRESS_CHECKOUT) else None
}
"""
Payment method classes

@note: use only cc and name of the payment gateways in keys.
@type: dict
"""


CFG_WEBPAYMENT_MSGS = {
    0: "This repository is completely free...",
    1: "You have successfully purchased the premium package. "
        "Please note that your transaction ID is %s",
    2: "Transaction failed.",
    3: "No premium package is required to display %s."
}
"""
Messages that is used for webpayment module.

@type: dict
"""
