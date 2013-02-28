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
BibFormat Element - displays disclaimer on all blog records
"""

from invenio.config import CFG_SITE_URL


def format_element(bfo):
    """
    Returns the disclaimer notifying that what the user
    is seeing is just a copy of the original blog element
    """

    current_language = bfo.lang
    this_recid = bfo.control_field('001')
    coll = bfo.field('980__a')
    elem_url = bfo.field('520__u')
    out = ""

    elem_html_url = """<a href = '%(url)s'>To go to the original click here</a>""" % {'url': elem_url}
    disclaimer_content = "<strong>Disclaimer: </strong> The content of this %s is an archived copy. " % coll.lower()
    out = """<div class="bottom-left-folded">%(disclaimer)s</div>
    """ % {'disclaimer': '<div class="disclaimer alert">&nbsp;%(disclaimer_content)s  %(url)s</div>' %
           {'disclaimer_content': disclaimer_content,
            'url': elem_html_url}}

    return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0