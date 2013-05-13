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
BibFormat element - Last Post Date
"""

from invenio.webblog_utils import get_blog_descendants, transform_format_date
from invenio.htmlutils import escape_html
from invenio.bibformat_engine import BibFormatObject

def format_element(bfo):
    """
    """

    last_posted_date = ""
    recid = bfo.control_field('001')
    descendants = get_blog_descendants(recid)
   
    for record in descendants:
	child_bfo = BibFormatObject(record)
        posted_date = transform_format_date(child_bfo.fields('269__c')[0], "%Y/%m/%d %H:%M:%S")
	if posted_date == "Unknown date":
	    posted_date = "0000/00/00 00:00:00"

	if posted_date > last_posted_date:
	    last_posted_date = posted_date

    return last_posted_date

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """

    return 0
