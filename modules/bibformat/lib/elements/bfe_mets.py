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
BibFormat element - METS
"""

from invenio import bibingest as b
from lxml import etree

def format_element(bfo):
    """
    Returns the METS representation of the corresponding record
    """

    submission_id = bfo.control_field('002')
    record_collection = bfo.fields('980__a')[0]
    ingestion_pack = b.select(record_collection)
    formatted_record = ingestion_pack.get_one(submission_id)['content']
    xml_tree = etree.XML(formatted_record)
    final_formatted_record = etree.tostring(xml_tree, pretty_print=True)
    return final_formatted_record

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """

    return 0