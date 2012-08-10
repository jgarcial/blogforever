# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2006, 2007, 2008, 2009, 2010, 2011 CERN.
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

# pylint: disable=C0301

"""WebSession configuration parameters."""

__revision__ = "$Id$"

CFG_WEBSESSION_GROUP_JOIN_POLICY = {'VISIBLEOPEN': 'VO',
                                    'VISIBLEMAIL': 'VM',
                                    'INVISIBLEOPEN': 'IO',
                                    'INVISIBLEMAIL': 'IM',
                                    'VISIBLEEXTERNAL' : 'VE'
                                    }

CFG_WEBSESSION_USERGROUP_STATUS = {'ADMIN':  'A',
                                   'MEMBER':'M',
                                   'PENDING':'P'
                                   }

CFG_WEBSESSION_INFO_MESSAGES = {"GROUP_CREATED": 'You have successfully created a new group.',
                                "JOIN_GROUP": 'You have successfully joined a new group.',
                                "GROUP_UPDATED": 'You have successfully updated a group.',
                                "GROUP_DELETED": 'You have successfully deleted a group.',
                                "MEMBER_DELETED": 'You have successfully deleted a member.',
                                "MEMBER_ADDED": 'You have successfully added a new member.',
                                "MEMBER_REJECTED": 'You have successfully removed a waiting member from the list.',
                                "JOIN_REQUEST": 'The group administrator has been notified of your request.',
                                "LEAVE_GROUP": 'You have successfully left a group.'

}

# Choose the providers which will be dislayed bigger (48x48) on login page.
# The order of the list decides the order of the login buttons.
CFG_EXTERNAL_LOGIN_LARGE = [
    "facebook",
    "google",
    "yahoo",
    "openid"
]

# Choose the order of the login buttons. The unordered providers will be
# displayed alphabetically after the ordered ones.
CFG_EXTERNAL_LOGIN_BUTTON_ORDER = []

# Select the labels of the username inputs for openid providers which needs
# username for authorization.
CFG_EXTERNAL_LOGIN_FORM_LABELS = {
    "openid": "Your OpenID Identifier",
    "aol": "Your AOL screenname",
    "myopenid": "Your myOpenID username",
    "myvidoop": "Your myvidoop username",
    "verisign": "Your VeriSign username",
    "wordpress": "Your WordPress username",
    "myspace": "Your myspace username",
    "livejournal": "Your livejournal username",
    "blogger": "The address of your blog"
}

CFG_WEBSESSION_COOKIE_NAME = "INVENIOSESSION"
CFG_WEBSESSION_ONE_DAY = 86400 #: how many seconds are there in one day
CFG_WEBSESSION_CLEANUP_CHANCE = 10000 #: cleanups have 1 in CLEANUP_CHANCE chance

## FIXME: Session locking is currently disabled because, since it's
## implementing the mod_python technique of using Apache mutexes, these
## are by default a very limited resources (according to
## <http://www.modpython.org/live/current/doc-html/inst-apacheconfig.html#l2h-21>)
## only 8 mutexes are available by default)
## Since the session would be locked at constructor time and unlocked at
## destructor time, and since we cache the session for the whole request
## handling time, enabling locking would mean that at most only 8 requests
## could been handled at the same time. This is quite limited and, anyway
## there's already local locking available thanks to our MySQL backend.
CFG_WEBSESSION_ENABLE_LOCKING = False

# Exceptions: errors
class InvenioWebSessionError(Exception):
    """A generic error for WebSession."""
    def __init__(self, message):
        """Initialisation."""
        self.message = message
    def __str__(self):
        """String representation."""
        return repr(self.message)

# Exceptions: warnings
class InvenioWebSessionWarning(Exception):
    """A generic warning for WebSession."""
    def __init__(self, message):
        """Initialisation."""
        self.message = message
    def __str__(self):
        """String representation."""
        return repr(self.message)

