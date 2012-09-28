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
BibFormat Element - displays the latest comments on a post
and it also offers a link to see all the comments written on
the corresponding post
"""

from invenio.webblog_utils import get_comments
from invenio.search_engine import print_record


cfg_messages = {}
cfg_messages["in_issue"] = {"en": "Comments on this post: ",
                            "fr": "Commentaires sur ce post:"}

def format_element(bfo):
    """
    Displays comments on a post
    """

    this_recid = bfo.control_field('001')
    current_language = bfo.lang
    post_comments_recids = get_comments(this_recid, newest_first=True)
    out = ""
    if post_comments_recids:
        # let's print just the 3 latest posts
        latest_post_comments_recids = post_comments_recids[:2]
        out += "<h4>%s</h4>" % cfg_messages["in_issue"][current_language]

        for comment_recid in latest_post_comments_recids:
            out += print_record(comment_recid, format='hb')
            out += "<br />"

        all_comments = ""
        all_post_comments_recids = post_comments_recids[2:]
        for comment_recid in all_post_comments_recids:
            all_comments += print_record(comment_recid, format='hb')
            all_comments += "<br />"

        out += """
            <script type="text/javascript">
            function displayAllComments(){
                var all_comments = document.getElementById('all_comments');
                var see_all_link = document.getElementById('see_all_link');
                if (all_comments.style.display == 'none'){
                    all_comments.style.display = '';
                    see_all_link.innerHTML = "Hide"
                } else {
                    all_comments.style.display = 'none';
                    see_all_link.innerHTML = "Show all"
                }
            }
            </script>
            """

        out += '<span id="all_comments" style="">' + all_comments + '</span>'
        out += '<a class="moreinfo" id="see_all_link" \
                href="javascript:void(0)" onclick="displayAllComments()""></a>'
        out += '<script type="text/javascript">displayAllComments()</script>'

    return out


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
