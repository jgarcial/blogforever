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
BibFormat Element - displays the number of comments
for the corresponding post
"""

from invenio.config import CFG_SITE_SECURE_URL
from invenio.webblog_utils import get_comments


def format_element(bfo):
    """
    Displays the number of comments for the corresponding post
    """

    this_recid = bfo.control_field('001')
    current_language = bfo.lang
    post_comments_recids = get_comments(this_recid)
    post_url = bfo.fields('520__u')[0]

    message = "%i Comments" % len(post_comments_recids)
    out = ""
    if post_comments_recids:
        out = """<span><a href="%s/search?p=773__o:%s&cc=Comments">%s</a></span>""" % \
                (CFG_SITE_SECURE_URL, post_url, message)
    else:
        out = """<span>No comments yet</span>"""
    return out


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
