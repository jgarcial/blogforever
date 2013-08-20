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
BibFormat Element - creates the comment header
"""

from invenio.bibformat_engine import BibFormatObject
from invenio.latexutils import format_latex_field
from invenio.webblog_utils import get_parent_post


def format_element(bfo):
    """
    Formats comments header using the post's name
    """

    this_recid = bfo.control_field('001')

    post_recid = get_parent_post(this_recid)
    post_rec = BibFormatObject(post_recid)
    try:
        post_title = post_rec.fields('245__a')[0]
    except:
        post_title = 'Untitled'

    return format_latex_field('title', 'Comment on post: ' + post_title)


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
