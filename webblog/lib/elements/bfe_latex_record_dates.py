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
BibFormat Element - Displays the archived and posted date of a record
"""

import datetime

from invenio.latexutils import format_latex_field
from invenio.webblog_utils import transform_format_date
from invenio.search_engine import get_creation_date


def format_element(bfo, format_latex=True):
    """
    Displays the archived and posted date of a record

    @param format_latex: Whether the result should be formatted as latex or
    returned as a plain text.
    @type format_latex: bool
    """
    recid = bfo.control_field('001')

    try:
        posted_date = transform_format_date(bfo.fields('269__c')[0])
        posted_date = "Posted Date: " + posted_date
    except:
        posted_date = ""

    record_creation_date = get_creation_date(recid)
    date = datetime.datetime.strptime(record_creation_date, "%Y-%m-%d")
    record_creation_date = "Archived date: " + date.strftime("%Y/%m/%d")

    out = posted_date
    if out:
        if format_latex:
            out += '\\\\'
        else:
            out += ' '
    out += record_creation_date

    if format_latex:
        out = format_latex_field("date", out, False)

    return out


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0