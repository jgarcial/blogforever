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
BibFormat Element - displays the latest posts on a blog
and it also offers a link to see all the posts of the
corresponding blog in latex format
"""

from invenio.webblog_utils import get_posts
from invenio.search_engine import call_bibformat


cfg_messages = {}
cfg_messages["in_issue"] = {"en": "Posts in this blog",
                            "fr": "Posts sur ce blog"}


def format_element(bfo):
    """
    Displays the latest posts on a blog and it also offers
    a link to see all the posts of the corresponding blog
    """

    this_recid = bfo.control_field('001')
    current_language = bfo.lang
    blog_posts_recids = get_posts(this_recid)
    blog_posts_recids.reverse()
    out = ""
    if blog_posts_recids:
        try:
            out += "\\section{%s}" % cfg_messages["in_issue"][current_language]
        except: # in english by default
            out += "\\section{%s}" % cfg_messages["in_issue"]['en']

        posts = []
        for post_recid in blog_posts_recids:
            posts.append(call_bibformat(post_recid, format='PDFB'))

        out += """\\begin{center}
        \\hline
        \\end{center}""".join(posts)

    return out


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
