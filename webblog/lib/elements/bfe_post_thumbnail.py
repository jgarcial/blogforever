#!/usr/bin/env python
# -*- coding: utf-8 -*-
## This file is part of CDS Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007 CERN.
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
BibFormat Element - thumbnail of the post
"""
from invenio.bibformat_engine import BibFormatObject
from invenio.config import CFG_SITE_URL
from invenio.webjournal_utils import get_release_datetime, issue_to_datetime, get_journal_preferred_language
from invenio.dateutils import get_i18n_day_name, get_i18n_month_name


def format_element(bfo):
    """
    Returns the url of the previous post record in the current language.
    """

    # get variables
    this_recid = bfo.control_field('001')
    files = bfo.fields('8564_')

    thumbnail_url = ''
    snapshot_url = ''

    for f in files:
        if f['u'].find('TL_') > -1:
            thumbnail_url = f['u']
        elif f['u'].find('snapshot') > -1:
            snapshot_url = f['u']

    # assemble the HTML output
    img = '<img src="%s">' % (thumbnail_url)
    out = '<a href="%s" target="_blank">%s</a>' % (snapshot_url, img)

    return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0

if __name__ == "__main__":
    myrec = BibFormatObject(619)
    format(myrec)
