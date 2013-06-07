# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2012 CERN.
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

"""
BibFormat element - TimeLine
"""

from invenio.webblog_utils import get_blog_descendants, transform_format_date
from invenio.htmlutils import escape_html
from invenio.bibformat_engine import BibFormatObject
from invenio.search_engine import call_bibformat
from lxml import etree

def format_element(bfo):
    """
    """

    recid = bfo.control_field('001')
    descendants = get_blog_descendants(recid)
    final_formatted_record = ""
 
    for record in descendants:
        child_bfo = BibFormatObject(record)
        posted_date = transform_format_date(child_bfo.fields('269__c')[0], "%Y/%m/%d %H:%M:%S")
        title = escape_html(child_bfo.fields('245__a')[0], escape_quotes=True)
        body = escape_html(call_bibformat(record, format='HTL'), escape_quotes=True)

        formatted_record = """<event start = "%s" title = "%s">""" % (posted_date, escape_html(title))
        formatted_record += body
        formatted_record += "</event>"
        xml_tree = etree.XML(formatted_record)
        final_formatted_record += etree.tostring(xml_tree, pretty_print=True)

    return final_formatted_record


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """

    return 0
