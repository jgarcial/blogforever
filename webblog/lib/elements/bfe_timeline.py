#!/usr/bin/env python
# -*- coding: utf-8 -*-
## This file is part of CDS Invenio.
## Copyright (C) 2012 CERN.
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
BibFormat Element - displays timeline slider for blogs
"""

from invenio.bibformat_elements.bfe_xtl_url import format_element as bfe_xtl_url
from invenio.bibformat_elements.bfe_last_post_date import format_element as bfe_last_post_date
from invenio.webblog_utils import get_posts


def format_element(bfo):
    """
    Returns the timeline slider
    """
    recid = bfo.control_field('001')
    
    if not len(get_posts(recid)):
        return ""

    else:
        data_source = bfe_xtl_url(bfo)
        data_initial_date = bfe_last_post_date(bfo)
    
        out = """<div id="tl"
                     data-source="%s"
                     data-initial-date="%s"
                     class="timeline-default dark-theme"
                     style="height: 350px; margin: 2em;">
                </div>""" % (data_source, data_initial_date)
    
        return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
