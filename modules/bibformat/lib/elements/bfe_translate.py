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
from invenio.config import CFG_TRANSLATE_RECORD_PREVIEW
"""
BibFormat Element - displays Google translator link
"""

from invenio.search_engine_utils import get_fieldvalues
from invenio.translate_utils import get_translate_script
from translate_utils import match_language_code


def format_element(bfo):
    """
    Displays the Google translator link
    """

    if not CFG_TRANSLATE_RECORD_PREVIEW:
        return ""

    record_langs = get_fieldvalues(bfo.recID, '041%')

    if not record_langs:
        return get_translate_script('to-be-translated', bfo.lang, True)

    for lang in record_langs:
        if not match_language_code(bfo.lang, lang):
            return get_translate_script('to-be-translated', bfo.lang, True)

    return ""


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
