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
BibFormat Element - creates the posted date of a blog post
"""

from invenio.bibformat_engine import BibFormatObject
from invenio.config import CFG_SITE_URL
from invenio.messages import gettext_set_language
import datetime

def format_element(bfo):
    """
    Formats the date in which the post was posted
    """

    this_recid = bfo.control_field('001')

    _ = gettext_set_language(bfo.lang)

    try:
        posted_date = bfo.fields('269__c')[0]
        # hack
        if posted_date.find("ERROR") > -1:
            posted_date = "Unknown date"
        else:
            date = datetime.datetime.strptime(posted_date, "%m/%d/%Y %I:%M:%S %p")
            posted_date = date.strftime("%Y/%m/%d %H:%M:%S")
    except:
        posted_date = "Unknown date"

    out = '<i class="icon-calendar"></i> <span class="post-posted-date"> %s </span>' % posted_date
    return out


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0


