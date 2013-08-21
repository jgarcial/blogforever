# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2006, 2007, 2008, 2009, 2010, 2011 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""BibFormat element - Prints short title
"""

__revision__ = "$Id$"
from invenio.config import CFG_SITE_URL
from cgi import escape
from invenio.webblog_utils import get_parent_post
from invenio.bibformat_engine import BibFormatObject


def format_element(bfo, highlight="no", multilang='no'):
    """
    Prints a short title, suitable for brief format.

    @param highlight: highlights the words corresponding to search query if set to 'yes'
    """

    if bfo.field('980__a') == "COMMENT":
        this_recid = bfo.control_field('001')
        post_recid = get_parent_post(this_recid)
        post_rec = BibFormatObject(post_recid)
        try:
            post_title = post_rec.fields('245__a')[0]
        except:
            post_title = 'Untitled'

        parent_type = bfo.field('773__4')
        title = "Comment on %s: %s" % (escape(parent_type.lower()), escape(post_title))

    else:
        try:
            title = bfo.field('245__a')
        except:
            title = 'Untitled'

    this_recid = bfo.control_field('001')
    current_language = bfo.lang

    out = """<span><a href="%s/record/%s?ln=%s">%s</a></span>""" % (CFG_SITE_URL, this_recid, current_language, escape(title))

    return out


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0