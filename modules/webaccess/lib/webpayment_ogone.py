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
Ogone class to make payment requests from Ogone
"""
from invenio.config import CFG_OGONE_API_PSPID
from invenio.config import CFG_OGONE_API_PSWD
from invenio.config import CFG_OGONE_API_USERID
from invenio.config import CFG_PREMIUM_SERVICE
from invenio.config import CFG_TEST_PREMIUM_SERVICE
from invenio.webpayment_base import PaymentGateway
from invenio.webpayment_forms import OGoneCreditCardForm
from xml.dom.minidom import parseString
import urllib
import urllib2


class Ogone(PaymentGateway):
    """
    Contains methods to use Ogone API
    """
    name = "Ogone"

    TEST_SERVER = "https://secure.ogone.com/ncol/test/orderdirect.asp"
    SERVER = "https://secure.ogone.com/ncol/prod/orderdirect.asp"

    _additional_form = OGoneCreditCardForm

    def __init__(self, form=None, credit_card_form=None):
        """
        Initialization
        """
        PaymentGateway.__init__(self, form, credit_card_form)

        if not int(CFG_PREMIUM_SERVICE):
            self._request_url = None
        elif int(CFG_TEST_PREMIUM_SERVICE):
            self._request_url = self.TEST_SERVER
        else:
            self._request_url = self.SERVER

    def process(self):
        """
        Make the request to "pay with credit card".
        """
        values = {
            'PSPID': CFG_OGONE_API_PSPID,
            'USERID': CFG_OGONE_API_USERID,
            'PSWD': CFG_OGONE_API_PSWD,
            'ORDERID': "1",
            'AMOUNT': int(self.premium_package.price * 100),
            'CURRENCY': self.premium_package.currency,
            'CARDNO': self.credit_card_form.card_number.data,
            'ED': "%s%s" % (self.credit_card_form.expiration_month.data
                            .zfill(2),
                            self.credit_card_form.expiration_year.data[-2:]),
            'CVC': self.credit_card_form.cvv.data,
            'OPERATION': 'SAL',
        }
        while True:
            values['ORDERID'] = self._generate_order_id()
            params = urllib.urlencode(values)
            request = urllib2.Request(self._request_url, params)
            response = parseString(urllib2.urlopen(request).read())
            ncresponse = response.getElementsByTagName("ncresponse")[0]
            ncerror = str(ncresponse.getAttribute("NCERROR"))
            if ncerror != "50001113":
                break

        status = ncresponse.getAttribute("STATUS")
        self._set_response(ncerror == "0" and status == "9")
        if self.is_response_successful():
            self.set_transaction_id(str(ncresponse.getAttribute("PAYID")))
        else:
            self.add_error_message(str(ncresponse.getAttribute("NCERRORPLUS")))

        return self.get_response()
