#!/usr/bin/env python
# -*- coding: utf-8 -*-
## This file is part of CDS Invenio.
## Copyright (C) 2013 CERN.
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
BibFormat Element - displays Google translator link
"""

from invenio.config import CFG_TRANSLATE_RECORD_PREVIEW, CFG_SITE_LANG
from invenio.translate_utils import get_translate_script


def format_element(bfo):
    """
    Displays the Google translator link
    """

    current_language = bfo.lang
    language_of_blog_post = bfo.field("041__a")

    # Insert translate script
    out = ""
    if CFG_TRANSLATE_RECORD_PREVIEW:
        if current_language != language_of_blog_post:
            out += get_translate_script('to-be-translated', current_language, True)

    return out


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
