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
BibFormat Element - creates the blog navigation menu
"""
from invenio.search_engine import search_pattern, record_exists
from invenio.bibformat_engine import BibFormatObject
from invenio.config import CFG_SITE_URL
from invenio.webblog_utils import get_parent_blog, get_posts


cfg_messages = {}
cfg_messages["in_issue"] = {"en": "Latest posts: ",
                            "fr": "Dernières posts:"}


def format_element(bfo):
    """
    Creates a navigation for articles in the same issue and category.
    """
    # get variables
    this_recid = bfo.control_field('001')
    menu_recids = []
    current_language = bfo.lang
    this_title = ""
    try:
        this_title = bfo.fields('245__a')[0]
    except:
        return ""

    blog_recid = get_parent_blog(this_recid)
    blog_rec = BibFormatObject(blog_recid)
    try:
        blog_title = blog_rec.fields('245__a')[0]
    except:
        blog_title = 'Untitled'

    menu_recids = get_posts(blog_recid, newest_first=True)

    menu_out = '<h4>%s</h4>' % cfg_messages["in_issue"][current_language]

    for recid in menu_recids:
        if str(this_recid) == str(recid):
            menu_out += '<div class="active"><div class="litem">%s</div></div>' % this_title
        else:
            temp_rec = BibFormatObject(recid)
            try:
                title = temp_rec.fields('245__a')[0]
            except:
                title = 'Untitled'
            menu_out += '<div class="litem"><a href="%s/record/%s%s">%s</a></div>' % (CFG_SITE_URL,
                                                                                      recid,
                                                                                      (bfo.lang=="fr") and "?ln=fr" or "",
                                                                                      title)

    return menu_out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0

if __name__ == "__main__":
    myrec = BibFormatObject(619)
    format(myrec)
