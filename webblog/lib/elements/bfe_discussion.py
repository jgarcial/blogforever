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
BibFormat Element - 
"""

from invenio.config import CFG_SITE_SECURE_URL, \
            CFG_WEBCOMMENT_ALLOW_COMMENTS, \
            CFG_WEBSEARCH_SHOW_COMMENT_COUNT
from invenio.webcommentadminlib import get_nb_comments
from invenio.urlutils import create_html_link

def format_element(bfo):
    """
    Returns
    """

    current_language = bfo.lang
    this_recid = bfo.control_field('001')
    if CFG_WEBCOMMENT_ALLOW_COMMENTS and CFG_WEBSEARCH_SHOW_COMMENT_COUNT:
        num_comments = get_nb_comments(this_recid)
        if num_comments > 0:
            message = """Follow discussion """
            comments_url = create_html_link(CFG_SITE_SECURE_URL +\
                                           "/record/%s/comments" % this_recid, {}, message)
            out = """| <i class="icon-group"></i>  """ +  comments_url
    return out


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0