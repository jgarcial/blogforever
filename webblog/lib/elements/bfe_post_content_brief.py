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
"""
BibFormat Element -
"""


__revision__ = "$Id$"

from invenio import bibformat_utils

def format_element(bfo, prefix, suffix, limit, max_chars, extension="[...] ", contextual="no",
                   highlight='no', escape="3", separator="<br/>", latex_to_html='no'):
    """ Prints the abstract of a post in HTML.


    @param prefix: a prefix for abstract
    @param limit: the maximum number of sentences of the abstract to display
    @param max_chars: the maximum number of chars of the abstract to display 
    @param extension: a text printed after abstracts longer than parameter 'limit'
    @param suffix: a suffix for abstract
    @parmm contextual if 'yes' prints sentences the most relative to user search keyword (if limit < abstract)
    @param highlight: if 'yes' highlights words from user search keyword
    @param escape: escaping method (overrides default escape parameter to not escape separators)
    @param separator: a separator between each abstract
    @param latex_to_html: if 'yes', interpret as LaTeX abstract
    """

    out = ""

    try:
        escape_mode_int = int(escape)
    except ValueError, e:
        escape_mode_int = 0

    abstract = bfo.fields('520__a', escape=escape_mode_int)
#    abstract.extend(bfo.fields('520__b', escape=escape_mode_int))
    abstract = separator.join(abstract)

    if contextual == 'yes' and limit != "" and \
           limit.isdigit() and int(limit) > 0:
        context = bibformat_utils.get_contextual_content(abstract,
                                                         bfo.search_pattern,
                                                         max_lines=int(limit))
        abstract = "<br/>".join(context)


    if abstract:
        out += prefix
        print_extension = False

        if max_chars != "" and max_chars.isdigit() and \
               int(max_chars) < len(abstract):
            print_extension = True
            abstract = abstract[:int(max_chars)]

        if limit != "" and limit.isdigit():
            s_abstract = abstract.split(". ") 

            if int(limit) < len(s_abstract):
                print_extension = True
                s_abstract = s_abstract[:int(limit)]

            out = '. '.join(s_abstract)

            # Add final dot if needed
            if abstract.endswith('.'):
                out += '.'

            if print_extension:
                out += " " + extension

        else:
            out += abstract

        out += suffix

        out += "<div></div>"
#
#    if highlight == 'yes':
#        out = bibformat_utils.highlight(out, bfo.search_pattern)
#
#    if latex_to_html == 'yes':
#        out = bibformat_utils.latex_to_html(out)

    return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
