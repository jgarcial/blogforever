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
The forms to manage premium packages and buy premium
packages with credit card.
"""
from datetime import date
from invenio.webinterface_handler_flask_utils import _
from invenio.webmessage_forms import validate_user_nicks
from invenio.webpayment_query import get_all_collections
from invenio.webpayment_query import get_all_premium_packages
from invenio.websession_config import COUNTRY_ISO_CODES
from invenio.wtforms_utils import InvenioBaseForm
from wtforms import HiddenField
from wtforms import SelectField
from wtforms import TextAreaField
from wtforms import TextField
from wtforms.validators import ValidationError
from wtforms.validators import Required


class CollectionListField(SelectField):
    """
    Select field customized for displaying collections.
    """
    def __init__(self, label=None, validators=None, **kwargs):
        """
        Sets the choices as the collections.
        """
        super(CollectionListField, self).__init__(label=label,
                                                  validators=validators,
                                                  **kwargs)
        self.choices = get_all_collections()

    def pre_validate(self, form):
        """
        Do not any pre-validation.
        """
        pass


class PremiumPackageListField(SelectField):
    """
    Select field customized for displaying premium packages.
    """
    def __init__(self, label=None, validators=None, **kwargs):
        """
        Sets the choices as the premium packages.
        """
        super(PremiumPackageListField, self).__init__(label=label,
                                                      validators=validators,
                                                      **kwargs)
        premium_packages = get_all_premium_packages()
        self.choices = [(package.id, package.name) for package
                        in premium_packages]

    def pre_validate(self, dummy):
        try:
            self.data = int(self.data)
        except:
            raise ValueError(self.gettext('Please select a valid premium '
                                          'package.'))

        for v, _ in self.choices:
            if self.data == v:
                break
        else:
            raise ValueError(self.gettext('Please select a valid '
                                          'premium package.'))


def extract_list_values(data):
    """
    Extract the values from a list structured string.

    >>> extract_list_values("[1,2,3]")
    [1, 2, 3]
    >>> extract_list_values("")
    []

    @param data: a string looks like a list
    @type data: str

    @rtype: list
    """
    if not data or data == "[]":
        return []
    data = data[1:-1].split(",")
    for i in range(len(data)):
        data[i] = int(data[i])
    return data


def float_filter(data):
    """
    Converts the string to a float.

    >>> float_filter("3.14")
    3.14
    >>> float_filter("3,14")
    3.14

    @raise ValueError: if the data is not in a form of float

    @param data: a float as a string
    @type data: str

    @rtype: float
    """
    if not data:
        return data

    try:
        return float(data)
    except:
        pass

    data = data.replace(",", ".")
    try:
        return float(data)
    except:
        raise ValueError("Please give a valid number.")


def integer_filter(data):
    """
    Converts the string to a float.

    >>> integer_filter("3")
    3
    >>> integer_filter("3.14")
    3
    >>> integer_filter("3,14")
    3

    @raise ValueError: if the data is not in a form of integer

    @param data: an integer as a string
    @type data: str

    @rtype: int
    """
    if not data:
        return data

    try:
        return int(data)
    except:
        pass

    data = data.replace(",", ".")
    try:
        return int(data)
    except:
        raise ValueError("Please give a valid number.")


def validate_collections(form, field):
    """
    Validates the collections field in the L{PremiumPackageForm}.

    @raise ValidationError: If the collection id is not valid.
    """
    if not field.data:
        raise ValueError(field.gettext("Please add at least one collection."))

    choices = [v for v, _ in form.collection_list.choices]
    for collection in field.data:
        try:
            collection = int(collection)
        except:
            raise ValidationError(field.gettext("%s is not a valid collection."
                                                % collection))
        if not collection in choices:
            raise ValidationError(field.gettext("%s is not a valid collection."
                                                % collection))


def validate_username(form, field):
    """
    Validates the username.

    @raise ValidationError: If the username is not exist.
    """
    try:
        validate_user_nicks(form, field)
    except:
        raise ValidationError(field.gettext("Could not find the user: %s."
                                            % field.data))


def validate_length(length):
    """
    Returns a function to validate max length with more appropriate message
    than the default.

    @param length: the max length
    @type length: int

    @rtype: function
    """
    def validate(dummy, field):
        if len(field.data) > length:
            raise ValidationError(field.gettext(('%s must be less than %d '
                                                'characters')
                                                % (field.label.text, length)))

    return validate


class PremiumPackageForm(InvenioBaseForm):
    """
    Form to manage premium packages.
    """

    #: The name of the premium package.
    #:
    #: B{Validators:}
    #:     - Max length is 256 characters.
    #:
    #: @type: L{TextField}
    name = TextField(label=_("Name"),
                     validators=(validate_length(256),
                                 Required(message=_(u'Please give a '
                                                    'valid name.'))))

    #: Details of the premium package.
    #:
    #: B{Validators:}
    #:     - Max length is 65536 characters.
    #:
    #: @type: L{TextAreaField}
    details = TextAreaField(label=_("Details"),
                            validators=(validate_length(65536),
                                        Required(message=_(u'Please give a '
                                                           'valid description.'
                                                           ))))

    #: The duration of the premium package.
    #:
    #: B{Filters:}
    #:     - L{integer_filter}
    #:
    #: @type: L{TextField}
    duration = TextField(label=_("Duration"),
                         filters=(integer_filter,))

    def validate_duration(self, field):
        """
        Validates the duration field.

        @raise ValidationError: if there the data field is empty when unit
        time is not unlimited.
        """
        if not field.data and self.unit_time.data != 'Unlimited':
            raise ValidationError(_("Please give a valid number"))

    #: The unit time of the duration of the premium package.
    #:
    #: B{Choices:}
    #:     - Hour
    #:     - Day
    #:     - Week
    #:     - Month
    #:     - Year
    #:     - Unlimited
    #:
    #: @type: L{SelectField}
    unit_time = SelectField(choices=(("Hour", _("Hour")),
                                     ("Day", _("Day")),
                                     ("Week", _("Week")),
                                     ("Month", _("Month")),
                                     ("Year", _("Year")),
                                     ("Unlimited", _("Unlimited"))))

    #: The price of the premium package.
    #:
    #: B{Filters:}
    #:     - L{float_filter}
    #:
    #: @type: L{TextField}
    price = TextField(label=_("Price"),
                      filters=(float_filter,),
                      validators=(Required(message=_(u'Please give a valid '
                                                     'number.')),))

    #: The currency of the price of the premium package.
    #:
    #: B{Choices:}
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
    #: @type: L{SelectField}
    currency = SelectField(choices=(("CAD", _("CAD")),
                                    ("CZK", _("CZK")),
                                    ("DKK", _("DKK")),
                                    ("EUR", _("EUR")),
                                    ("HKD", _("HKD")),
                                    ("HUF", _("HUF")),
                                    ("JPY", _("JPY")),
                                    ("NOK", _("NOK")),
                                    ("NZD", _("NZD")),
                                    ("PLN", _("PLN")),
                                    ("GBP", _("GBP")),
                                    ("SGD", _("SGD")),
                                    ("SEK", _("SEK")),
                                    ("CHF", _("CHF")),
                                    ("USD", _("USD"))),
                           default="EUR")

    #: List of the collections that are able to be restricted.
    #:
    #: @type: L{CollectionListField}
    collection_list = CollectionListField(label=_("Collections"))

    #: List of the IDs of the collections that are selected to be restricted.
    #:
    #: B{Filters:}
    #:     - L{extract_list_values}
    #:
    #: B{Validators:}
    #:     - L{validate_collections}
    #:
    #: @type: L{HiddenField}
    collections = HiddenField(filters=(extract_list_values,),
                              validators=(validate_collections,))

    #: The ID of the existing premium package wanted to be edited.
    #: If the form is used to create new one, the id is not required.
    #:
    #: @type: L{HiddenField}
    package_id = HiddenField()


class GiftPremiumPackageForm(InvenioBaseForm):
    """
    Form to give a premium package to a user.
    """

    #: The username of the lucky user.
    #:
    #: B{Validators:}
    #:     - L{validate_username}
    #:
    #: @type: L{TextField}
    username = TextField(label=_("User Name"), validators=(validate_username,))

    #: The list of the premium packages.
    #:
    #: B{Choices:}
    #:     - All of the premium packages
    #:
    #: @type: L{PremiumPackageListField}
    premium_package = PremiumPackageListField(label=_("Premium Package"),
                                              choices=tuple())


class PaypalCreditCardForm(InvenioBaseForm):
    """
    Additional form to use credit card through Paypal.

    B{Required information to use paypal}:
        - I{Name on card}
        - I{Card number}
        - I{Expiration date of the card}
        - I{Security Code (CVV)}
        - First Name
        - Last Name
        - Street
        - City
        - State / Province
        - ZIP / Postal Code
        - Country Code
    """

    #: @type: L{TextField}
    first_name = TextField(label=_("First Name"),
                           validators=(Required(message=_(u'Please enter your '
                                                          'first name.')),))

    #: @type: L{TextField}
    last_name = TextField(label=_("Last Name"),
                          validators=(Required(message=_(u'Please enter your '
                                                         'last name.')),))

    #: @type: L{TextField}
    street = TextField(label=_("Street"),
                       validators=(Required(message=_(u'Please enter your '
                                                      'street.')),))

    #: @type: L{TextField}
    city = TextField(label=_('City'),
                     validators=(Required(message=_(u'Please enter your '
                                                    'city.')),))

    #: @type: L{TextField}
    state = TextField(label=_("State / Province"),
                      validators=(Required(message=_(u'Please enter your '
                                                     'state or province.')),))

    #: @type: L{TextField}
    postal_code = TextField(label=_("ZIP / Postal Code"),
                            validators=(Required(message=_(u'Please enter '
                                                           'your ZIP/Postal '
                                                           'Code.')),))

    #: The list of the countries.
    #:
    #: B{Choices:}
    #:     - All countries from L{COUNTRY_ISO_CODES}
    #:
    #: @type: L{SelectField}
    country = SelectField(label=_("Country"),
                          choices=[(code, name) for (name, code)
                                   in COUNTRY_ISO_CODES])


class OGoneCreditCardForm(InvenioBaseForm):
    """
    Additional form to use credit card through Ogone.

    B{Required information to use Ogone}:
        - I{Name on card}
        - I{Card number}
        - I{Expiration date of the card}
        - I{Security Code (CVV)}
        - First Name
        - Last Name

    """

    #: @type: L{TextField}
    first_name = TextField(label=_("First Name"),
                           validators=(Required(message=_(u'Please enter your '
                                                          'first name.')),))

    #: @type: L{TextField}
    last_name = TextField(label=_("Last Name"),
                          validators=(Required(message=_(u'Please enter your '
                                                         'last name.')),))


class CreditCardForm(InvenioBaseForm):
    """
    Credit card form to purchase a premium package.

    """

    #: @type: L{TextField}
    name_on_card = TextField(label=_("Name on Card"),
                             validators=(Required(message=_(u'Please enter '
                                                            'name on the '
                                                            'card.')),))

    #: @type: L{TextField}
    card_number = TextField(label=_("Card Number"),
                            validators=(Required(message=_(u'Please enter '
                                                           'your credit card '
                                                           'number.')),))

    #: The month of the expiration date of the credit card.
    #:
    #: @type: L{SelectField}
    expiration_month = SelectField(label=_("Expiration"),
                                   choices=[(month, month) for month
                                            in range(1, 13)])

    #: The year of the expiration date of the credit card.
    #:
    #: @type: L{SelectField}
    expiration_year = SelectField(label=_("Expiration"),
                                  choices=[(date.today().year + year,
                                            date.today().year + year) for year
                                           in range(20)])

    #: @type: L{TextField}
    cvv = TextField(label="Security Code",
                    validators=(Required(message=_(u'Please enter your '
                                                   'security code.')),))

    #: The ID of the package that is going to be purchased.
    #:
    #: @type: L{HiddenField}
    id_package = HiddenField()

    #: Additional fields to use specific payment gateways.
    #:
    #: @see: L{PaypalCreditCardForm}
    #: @see: L{OGoneCreditCardForm}
    #:
    #: @type: L{InvenioBaseForm}
    additional = None
