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
BibFormat Element - displays the author of a comment record
"""

from invenio.config import CFG_SITE_URL
import cgi

cfg_messages = {}
cfg_messages["in_issue"] = {"en": "wrote",
                            "fr": "a écrit"}

def format_element(bfo):
    """
    Displays the author of a comment record
    """

    author = bfo.field('100__a')
    current_language = bfo.lang
    out = """<a href = "%s/search?ln=%s&p=%s&f=author"> <i class="icon-col-Comments"></i> %s</a> %s:""" % \
                (CFG_SITE_URL, current_language, author, author, \
                 cfg_messages["in_issue"][current_language])

    return out
    
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