COUNTRY_ISO_CODES = [
    ('AALAND ISLANDS', 'AX'),
    ('AFGHANISTAN', 'AF'),
    ('ALBANIA', 'AL'),
    ('ALGERIA', 'DZ'),
    ('AMERICAN SAMOA', 'AS'),
    ('ANDORRA', 'AD'),
    ('ANGOLA', 'AO'),
    ('ANGUILLA', 'AI'),
    ('ANTARCTICA', 'AQ'),
    ('ANTIGUA AND BARBUDA', 'AG'),
    ('ARGENTINA', 'AR'),
    ('ARMENIA', 'AM'),
    ('ARUBA', 'AW'),
    ('AUSTRALIA', 'AU'),
    ('AUSTRIA', 'AT'),
    ('AZERBAIJAN', 'AZ'),
    ('BAHAMAS', 'BS'),
    ('BAHRAIN', 'BH'),
    ('BANGLADESH', 'BD'),
    ('BARBADOS', 'BB'),
    ('BELARUS', 'BY'),
    ('BELGIUM', 'BE'),
    ('BELIZE', 'BZ'),
    ('BENIN', 'BJ'),
    ('BERMUDA', 'BM'),
    ('BHUTAN', 'BT'),
    ('BOLIVIA', 'BO'),
    ('BOSNIA AND HERZEGOWINA', 'BA'),
    ('BOTSWANA', 'BW'),
    ('BOUVET ISLAND', 'BV'),
    ('BRAZIL', 'BR'),
    ('BRITISH INDIAN OCEAN TERRITORY', 'IO'),
    ('BRUNEI DARUSSALAM', 'BN'),
    ('BULGARIA', 'BG'),
    ('BURKINA FASO', 'BF'),
    ('BURUNDI', 'BI'),
    ('CAMBODIA', 'KH'),
    ('CAMEROON', 'CM'),
    ('CANADA', 'CA'),
    ('CAPE VERDE', 'CV'),
    ('CAYMAN ISLANDS', 'KY'),
    ('CENTRAL AFRICAN REPUBLIC', 'CF'),
    ('CHAD', 'TD'),
    ('CHILE', 'CL'),
    ('CHINA', 'CN'),
    ('CHRISTMAS ISLAND', 'CX'),
    ('COCOS (KEELING) ISLANDS', 'CC'),
    ('COLOMBIA', 'CO'),
    ('COMOROS', 'KM'),
    ('CONGO, Democratic Republic of (was Zaire)', 'CD'),
    ('CONGO, Republic of', 'CG'),
    ('COOK ISLANDS', 'CK'),
    ('COSTA RICA', 'CR'),
    ("COTE D'IVOIRE", 'CI'),
    ('CROATIA (local name: Hrvatska)', 'HR'),
    ('CUBA', 'CU'),
    ('CYPRUS', 'CY'),
    ('CZECH REPUBLIC', 'CZ'),
    ('DENMARK', 'DK'),
    ('DJIBOUTI', 'DJ'),
    ('DOMINICA', 'DM'),
    ('DOMINICAN REPUBLIC', 'DO'),
    ('ECUADOR', 'EC'),
    ('EGYPT', 'EG'),
    ('EL SALVADOR', 'SV'),
    ('EQUATORIAL GUINEA', 'GQ'),
    ('ERITREA', 'ER'),
    ('ESTONIA', 'EE'),
    ('ETHIOPIA', 'ET'),
    ('FALKLAND ISLANDS (MALVINAS)', 'FK'),
    ('FAROE ISLANDS', 'FO'),
    ('FIJI', 'FJ'),
    ('FINLAND', 'FI'),
    ('FRANCE', 'FR'),
    ('FRENCH GUIANA', 'GF'),
    ('FRENCH POLYNESIA', 'PF'),
    ('FRENCH SOUTHERN TERRITORIES', 'TF'),
    ('GABON', 'GA'),
    ('GAMBIA', 'GM'),
    ('GEORGIA', 'GE'),
    ('GERMANY', 'DE'),
    ('GHANA', 'GH'),
    ('GIBRALTAR', 'GI'),
    ('GREECE', 'GR'),
    ('GREENLAND', 'GL'),
    ('GRENADA', 'GD'),
    ('GUADELOUPE', 'GP'),
    ('GUAM', 'GU'),
    ('GUATEMALA', 'GT'),
    ('GUINEA', 'GN'),
    ('GUINEA-BISSAU', 'GW'),
    ('GUYANA', 'GY'),
    ('HAITI', 'HT'),
    ('HEARD AND MC DONALD ISLANDS', 'HM'),
    ('HONDURAS', 'HN'),
    ('HONG KONG', 'HK'),
    ('HUNGARY', 'HU'),
    ('ICELAND', 'IS'),
    ('INDIA', 'IN'),
    ('INDONESIA', 'ID'),
    ('IRAN (ISLAMIC REPUBLIC OF)', 'IR'),
    ('IRAQ', 'IQ'),
    ('IRELAND', 'IE'),
    ('ISRAEL', 'IL'),
    ('ITALY', 'IT'),
    ('JAMAICA', 'JM'),
    ('JAPAN', 'JP'),
    ('JORDAN', 'JO'),
    ('KAZAKHSTAN', 'KZ'),
    ('KENYA', 'KE'),
    ('KIRIBATI', 'KI'),
    ("KOREA, DEMOCRATIC PEOPLE'S REPUBLIC OF", 'KP'),
    ('KOREA, REPUBLIC OF', 'KR'),
    ('KUWAIT', 'KW'),
    ('KYRGYZSTAN', 'KG'),
    ("LAO PEOPLE'S DEMOCRATIC REPUBLIC", 'LA'),
    ('LATVIA', 'LV'),
    ('LEBANON', 'LB'),
    ('LESOTHO', 'LS'),
    ('LIBERIA', 'LR'),
    ('LIBYAN ARAB JAMAHIRIYA', 'LY'),
    ('LIECHTENSTEIN', 'LI'),
    ('LITHUANIA', 'LT'),
    ('LUXEMBOURG', 'LU'),
    ('MACAU', 'MO'),
    ('MACEDONIA, THE FORMER YUGOSLAV REPUBLIC OF', 'MK'),
    ('MADAGASCAR', 'MG'),
    ('MALAWI', 'MW'),
    ('MALAYSIA', 'MY'),
    ('MALDIVES', 'MV'),
    ('MALI', 'ML'),
    ('MALTA', 'MT'),
    ('MARSHALL ISLANDS', 'MH'),
    ('MARTINIQUE', 'MQ'),
    ('MAURITANIA', 'MR'),
    ('MAURITIUS', 'MU'),
    ('MAYOTTE', 'YT'),
    ('MEXICO', 'MX'),
    ('MICRONESIA, FEDERATED STATES OF', 'FM'),
    ('MOLDOVA, REPUBLIC OF', 'MD'),
    ('MONACO', 'MC'),
    ('MONGOLIA', 'MN'),
    ('MONTSERRAT', 'MS'),
    ('MOROCCO', 'MA'),
    ('MOZAMBIQUE', 'MZ'),
    ('MYANMAR', 'MM'),
    ('NAMIBIA', 'NA'),
    ('NAURU', 'NR'),
    ('NEPAL', 'NP'),
    ('NETHERLANDS', 'NL'),
    ('NETHERLANDS ANTILLES', 'AN'),
    ('NEW CALEDONIA', 'NC'),
    ('NEW ZEALAND', 'NZ'),
    ('NICARAGUA', 'NI'),
    ('NIGER', 'NE'),
    ('NIGERIA', 'NG'),
    ('NIUE', 'NU'),
    ('NORFOLK ISLAND', 'NF'),
    ('NORTHERN MARIANA ISLANDS', 'MP'),
    ('NORWAY', 'NO'),
    ('OMAN', 'OM'),
    ('PAKISTAN', 'PK'),
    ('PALAU', 'PW'),
    ('PALESTINIAN TERRITORY, Occupied', 'PS'),
    ('PANAMA', 'PA'),
    ('PAPUA NEW GUINEA', 'PG'),
    ('PARAGUAY', 'PY'),
    ('PERU', 'PE'),
    ('PHILIPPINES', 'PH'),
    ('PITCAIRN', 'PN'),
    ('POLAND', 'PL'),
    ('PORTUGAL', 'PT'),
    ('PUERTO RICO', 'PR'),
    ('QATAR', 'QA'),
    ('REUNION', 'RE'),
    ('ROMANIA', 'RO'),
    ('RUSSIAN FEDERATION', 'RU'),
    ('RWANDA', 'RW'),
    ('SAINT HELENA', 'SH'),
    ('SAINT KITTS AND NEVIS', 'KN'),
    ('SAINT LUCIA', 'LC'),
    ('SAINT PIERRE AND MIQUELON', 'PM'),
    ('SAINT VINCENT AND THE GRENADINES', 'VC'),
    ('SAMOA', 'WS'),
    ('SAN MARINO', 'SM'),
    ('SAO TOME AND PRINCIPE', 'ST'),
    ('SAUDI ARABIA', 'SA'),
    ('SENEGAL', 'SN'),
    ('SERBIA AND MONTENEGRO', 'CS'),
    ('SEYCHELLES', 'SC'),
    ('SIERRA LEONE', 'SL'),
    ('SINGAPORE', 'SG'),
    ('SLOVAKIA', 'SK'),
    ('SLOVENIA', 'SI'),
    ('SOLOMON ISLANDS', 'SB'),
    ('SOMALIA', 'SO'),
    ('SOUTH AFRICA', 'ZA'),
    ('SOUTH GEORGIA AND THE SOUTH SANDWICH ISLANDS', 'GS'),
    ('SPAIN', 'ES'),
    ('SRI LANKA', 'LK'),
    ('SUDAN', 'SD'),
    ('SURINAME', 'SR'),
    ('SVALBARD AND JAN MAYEN ISLANDS', 'SJ'),
    ('SWAZILAND', 'SZ'),
    ('SWEDEN', 'SE'),
    ('SWITZERLAND', 'CH'),
    ('SYRIAN ARAB REPUBLIC', 'SY'),
    ('TAIWAN', 'TW'),
    ('TAJIKISTAN', 'TJ'),
    ('TANZANIA, UNITED REPUBLIC OF', 'TZ'),
    ('THAILAND', 'TH'),
    ('TIMOR-LESTE', 'TL'),
    ('TOGO', 'TG'),
    ('TOKELAU', 'TK'),
    ('TONGA', 'TO'),
    ('TRINIDAD AND TOBAGO', 'TT'),
    ('TUNISIA', 'TN'),
    ('TURKEY', 'TR'),
    ('TURKMENISTAN', 'TM'),
    ('TURKS AND CAICOS ISLANDS', 'TC'),
    ('TUVALU', 'TV'),
    ('UGANDA', 'UG'),
    ('UKRAINE', 'UA'),
    ('UNITED ARAB EMIRATES', 'AE'),
    ('UNITED KINGDOM', 'GB'),
    ('UNITED STATES', 'US'),
    ('UNITED STATES MINOR OUTLYING ISLANDS', 'UM'),
    ('URUGUAY', 'UY'),
    ('UZBEKISTAN', 'UZ'),
    ('VANUATU', 'VU'),
    ('VATICAN CITY STATE (HOLY SEE)', 'VA'),
    ('VENEZUELA', 'VE'),
    ('VIET NAM', 'VN'),
    ('VIRGIN ISLANDS (BRITISH)', 'VG'),
    ('VIRGIN ISLANDS (U.S.)', 'VI'),
    ('WALLIS AND FUTUNA ISLANDS', 'WF'),
    ('WESTERN SAHARA', 'EH'),
    ('YEMEN', 'YE'),
    ('ZAMBIA', 'ZM'),
    ('ZIMBABWE', 'ZW')
]
