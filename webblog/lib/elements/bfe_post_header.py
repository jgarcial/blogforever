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
BibFormat Element - creates the post header
"""

from invenio.bibformat_engine import BibFormatObject
from invenio.config import CFG_SITE_URL
from invenio.webblog_utils import get_parent_blog


def format_element(bfo):
    """
    Formats posts header using the blog's name and
    the date in which the post was created
    """

    this_recid = bfo.control_field('001')

    blog_recid = get_parent_blog(this_recid)
    blog_rec = BibFormatObject(blog_recid)
    try:
        blog_title = blog_rec.fields('245__a')[0]
    except:
        blog_title = 'Untitled'

    try:
        creation_date = bfo.fields('269__c')[0]
    except:
        creation_date = ""

    out = '<div id="top"><div id="topbanner">&nbsp;</div>'
    out += '<div id="mainmenu"><table width="100%">'
    out += '<tr><td class="left"><a href="%s/record/%s?%s">%s</a>' % (CFG_SITE_URL,
                                                                     blog_recid, bfo.lang, blog_title)

    out += '<td class="right">%s</td>' % creation_date
    out += '</td></tr></table></div></div>'
    out += '<div id="mainphoto"></div>'

    return out


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
