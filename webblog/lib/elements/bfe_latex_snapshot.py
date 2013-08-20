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
BibFormat Element - displays snapshot
"""
from invenio.bibdocfile import bibdocfile_url_to_fullpath
from invenio.bibformat_pdf_with_latex_template_config import \
    CFG_BIBFORMAT_LATEX_REPRESENTATION_OF_HTML_TAGS


def format_element(bfo):
    """
    Displays the snapshot
    """

    files = bfo.fields('8564_')

    snapshot_url = ''

    for f in files:
        if f['u'].find('SnapShot_') > -1:
            snapshot_url = f['u']

    image_path = bibdocfile_url_to_fullpath(snapshot_url)

    out = CFG_BIBFORMAT_LATEX_REPRESENTATION_OF_HTML_TAGS['img']['start']

    return out % {
        'size_config': "width=\\textwidth, keepaspectratio=true",
        'path': image_path,
        'caption': ""
    }


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
