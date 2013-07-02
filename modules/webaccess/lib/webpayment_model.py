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
Models of the tables that are used for webpayment module.
"""
from invenio.sqlalchemyutils import db
from invenio.webaccess_model import AccROLE
from invenio.websession_model import User
from invenio.websearch_model import Collection


class Premium(db.Model):
    """
    Represents a premium model.

    This model keeps the following information about the premium packages.
        - ID
        - Name
        - Details
        - Duration and unit time
        - Price and currency
        - Order

    @see: L{PremiumPackageForm}
    """

    __table_name__ = 'premium'

    #: @type: L{Column}
    id = db.Column(db.Integer(11, unsigned=False),
                   nullable=False,
                   primary_key=True)

    #: @type: L{Column}
    name = db.Column(db.String(256),
                     nullable=False)

    #: @type: L{Column}
    details = db.Column(db.Text,
                        nullable=False)

    #: @type: L{Column}
    duration = db.Column(db.Integer(11, unsigned=True),
                         nullable=False)

    #: @type: L{Column}
    unit_time = db.Column(db.Enum('HOUR', 'DAY', 'WEEK', 'MONTH', 'YEAR',
                                  'UNLIMITED'),
                          nullable=False)

    #: @type: L{Column}
    price = db.Column(db.Float(2),
                      nullable=False)

    #: The curreny of the price of the premium package.
    #:
    #: B{Supported currencies:}
    #:     - CAD: Canadian Dollar
    #:     - CZK: Czech Koruna
    #:     - DKK: Danish Krone
    #:     - EUR: Euro
    #:     - HKD: Hong Kong Dollar
    #:     - HUF: Hungarian Forint
    #:     - JPY: Japanese Yen
    #:     - NOK: Norwegian Krone
    #:     - NZD: New Zealand Dollar
    #:     - PLN: Polish Zloty
    #:     - GBP: British Pound
    #:     - SGD: Singapore Dollar
    #:     - SEK: Swedish Krona
    #:     - CHF: Swiss Franc
    #:     - USD: US Dollar
    #:
    #: @type: L{Column}
    currency = db.Column(db.Enum('AUD', 'CAD', 'CZK', 'DKK', 'EUR', 'HKD',
                                 'HUF', 'JPY', 'NOK', 'NZD', 'PLN', 'GBP',
                                 'SGD', 'SEK', 'CHF', 'USD'),
                         nullable=False)

    #: The display order of the premium package in the web interface.
    #:
    #: @type: L{Column}
    ord = db.Column(db.Integer(11),
                    nullable=False)


class HstPAYMENT(db.Model):
    """
    Represents a HstPAYMENT model

    Keeps the information about:
        - ID of the user
        - ID of the premium package
        - Price and currency
        - Transaction time
        - Payment method
        - Transaction ID (token)
    """
    __table_name__ = 'hstPAYMENT'

    #: @type: L{Column}
    id = db.Column(db.Integer(11, unsigned=False),
                   nullable=False,
                   primary_key=True)

    #: @type: L{Column}
    id_user = db.Column(db.Integer(11, unsigned=True),
                        db.ForeignKey(User.id),
                        nullable=False)

    #: @type: L{Column}
    id_package = db.Column(db.Integer(11, unsigned=True),
                           db.ForeignKey(Premium.id),
                           nullable=False)

    #: @type: L{Column}
    price = db.Column(db.Float(2),
                      nullable=False)

    #: @type: L{Column}
    currency = db.Column(db.Enum('AUD', 'CAD', 'CZK', 'DKK', 'EUR', 'HKD',
                                 'HUF', 'JPY', 'NOK', 'NZD', 'PLN', 'GBP',
                                 'SGD', 'SEK', 'CHF', 'USD'),
                         nullable=False)

    #: @type: L{Column}
    transaction_time = db.Column(db.DateTime(),
                                 nullable=False)

    #: @type: L{Column}
    payment_method = db.Column(db.String(256),
                               nullable=False)

    #: The token returned from payment gateway.
    #:
    #: @type: L{Column}
    token = db.Column(db.String(256),
                      nullable=False)


class PremiumCollection(db.Model):
    """
    Represents a PremiumCollection model

    Keeps the information about which premium package allows the user to
    display which collections.
    """
    __table_name__ = 'premium_collection'

    #: @type: L{Column}
    id_package = db.Column(db.Integer(11, unsigned=False),
                           db.ForeignKey(Premium.id),
                           nullable=False,
                           primary_key=True)

    #: @type: L{Column}
    id_collection = db.Column(db.Integer(11, unsigned=False),
                              db.ForeignKey(Collection.id),
                              nullable=False,
                              primary_key=True)


class CollectionAccROLE(db.Model):
    """
    Represents a CollectionAccROLE model

    Keeps the information about which collection can be displayed by which
    user role.
    """
    __table_name__ = 'collection_accROLE'

    #: @type: L{Column}
    id_collection = db.Column(db.Integer(11, unsigned=False),
                              db.ForeignKey(Collection.id),
                              nullable=False,
                              primary_key=True)

    #: @type: L{Column}
    id_accROLE = db.Column(db.Integer(11, unsigned=False),
                           db.ForeignKey(AccROLE.id),
                           nullable=False,
                           primary_key=True)

    #: @type: L{RelationshipProperty}
    role = db.relationship(AccROLE, backref='collections')


__all__ = ['Premium',
           'HstPAYMENT',
           'PremiumCollection',
           'CollectionAccROLE']
