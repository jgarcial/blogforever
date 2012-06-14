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
BibFormat Element - displays the tags of a blog and/or blog post
"""

from invenio.config import CFG_SITE_URL

cfg_messages = {}
cfg_messages["in_issue"] = {"en": "Tags",
                            "es": "Etiquetas",
                            "fr": "Balises"}

def format_element(bfo):
    """
    Returns all the tags of the correspoding blog or blogpost
    """

    current_language = bfo.lang
    #TODO: to decide new MARC tag for tags
    tags = bfo.fields('653__1')

    out = ""

    if tags:
        out += """<span style="font-size:smaller;font-weight:bold;color:#0D2B88;" >%s:</span> <span class="moreinfo">""" % \
            cfg_messages["in_issue"][current_language]

        for tag in tags:
            out += """<a href = "%s/search?ln=%s&p=%s">%s</a>  """ % (CFG_SITE_URL, current_language, tag, tag)

        out += """</span>"""
    return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
