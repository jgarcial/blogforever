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
BibFormat Element - thumbnail
"""
from invenio.bibformat_engine import BibFormatObject
from invenio.config import CFG_SITE_URL


def format_element(bfo):
    """
    Displays the thumbnail on brief blog records
    """

    # get variables
    this_recid = bfo.control_field('001')
    current_language = bfo.lang
    files = bfo.fields('8564_')

    thumbnail_url = ''

    for f in files:
        if f['u'].find('Thumbnail') > -1:
            snapshot_url = f['u']

    record_url = "%s/record/%s?ln=%s" % (CFG_SITE_URL, this_recid, current_language)
    out = """<a href='%s'>
                <div style="background-image:url(%s);display:inline-block;height:100px;width:100px"></div>
            </a>""" % (record_url, snapshot_url)

    return out


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
