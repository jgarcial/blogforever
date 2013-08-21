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
BibFormat Element - displays the topic of the parent blog
"""

from invenio.config import CFG_SITE_URL
from invenio.urlutils import create_html_link

cfg_messages = {}
cfg_messages["in_issue"] = {"en": "Topic",
                            "es": "Tema"}

def format_element(bfo):
    """
    Returns all the topics of the corresponding parent blog
    """

    current_language = bfo.lang
    topics = bfo.fields('654__a')

    try:
        out = '<h4><i class="icon-picture"></i>&nbsp;%s</h4>' % cfg_messages["in_issue"][current_language]
    except: # in english by default
        out = '<h4><i class="icon-picture"></i>&nbsp;%s</h4>' % cfg_messages["in_issue"]['en']

    if topics:
        for topic in topics:
            url = create_html_link(CFG_SITE_URL + "/search", \
                                    {'p': '654__a:"%s"' % topic, \
                                     'ln': current_language}, topic, linkattrd = {'style':"color:white"})
            out += '<span class="label label-success">%s</span>&nbsp;&nbsp;' % url
    else:
        out += '<span>No topic yet</span>'

    return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0