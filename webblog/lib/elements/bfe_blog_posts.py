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
BibFormat Element - adds the latest post to its blog
"""

from invenio.webblog_utils import get_parent_blog, get_posts
from invenio.search_engine import print_record


cfg_messages = {}
cfg_messages["in_issue"] = {"en": "Latest posts: ",
                            "fr": "Dernières posts:"}


def format_element(bfo):
    """
    """

    # get variables
    this_recid = bfo.control_field('001')
    current_language = bfo.lang
    blog_recid = get_parent_blog(this_recid)
    blog_posts_recids = get_posts(blog_recid, newest_first=True)
    out = ""

    if blog_posts_recids:
        out += "<h4>%s</h4>" % cfg_messages["in_issue"][current_language]

        for post_recid in blog_posts_recids:
            out += print_record(post_recid, format='hb')
            out += "<br />"

    return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
