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
from invenio.webblog_utils import get_parent_blog, get_posts, transform_format_date
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
    out = ""
    menu_out = ""
    current_language = bfo.lang
    try:
        this_title = bfo.fields('245__a')[0]
    except:
        return "Unknown title"

    blog_recid = get_parent_blog(this_recid)
    menu_recids = get_posts(blog_recid)

    if menu_recids:
        menu_recids.reverse()
        latest_posts = menu_recids[:6]

        try:
            menu_title = '<h4>%s</h4>' % cfg_messages["in_issue"][current_language]
        except: # in english by default
            menu_title = '<h4>%s</h4>' % cfg_messages["in_issue"]['en']

        menu_out += """<div class="sidebar-nav">
                        <div class="well left-menu-well">
                        <ul class="nav nav-list">
                        <li class="nav-header">%s</li>""" % menu_title

        for recid in latest_posts:
            temp_rec = BibFormatObject(recid)
	    posted_date = transform_format_date(temp_rec.fields('269__c')[0], "%Y/%m/%d %H:%M:%S")
	    # HACK
	    if posted_date == "Unknown date":
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

        all_posts = menu_recids[6:]
        if all_posts:
            for recid in all_posts:
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

                out += """<li class="divider"></li>"""
                if str(this_recid) == str(recid):
                    out += '<li class="active">%s<br/><span><small>%s</small></span></li>' % (this_title, posted_date)
                else:
                    try:
                        title = temp_rec.fields('245__a')[0]
                    except:
                        title = 'Unknown title'
                    out += '<li><a href="%s/record/%s?ln=%s">%s</a><br/><span><small>%s</small></span></li>' % (CFG_SITE_SECURE_URL,
                                                                                                           recid,
                                                                                                           bfo.lang,
                                                                                                           title, posted_date)
            out += """<li class="divider"></li>"""

            out += """
                <script type="text/javascript">
                function displayAllPosts(){
                    var all_posts_menu = document.getElementById('all_posts_menu');
                    var see_all_link = document.getElementById('see_all_link');
                    if (all_posts_menu.style.display == 'none'){
                        all_posts_menu.style.display = '';
                        see_all_link.innerHTML = '  <i class="icon-double-angle-up big-icon"></i>'
                    } else {
                        all_posts_menu.style.display = 'none';
                        see_all_link.innerHTML = '  <i class="icon-double-angle-down big-icon"></i>'
                    }
                }
                </script>
                """

            menu_out += '<span id="all_posts_menu" style="">' + out + '</span>'
            menu_out += '<div style="padding-left: 215px;"> \
                            <a id="see_all_link" href="javascript:void(0)" onclick="displayAllPosts()""></a>\
                        </div>'
            menu_out += '<script type="text/javascript">displayAllPosts()</script>'

        menu_out += """</ul></div></div>"""

    return menu_out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
