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


"""
BibFormat Element - displays the archived and/or the posted dates
"""

from invenio.search_engine import get_creation_date
from invenio.webblog_utils import transform_format_date
import datetime

def format_element(bfo):
    """
    Displays the archived and/or the posted dates
    """

    recid = bfo.control_field('001')
    out = ""
    try:
        posted_date = transform_format_date(bfo.fields('269__c')[0])
    except:
        posted_date = ""
    record_creation_date = get_creation_date(recid)
    date = datetime.datetime.strptime(record_creation_date, "%Y-%m-%d")
    record_creation_date = date.strftime("%Y/%m/%d")

    if posted_date:
        out = '<h4><i class="icon-calendar"></i> Posted date </h4> <span class="post-posted-date"> %s </span><br/>' % posted_date
    if record_creation_date:
        out += '<h4><i class="icon-calendar"></i> Archived date </h4><span class="post-posted-date"> %s </span> ' % record_creation_date
    return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if
    output of this element should be escaped.
    """

    return 0
