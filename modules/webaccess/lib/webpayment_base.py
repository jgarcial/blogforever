# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2012, 2013 CERN.
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
The base class for the payment gateways.
"""
from invenio.config import CFG_SITE_SECURE_URL


class PaymentGateway:
    """
    Base class for payment gateways.

    @note: process method should be overridden if the payment gateway is used
           for buying with credit card.

    @note: construct_checkout_url, get_transaction_details and
           complete_transaction methods should be overridden if the payment
           redirects the user to a 3rd party site to complete the payment
    """

    #: The url of the api test server
    #:
    #: @type: str
    TEST_SERVER = None

    #: The url of the api server
    #:
    #: @type: str
    SERVER = None

    #: Some gateways require additional inputs different than credit card
    #: informations. The L{InvenioBaseForm} to take additional information
    #: should be given with this variable.
    #:
    #: @type: L{InvenioBaseForm}
    #:
    #: @see: L{PaypalCreditCardForm}
    #: @see: L{OGoneCreditCardForm}
    _additional_form = None

    #: The name of the gateway
    #:
    #: @type: str
    name = None

    #: @ivar: Premium package on transaction.
    #:
    #: @type: L{Premium}
    premium_package = None

    #: @ivar: Form returned from payment gateway after transaction is
    #: completed.
    #:
    #: @type: dict or str
    form = None

    #: @ivar: Credit card form that contains information to but premium
    #: package.
    #:
    #: @type: L{CreditCardForm}
    credit_card_form = None

    #: @ivar: Response of the payment gateway
    #:
    #: @type: L{PaymentGatewayResponse}
    _response = None

    #: The image of the "pay with" button
    #:
    #: @type: str
    _button_img = CFG_SITE_SECURE_URL + "/img/credit_card.png"

    #: url of VISA icon
    #:
    #. @type: str
    VISA = CFG_SITE_SECURE_URL + "/img/visa.png"

    #:  url of MASTERCARD icon
    #:
    #: @type: str
    MASTERCARD = CFG_SITE_SECURE_URL + "/img/mastercard.png"

    #: url of DISCOVER icon
    #:
    #: @type: str
    DISCOVER = CFG_SITE_SECURE_URL + "/img/discover.png"

    #: url of AMERICANEXPRESS icon
    #:
    #: @type: str
    AMERICANEXPRESS = CFG_SITE_SECURE_URL + "/img/americanexpress.png"

    #: url of MAESTRO icon
    #:
    #: @type: str
    MAESTRO = CFG_SITE_SECURE_URL + "/img/maestro.png"

    #: The credit card types accepted.
    #:
    #: @type: list
    _accept_types = [VISA, MASTERCARD, DISCOVER, AMERICANEXPRESS, MAESTRO]

    def __init__(self, form=None, credit_card_form=None):
        """
        Initialize credit card and premium package information

        @param form: the form returned from payment gateway api.
        @type form: dict

        @param credit_card_form: The form contains information to pay with
        credit card.
        @type credit_card_form: L{CreditCardForm}
        """
        from invenio.webpayment_query import get_premium_package

        self.form = form
        self.credit_card_form = credit_card_form

        id_package = (self.form and
                      self.form['id_package'] or
                      self.credit_card_form and
                      self.credit_card_form.id_package.data or
                      None)
        if id_package:
            self.premium_package = get_premium_package(id_package)

    def process(self):
        """
        This method should make the credit card transaction and return the
        response including transaction ID if succeeded, error messages if
        failed.

        @rtype: L{PaymentGatewayResponse}

        @see: L{PayPal}

        @note: This method should be overridden if the payment gateway is used
        for buying with credit card.
        """
        raise Exception(self)

    def construct_checkout_url(self):
        """
        This method should return the response with 3rd party site URL to
        checkout in the 'data' field of the response.

        If fails, it should return response with error messages.

        @note: The return URL when calling the payment gateway api should be in
        the form of B{CFG_SITE_SECURE_URL/webpayment/review?id_package=self.\
        premium_package.id&payment_method=self.name}

        @note: If you want to show the user what s/he is buying, the endpoint
        should be I{review} and override get_transaction_details, or you may
        complete the payment after returning from 3rd party site by setting
        endpoint as I{complete}.

        @rtype: L{PaymentGatewayResponse}
        """
        raise Exception(self)

    def get_transaction_details(self, form):
        """
        Should check if the transaction is appropriate for the payment gateway.
        If it is, should return the HTML code of the button for completing the
        transaction in 'data' key of the response. Otherwise, it should return
        a response with error messages.

        @note: If you want to skip this step, just don't override this
        function.

        @rtype: L{PaymentGatewayResponse}
        """
        raise Exception(self, form)

    def complete_transaction(self, form):
        """
        This method should complete the transaction. If succeeded, should
        return a response with transaction ID. Otherwise, should return a
        response with error messages.

        @rtype: L{PaymentGatewayResponse}
        """
        raise Exception(self, form)

    def _set_response(self, success=False):
        """
        Constructs the response of the payment gateway

        @param success: if the transaction is succeeded of not.
        @type success: bool
        """
        self._response = PaymentGatewayResponse(self.premium_package,
                                                success=success)

    def get_response(self):
        """
        Returns the response

        @rtype L{PaymentGatewayResponse}
        """
        return self._response

    def is_response_successful(self):
        """
        Returns if the response is secceeded

        @rtype bool
        """
        return self._response.get('success', False)

    def set_transaction_id(self, id_transaction):
        """
        Sets the succeeded transaction id.

        @param id_transaction: the ID of the transaction
        @type id_transaction: str
        """
        self._response['id_transaction'] = "%s-%s" % (self.name,
                                                      id_transaction)

    def add_error_message(self, error_msg):
        """
        Adds the error message if the transaction is failed.

        @param error_msg: An error message
        @type error_msg: str
        """
        self._response['error_messages'].append(error_msg)

    def complete_payment(self, id_user, payment_method):
        """
        Completes the payment, registers the payment history, give the user the
        right to access corresponding collections or extends the membership.

        @param id_user: the id of the user
        @type id_user: int

        @param payment_method: the name of the payment method
        @type payment_method: str
        """
        from invenio.webpayment import grant_user_access
        from invenio.webpayment import register_payment_history

        register_payment_history(id_user,
                                 self.premium_package,
                                 payment_method,
                                 self._response['id_transaction'])

        grant_user_access(id_user, self.premium_package)

    @classmethod
    def get_additional_form(cls):
        """
        Returns the additional inputs

        @rtype: list
        """
        if cls._additional_form:
            return cls._additional_form
        else:
            return None

    def _generate_order_id(self):
        """
        Generates a random string started with payment gateway name.

        @rtype: str
        """
        from random import choice
        generate = lambda: reduce((lambda x, y: x + y),
                                  [choice("qwertyuiopasdfghj"
                                          "klzxcvbnm1234567890")
                                   for dummy in range(16)])
        return "%s-%s" % (self.name, generate())

    @classmethod
    def get_button_img(self, name):
        """
        Returns the HTML code of the "Pay with this payment gateway" button.
        """
        if name == 'cc':
            out = ''
            for card in self._accept_types:
                out += '<img class="payment_method" src="%s" />' % card
            return out
        else:
            return '<img class="payment_method" src="%s"/>' % self._button_img


class PaymentGatewayResponse(dict):
    """
    This class is a dict which ensures the required keys are constructed to use
    it as the response of the payment gateway.
    """
    def __init__(self, premium_package, success):
        """
        @param premium_package: the information about premium package
        @type premium_package: L{Premium}

        @param success: whether the response is succeeded or not
        @type success: bool
        """
        dict.__init__(self)
        self['premium_package'] = premium_package
        self['success'] = success
        self['id_transaction'] = None
        self['error_messages'] = []
        self['data'] = None
