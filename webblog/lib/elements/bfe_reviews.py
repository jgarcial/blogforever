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
BibFormat Element - displays a link to the reviews of the record
"""

from invenio.config import CFG_SITE_URL, \
            CFG_WEBCOMMENT_ALLOW_COMMENTS, \
            CFG_WEBSEARCH_SHOW_REVIEW_COUNT
from invenio.webcommentadminlib import get_nb_reviews
from invenio.urlutils import create_html_link

def format_element(bfo):
    """
    Displays a link to the reviews of the record
    """
    
    out = ""
    this_recid = bfo.control_field('001')
    if CFG_WEBCOMMENT_ALLOW_COMMENTS and CFG_WEBSEARCH_SHOW_REVIEW_COUNT:
        num_reviews = get_nb_reviews(this_recid)
        if num_reviews > 0:
            message = """%i Reviews""" % num_reviews
            reviews_url = create_html_link(CFG_SITE_URL +\
                                           "/record/%s/reviews" % this_recid, {}, message)
            out = """| <i class="icon-eye-open"></i>  """ +  reviews_url
    return out


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0