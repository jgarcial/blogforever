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
BibFormat Element - creates the blog navigation menu
"""
from invenio.bibformat_engine import BibFormatObject
from invenio.config import CFG_SITE_SECURE_URL
from invenio.webblog_utils import get_parent_blog, get_posts
import datetime

cfg_messages = {}
cfg_messages["in_issue"] = {"en": "More posts in this blog ",
                            "fr": "Plus posts dans ce blog "}


def format_element(bfo):
    """
    Creates a navigation menu in a post record with the links
    of the other posts in the same blog
    """
    # get variables
    this_recid = bfo.control_field('001')
    menu_recids = []
    menu_out = ""
    current_language = bfo.lang
    try:
        this_title = bfo.fields('245__a')[0]
    except:
        return "Unknown title"

    blog_recid = get_parent_blog(this_recid)
    menu_recids = get_posts(blog_recid)
    menu_recids.reverse()

    try:
        menu_title = '<h4>%s</h4>' % cfg_messages["in_issue"][current_language]
    except: # in english by default
        menu_title = '<h4>%s</h4>' % cfg_messages["in_issue"]['en']

    menu_out += """<div class="sidebar-nav">
                    <div class="well" style="width:250px; padding: 5px 0;">
                    <ul class="nav nav-list">
                    <li class="nav-header">%s</li>""" % menu_title

    for recid in menu_recids:
        temp_rec = BibFormatObject(recid)
        try:
            posted_date = temp_rec.fields('269__c')[0]
            # hack
            if posted_date.find("ERROR") > -1:
                posted_date = ""
            else:
                date = datetime.datetime.strptime(posted_date, "%m/%d/%Y %I:%M:%S %p")
                posted_date = date.strftime("%Y/%m/%d %H:%M:%S")
        except:
            posted_date = ""

        menu_out += """<li class="divider"></li>"""
        if str(this_recid) == str(recid):
            menu_out += '<li class="active">%s<br/><span><small>%s</small></span></li>' % (this_title, posted_date)
        else:
            try:
                title = temp_rec.fields('245__a')[0]
            except:
                title = 'Unknown title'
            menu_out += '<li><a href="%s/record/%s?ln=%s">%s</a><span><small>%s</small></span></li>' % (CFG_SITE_SECURE_URL,
                                                                      recid,
                                                                      bfo.lang,
                                                                      title, posted_date)
    menu_out += """<li class="divider"></li></ul></div></div>"""
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
