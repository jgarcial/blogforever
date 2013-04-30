#!/usr/bin/env python
# -*- coding: utf-8 -*-
## This file is part of CDS Invenio.
## Copyright (C) 2012, 2013 CERN.
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
from invenio.config import CFG_SITE_SECURE_URL
from invenio.webblog_utils import get_parent_post, get_comments
from invenio.bibformat_utils import get_contextual_content
import datetime


cfg_messages = {}
cfg_messages["in_issue"] = {"en": "More comments in this post ",
                            "fr": "Plus commentaires dans ce post "}


def format_element(bfo):
    """
    Creates a navigation menu in a comment record with the links
    of the other comments in the same post
    """

    # get variables
    this_recid = bfo.control_field('001')
    this_content = bfo.fields('520__a')[0]
    menu_out = ""
    try:
        this_author = bfo.fields('100__a')[0]
    except:
        this_author = ""

    this_limit_content = get_contextual_content(this_content,
                                                [],
                                                max_lines=1)[0]
    menu_recids = []
    current_language = bfo.lang
    post_recid = get_parent_post(this_recid)

    if post_recid:
        menu_recids = get_comments(post_recid)

        if menu_recids:
            try:
                menu_title = '<h4>%s</h4>' % cfg_messages["in_issue"][current_language]
            except: # in english by default
                menu_title = '<h4>%s</h4>' % cfg_messages["in_issue"]['en']

            menu_out += """<div class="sidebar-nav">
                <div class="well" style="width:250px; padding: 10px 10px;">
                <ul class="nav nav-list">
                <li class="nav-header">%s</li>""" % menu_title

            for recid in menu_recids:
                menu_out += """<li class="divider"></li>"""
                if str(this_recid) == str(recid):
                    menu_out += '<li class="active"><span><b><i class="icon-user"></i>%s</b> %s [...]</span></li>' % (this_author, this_limit_content)
                else:
                    temp_rec = BibFormatObject(recid)
                    content = temp_rec.fields('520__a')[0]
                    limit_content = get_contextual_content(content,
                                                           [],
                                                           max_lines=1)[0]
                    try:
                        author = temp_rec.fields('100__a')[0]
                    except:
                        this_author = ""
                    menu_out += '<li><a href="%s/record/%s?ln=%s"><span><b><i class="icon-user"></i>%s</b> %s [...]</spam></a></li>' % \
                                    (CFG_SITE_SECURE_URL, recid, bfo.lang, author, limit_content)
            menu_out += """<li class="divider"></li></ul></div></div>"""

    return menu_out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
