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
from flask.helpers import url_for
from invenio.sqlalchemyutils import db
from invenio.webhistory_collector import HistoryCollector
from invenio.webhistory_config import CFG_SHARE_MSGS
from invenio.webhistory_config import CFG_WEBHISTORY_MSGS
from invenio.webinterface_handler_flask_utils import _
from invenio.webpayment_model import HstPAYMENT
from sqlalchemy.sql import expression
"""
Collector for payment history of the user

@undocumented: COLLECTOR
"""


class PaymentHistory(HistoryCollector):
    """
    Collects payment history
    """
    icon = 'money'
    label = 'Payments'

    @staticmethod
    def get_date(x):
        return x.transaction_time

    @staticmethod
    def get_id(x):
        return x.id

    @staticmethod
    def serialize(x):
        return [x.price, x.currency]

    def get_user_history(self, limit, offset, filter_from, filter_to):
        """
        Returns user's payment history.
        """
        payments = (db.session
                    .query(HstPAYMENT.id,
                           HstPAYMENT.price,
                           HstPAYMENT.currency,
                           HstPAYMENT.transaction_time,
                           HstPAYMENT.token)
                    .filter(HstPAYMENT.id_user == self._uid))

        if filter_from:
            payments = payments.filter(HstPAYMENT.transaction_time
                                       >= filter_from)

        if filter_to:
            payments = payments.filter(HstPAYMENT.transaction_time
                                       <= filter_to)

        payments = (payments
                    .order_by(expression.desc(HstPAYMENT.transaction_time))
                    .limit(limit)
                    .offset(offset)
                    .all())

        return payments

    @staticmethod
    def get_message(entry):
        """
        Returns a message to display payment history on web-interface.

        @see: L{HistoryElement.get_message}
        """
        paymenturl = url_for("webpayment.index")
        return _(CFG_WEBHISTORY_MSGS[24]) % {'paymenturl': paymenturl,
                                             'price': entry.price,
                                             'currency': entry.currency,
                                             'token': entry.token}

    @staticmethod
    def get_share_message(serialized_history_element):
        """
        Returns a message used while sharing payment history on
        web-interface.

        @see: L{HistoryElement.get_share_message}
        """
        return _(CFG_SHARE_MSGS[24]) % {'price':
                                        float(serialized_history_element[0]),
                                        'currency':
                                        serialized_history_element[1]}

COLLECTOR = PaymentHistory
