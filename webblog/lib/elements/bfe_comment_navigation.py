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
BibFormat Element - creates the comment navigation menu
"""

from invenio.bibformat_engine import BibFormatObject
from invenio.config import CFG_SITE_URL
from invenio.webblog_utils import get_parent_post, get_comments
from invenio.bibformat_utils import get_contextual_content


cfg_messages = {}
cfg_messages["in_issue"] = {"en": "Other comments on this post: ",
                            "es": "Otros comentarios sobre la misma entrada: "}


def format_element(bfo):
    """
    Creates a navigation for comments.
    """

    # get variables
    this_recid = bfo.control_field('001')
    try:
        this_content = bfo.fields('520__a')[0]
    except:
        return ""
    try:
        this_author = bfo.fields('100__a')[0]
    except:
        return ""

    this_limit_content = get_contextual_content(this_content,
                                                [],
                                                max_lines=2)[0]
    menu_recids = []
    current_language = bfo.lang

    post_recid = get_parent_post(this_recid)

    menu_recids = get_comments(post_recid, newest_first=True)

    menu_out = '<h4>%s</h4>' % cfg_messages["in_issue"][current_language]

    for recid in menu_recids:
        if str(this_recid) == str(recid):
            menu_out += '<div class="active"><div class="litem"><b>%s</b>: %s [...]</div></div>' % (this_author, this_limit_content)
        else:
            temp_rec = BibFormatObject(recid)
            content = temp_rec.fields('520__a')[0]
            limit_content = get_contextual_content(content,
                                                   [],
                                                   max_lines=1)[0]

            try:
                author = temp_rec.fields('100__a')[0]
            except:
                author = 'Anonymous'
            menu_out += '<div class="litem"><a href="%s/record/%s%s"><b>%s</b>: %s [...]</a></div>' % (CFG_SITE_URL,
                                                                                                recid,
                                                                                                (bfo.lang=="fr") and "?ln=fr" or "?ln=en",
                                                                                                author, limit_content)
            

        
    return menu_out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
