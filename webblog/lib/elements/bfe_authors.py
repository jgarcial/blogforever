# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013 CERN.
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

"""BibFormat element - Prints authors
"""

__revision__ = "$Id$"

import re
from urllib import quote
from cgi import escape
from invenio.config import CFG_SITE_URL
from invenio.messages import gettext_set_language


cfg_messages = {}
#cfg_messages["in_issue"] = {"en": "by",
#                            "es": "por",
#                            "fr": "par"}

def format_element(bfo):
    """
    Prints the authors of posts and comments
    """

    _ = gettext_set_language(bfo.lang)    # load the right message language

    authors = bfo.fields('100__a')

    out = '<i class="icon-user"></i>'
    if authors:
        # Process authors to add link, highlight and format affiliation
        for author in authors:
            if author:
 #               out = cfg_messages["in_issue"][bfo.lang]
                out += '  <a href="' + CFG_SITE_URL + \
                        '/search?f=author&amp;p=' + quote(author) + \
                        '&amp;ln=' + bfo.lang + \
                        '">' + escape(author) + '</a>'

    return out


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
