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
BibFormat Element - adds the latest comments to its post
"""

from invenio.webblog_utils import get_comments
from invenio.search_engine import print_record

cfg_messages = {}
cfg_messages["in_issue"] = {"en": "Here you can see the comments on this post: ",
                            "fr": "Ici vous pouvez voir les commentaires sur ce post:"}
def format_element(bfo):
    """
    """

    this_recid = bfo.control_field('001')
    current_language = bfo.lang
    post_comments_recids = get_comments(this_recid, newest_first=True)
    out = ""

    if post_comments_recids:
        out += "<h4>%s</h4>" % cfg_messages["in_issue"][current_language]

        for comment_recid in post_comments_recids:
            out += print_record(comment_recid, format='hb')
            out += "<br />"

    return out
    
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0