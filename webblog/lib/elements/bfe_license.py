#!/usr/bin/env python
# -*- coding: utf-8 -*-
## This file is part of CDS Invenio.
## Copyright (C) 2013 CERN.
##
## CDS Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## CDS Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with CDS Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
BibFormat Element - displays license name and url if available
"""

from invenio.config import CFG_SITE_SECURE_URL
from invenio.urlutils import create_html_link

cfg_messages = {}
cfg_messages["in_issue"] = {"en": "License",
                            "es": "Licencia",
                            "fr": "Licence"}

def format_element(bfo):
    """
    Displays license name and url if available
    """

    current_language = bfo.lang
    licenses = bfo.fields('540')

    licenses = [{'a': 'Creative Commons', 'u': 'http://creativecommons.org/licenses/'}]

    if licenses:
        try:
            out = '<h4><i class="icon-legal"></i>&nbsp;%s</h4>' % cfg_messages["in_issue"][current_language]
        except: # in english by default
            out = '<h4><i class="icon-legal"></i>&nbsp;%s</h4>' % cfg_messages["in_issue"]['en']

        for license in licenses:
            license_name = license.get('a')
            license_url = license.get('u', license_name)

            url = create_html_link(license_url, {}, license_name)
            out += '<span>%s</span>' % url

    return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0