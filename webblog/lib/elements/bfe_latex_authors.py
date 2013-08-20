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
BibFormat Element - Authors of the record in latex format.
"""
from invenio.config import CFG_WEBDIR

from invenio.latexutils import format_latex_field


def format_element(bfo, width=60, format_latex=True):
    """
    Prints the authors of a record.

    @param bfo:
    @param width: the maximum number of chars of the author name line.
        Warning: If it is more than 60, new line is used after each author
    @type width: int

    @param format_latex: Whether the result should be formatted as latex or
    returned as a plain text.
    @type format_latex: bool

    @return: Authors of a record.
    @rtype: str
    """

    author_list = bfo.fields('100__a')
    author_img = "\includegraphics[height=10, keepaspectratio=true]{%s}~"
    author_img %= (CFG_WEBDIR + "/img/default_avatar.png", )
    authors = ""
    if len(author_list) == 1:
        authors = str(author_list[0])
    elif len(author_list) > 1:
        last_author = author_list.pop()
        for author in author_list:
            authors += str(author) + ", "
        authors += str(last_author)
    if authors:
        if format_latex:
            authors = format_latex_field("author", authors)
            if len(authors) > int(width) and width:
                authors = authors.replace(",", "\\\\")
        else:
            authors = author_img + authors
        return authors
    return ""


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0