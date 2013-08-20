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
"""BibFormat element - Converts html based records to latex template.
"""

from invenio.latexutils import begin_document, end_document
from invenio.bibformat_elements import bfe_latex_title, bfe_latex_authors, \
    bfe_latex_record_dates, bfe_latex_abstract


def format_element(bfo, max_authors_len=60):
    """
    Displays only title, authors, posted and archived date and abstract
    of a record.

    @param max_authors_len: the maximum number of chars of the author name
        line.
    """
    try:
        max_authors_len = int(max_authors_len)
    except (ValueError, TypeError):
        max_authors_len = 60

    # Initialize document
    out = begin_document()

    # Print title
    out += bfe_latex_title.format_element(bfo)

    # Print authors
    out += bfe_latex_authors.format_element(bfo, width=max_authors_len)

    # Print post and record creation date
    out += bfe_latex_record_dates.format_element(bfo)

    # add \maketitle
    out += "\n\\maketitle\n"

    # Print abstract
    out += bfe_latex_abstract.format_element(bfo)

    # Finalized document
    out += end_document()

    return out


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0