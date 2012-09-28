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
corresponding blog
"""

from invenio.webblog_utils import get_posts
from invenio.search_engine import print_record


cfg_messages = {}
cfg_messages["in_issue"] = {"en": "Posts on this blog: ",
                            "fr": "Posts sur ce blog:"}


def format_element(bfo):
    """
    Displays the latest posts on a blog and it also offers
    a link to see all the posts of the corresponding blog
    """

    this_recid = bfo.control_field('001')
    current_language = bfo.lang
    blog_posts_recids = get_posts(this_recid, newest_first=True)
    out = ""
    if blog_posts_recids:
        # let's print just the 3 latest posts
        latest_blog_posts_recids = blog_posts_recids[:3]
        out += "<h4>%s</h4>" % cfg_messages["in_issue"][current_language]

        for post_recid in latest_blog_posts_recids:
            out += print_record(post_recid, format='hb')
            out += "<br />"

        all_posts = ""
        all_blog_posts_recids = blog_posts_recids[3:]
        for post_recid in all_blog_posts_recids:
            all_posts += print_record(post_recid, format='hb')
            all_posts += "<br />"

        out += """
            <script type="text/javascript">
            function displayAllPosts(){
                var all_posts = document.getElementById('all_posts');
                var see_all_link = document.getElementById('see_all_link');
                if (all_posts.style.display == 'none'){
                    all_posts.style.display = '';
                    see_all_link.innerHTML = "Hide"
                } else {
                    all_posts.style.display = 'none';
                    see_all_link.innerHTML = "Show all"
                }
            }
            </script>
            """

        out += '<span id="all_posts" style="">' + all_posts + '</span>'
        out += '<a class="moreinfo" id="see_all_link" \
                href="javascript:void(0)" onclick="displayAllPosts()""></a>'
        out += '<script type="text/javascript">displayAllPosts()</script>'

    return out


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
