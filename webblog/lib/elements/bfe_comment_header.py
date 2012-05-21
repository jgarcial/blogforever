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

"""BibFormat Element - creates the comment header """
from invenio.search_engine import search_pattern, record_exists
from invenio.bibformat_engine import BibFormatObject
from invenio.config import CFG_SITE_URL
from invenio.webblog_utils import get_parent_post, get_posts

cfg_messages = {}
cfg_messages["in_issue"] = {"en": "Also in this blog: ",
                            "fr": "Aussi dans ce blog: "}


def format_element(bfo):
    
    # get variables
    this_recid = bfo.control_field('001')
    current_language = bfo.lang

    post_recid = get_parent_post(this_recid)
    if not post_recid:
        post_recid = 1742
    bfo_post = BibFormatObject(post_recid)
    try:
        post_title = bfo_post.fields('245__a')[0]
    except:
        post_title = 'Untitled'

    try:
        date = bfo.fields('269__c')[0]
    except:
        date = ''

    # assemble the HTML output
    out = '<div id="top"><div id="topbanner">&nbsp;</div>'
    out += '<div id="mainmenu"><table width="100%">'
    out += '<tr>'
    out += '<td class="left"><a href="%s/record/%s%s">%s</a></div>' % (CFG_SITE_URL,
                                                    post_recid, (bfo.lang=="fr")
                                                    and "?ln=fr" or "?ln=en", post_title)

    out += '<td class="right">%s</td>' % date
    out += '</tr>'
    out += '<tr>'
    #if len(available_languages) > 1:
    #    if current_language == "en" and "fr" in available_languages:
    #        #TODO: server name generic
    #        out += '<td class="left"><a href="%s/record/%s?ln=fr">&gt;&gt; french version</a></td>' % (CFG_SITE_URL, this_recid)
    #    elif current_language == "fr" and "en" in available_languages:
    #        out += '<td class="left"><a href="%s/record/%s?ln=en">&gt;&gt; version anglaise</a></td>' % (CFG_SITE_URL, this_recid)

    out += '<td class="right"></td>'
    out += '</tr>'
    out += '</table></div><div id="mainphoto"></div></div>'

    return out


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
