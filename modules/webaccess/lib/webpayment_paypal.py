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
"""
PayPal class to make payment requests from PayPal
"""
from invenio.config import CFG_PAYPAL_API_PASSWORD, CFG_PAYPAL_API_SIGNATURE, \
    CFG_PAYPAL_API_USERNAME, CFG_PAYPAL_API_VERSION, CFG_PREMIUM_SERVICE, \
    CFG_SITE_NAME, CFG_SITE_SECURE_URL, CFG_TEST_PREMIUM_SERVICE
from invenio.webpayment_base import PaymentGateway
from invenio.webpayment_forms import PaypalCreditCardForm
import cgi
import urllib
import urllib2


class PayPal(PaymentGateway):
    """
    Contains methods to use PayPal API
    """
    name = "Paypal"

    #: The prefix of the error codes of the data returned from paypal api.
    #:
    #: @type: str
    ERRORCODE_PREFIX = "L_ERRORCODE"

    #: The prefix of the error messages of the data returned from paypal api.
    #:
    #: @type: str
    MESSAGE_PREFIX = "L_LONGMESSAGE"

    TEST_SERVER = "https://api-3t.sandbox.paypal.com/nvp"
    SERVER = "https://api-3t.paypal.com/nvp"

    #: The test url of express checkout api.
    #:
    #: @type: str
    PAYPAL_EXPRESS_CHECKOUT_TEST = ("https://www.sandbox.paypal.com/cgi-bin/"
                                    "webscr")

    #: The url of express checkout api.
    #:
    #: @type: str
    PAYPAL_EXPRESS_CHECKOUT = "https://www.paypal.com/cgi-bin/webscr"

    _button_img = CFG_SITE_SECURE_URL + "/img/paypal_checkout.gif"

    _accept_types = [
        PaymentGateway.VISA,
        PaymentGateway.MASTERCARD,
        PaymentGateway.AMERICANEXPRESS,
        PaymentGateway.DISCOVER
    ]

    _additional_form = PaypalCreditCardForm

    def __init__(self, form=None, credit_card_form=None):
        """
        Initialization

        @param form: the form returned from paypal api.
        @type form: dict

        @param credit_card_form: The form contains information to pay with
        credit card.
        @type credit_card_form: L{CreditCardForm}
        """
        PaymentGateway.__init__(self, form=form,
                                credit_card_form=credit_card_form)

        if not int(CFG_PREMIUM_SERVICE):
            self._request_url = None
            self._express_checkout_url = None
        elif int(CFG_TEST_PREMIUM_SERVICE):
            self._request_url = self.TEST_SERVER
            self._express_checkout_url = self.PAYPAL_EXPRESS_CHECKOUT_TEST
        else:
            self._request_url = self.SERVER
            self._express_checkout_url = self.PAYPAL_EXPRESS_CHECKOUT

    def process(self):
        """
        Makes the request to "pay with credit card".
        """
        values = {
            'USER': CFG_PAYPAL_API_USERNAME,
            'PWD': CFG_PAYPAL_API_PASSWORD,
            'SIGNATURE': CFG_PAYPAL_API_SIGNATURE,
            'VERSION': '91.0',
            # DoDirectPayment Request Fields
            'METHOD': 'DoDirectPayment',
            'PAYMENTACTION': 'Sale',
            'IPADDRESS': '192.168.0.1',
            # Credit Card Details Fields
            'ACCT': self.credit_card_form.card_number.data,
            'EXPDATE': "%s%s" % (self.credit_card_form.expiration_month.data
                                 .zfill(2),
                                 self.credit_card_form.expiration_year.data),
            'CVV2': self.credit_card_form.cvv.data,
            # Payer Information Fields
            'FIRSTNAME': str(self.credit_card_form.additional().first_name
                             .data),
            'LASTNAME': str(self.credit_card_form.additional().last_name.data),
            # Address Fields
            'STREET': str(self.credit_card_form.additional().street.data),
            'CITY': str(self.credit_card_form.additional().city.data),
            'STATE': str(self.credit_card_form.additional().state.data),
            'COUNTRYCODE': str(self.credit_card_form.additional().country
                               .data),
            'ZIP': str(self.credit_card_form.additional().postal_code.data),
            # Payment Details Fields
            'AMT': "%.2f" % self.premium_package.price,
            'CURRENCYCODE': self.premium_package.currency,
            'ITEMAMT': self.premium_package.price,
            # Payment Details Item Fields
            'L_NAME0': self.premium_package.name,
            'L_DESC0': self.premium_package.details,
            'L_AMT0': "%.2f" % self.premium_package.price,
            'L_QTY0': '1',
        }

        params = urllib.urlencode(values)
        request = urllib2.Request(self._request_url, params)
        response = cgi.parse_qs(urllib2.urlopen(request).read())
        self._set_response(response['ACK'][0] == 'Success')
        if self.is_response_successful():
            self.set_transaction_id(response['TRANSACTIONID'][0])
        else:
            self._extract_error_messages(response)

        return self.get_response()

    def construct_checkout_url(self):
        """
        Constructs url to checkout with PayPal.

        @see: U{https://www.x.com/developers/paypal/documentation-tools/api/
        setexpresscheckout-api-operation-nvp}
        """
        # Parameters to get token from paypal
        values = {
            'USER': CFG_PAYPAL_API_USERNAME,
            'PWD': CFG_PAYPAL_API_PASSWORD,
            'SIGNATURE': CFG_PAYPAL_API_SIGNATURE,
            'VERSION': CFG_PAYPAL_API_VERSION,
            'METHOD': 'SetExpressCheckout',
            'RETURNURL': (CFG_SITE_SECURE_URL + "/webpayment/review"
                          + "?id_package="
                          + str(self.premium_package.id)
                          + "&payment_method="
                          + self.name),
            'CANCELURL': CFG_SITE_SECURE_URL + '/youraccount/',
            'REQCONFIRMSHIPPING': 0,
            'NOSHIPPING': 1,
            'ALLOWNOTE': 0,
            'ADDROVERRIDE': 0,
            'SOLUTIONTYPE': 'Mark',
            'LANDINGPAGE': 'Login',
            'BRANDNAME': CFG_SITE_NAME,
            'PAYMENTREQUEST_0_AMT': self.premium_package.price,
            'PAYMENTREQUEST_0_PAYMENTACTION': 'Sale',
            'PAYMENTREQUEST_0_CURRENCYCODE': self.premium_package.currency,
            'PAYMENTREQUEST_0_ALLOWEDPAYMENTMETHOD': 'InstantPaymentOnly',
            'L_PAYMENTREQUEST_0_NAME0': self.premium_package.name,
            'L_PAYMENTREQUEST_0_DESC0': self.premium_package.details,
            'L_PAYMENTREQUEST_0_AMT0': self.premium_package.price,
            'L_PAYMENTREQUEST_0_QTY0': 1,
            'L_PAYMENTTYPE0': 'InstantOnly',
            'LOCALECODE': 'GB'
        }

        params = urllib.urlencode(values)
        request = urllib2.Request(self._request_url, params)
        response = cgi.parse_qs(urllib2.urlopen(request).read())

        self._set_response(response['ACK'][0] == 'Success')

        if self.is_response_successful():
            authorize_params = {
                'cmd': '_express-checkout',
                'token': response['TOKEN'][0]
            }

            self._response['data'] = ("%s?%s" % (self._express_checkout_url,
                                      urllib.urlencode(authorize_params)))
        else:
            self._extract_error_messages(response)

        return self._response

    def get_transaction_details(self, form):
        """
        Sends request to get transaction details from paypal. Returns the
        response.

        @param form: the response of the paypal api.
        @type form: C{dict}

        @see: U{https://www.x.com/developers/paypal/documentation-tools/api/
        getexpresscheckoutdetails-api-operation-nvp}
        """
        from invenio.webinterface_handler import wash_urlargd

        args = wash_urlargd(form, {'token': (str, ''), 'PayerID': (str, '')})
        # Parameters to get the transactions details
        values = {
            'USER': CFG_PAYPAL_API_USERNAME,
            'PWD': CFG_PAYPAL_API_PASSWORD,
            'SIGNATURE': CFG_PAYPAL_API_SIGNATURE,
            'VERSION': CFG_PAYPAL_API_VERSION,
            'TOKEN': args['token'],
            'PAYERID': args['PayerID'],
            'METHOD': 'GetExpressCheckoutDetails'
        }

        params = urllib.urlencode(values)

        request = urllib2.Request(self._request_url, params)
        response = cgi.parse_qs(urllib2.urlopen(request).read())

        self._set_response(response['ACK'][0] == 'Success')

        if self.is_response_successful():
            complete_button = """
            <a href="%(complete_url)s">
                %(complete_button)s
            </a>
            """ % {
                'complete_url': (CFG_SITE_SECURE_URL
                                 + "/webpayment/complete?payment_method="
                                 + self.name +
                                 "&id_package="
                                 + str(self.premium_package.id)
                                 + "&token="
                                 + str(args['token'])
                                 + "&PayerID="
                                 + str(args['PayerID'])),
                'complete_button': self.get_button_img(None)
            }
            self._response['data'] = complete_button
        else:
            self._extract_error_messages(response)

        return self._response

    def complete_transaction(self, form):
        """
        Sends request to PayPal to complete the payment and grants the user the
        given premium package. Returns the response.

        @param form: the response of the paypal api.
        @type form: C{dict}

        @see: U{https://www.x.com/developers/paypal/documentation-tools/api/
        doexpresscheckoutpayment-api-operation-nvp}
        """
        from invenio.webinterface_handler import wash_urlargd

        args = wash_urlargd(form, {'token': (str, ''), 'PayerID': (str, '')})
        # Parameters to complete PayPal transaction
        values = {
            'USER': CFG_PAYPAL_API_USERNAME,
            'PWD': CFG_PAYPAL_API_PASSWORD,
            'SIGNATURE': CFG_PAYPAL_API_SIGNATURE,
            'VERSION': CFG_PAYPAL_API_VERSION,
            'TOKEN': args['token'],
            'PAYERID': args['PayerID'],
            'PAYMENTREQUEST_0_AMT': self.premium_package.price,
            'PAYMENTREQUEST_0_CURRENCYCODE': self.premium_package.currency,
            'METHOD': 'DoExpressCheckoutPayment'
        }

        params = urllib.urlencode(values)

        request = urllib2.Request(self._request_url, params)
        response = cgi.parse_qs(urllib2.urlopen(request).read())

        self._set_response(response['ACK'][0] == 'Success')

        if self.is_response_successful():
            self.set_transaction_id(response['PAYMENTINFO_0_TRANSACTIONID'][0])
        else:
            self._extract_error_messages(response)

        return self._response

    def _extract_error_messages(self, response):
        """
        Extracts the error messages from the response returned from paypal api.

        @param response: the response returned from paypal api
        @type response: dict
        """
        for key in response.keys():
            if key.startswith(self.ERRORCODE_PREFIX):
                self.add_error_message(response[self.MESSAGE_PREFIX +
                                       key[len(self.ERRORCODE_PREFIX):]][0])
