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


"""BibFormat element - Offers a link to download BagIt version of a record
"""

__revision__ = "$Id$"


from invenio.urlutils import create_html_link
from invenio.messages import gettext_set_language
from invenio.config import CFG_SITE_SECURE_URL
from invenio.bibarchive_archiver import get_record

def format_element(bfo, style):
    """
    Offers link to download the Bagit preservation file
    @param style: the CSS style to be applied to the link.
    """

    _ = gettext_set_language(bfo.lang)

    out = ""
    try:
        recid = bfo.control_field('001')
    except:
        raise Exception("Record not found")

    linkattrd = {}
    if style != '':
        linkattrd['style'] = style

    path = get_record(recid)['data']
    
    label = _("Download BagIt")

    
    
    out += create_html_link(CFG_SITE_SECURE_URL + "/record/"+str(recid)+"/bagit",
                              {},
                              link_label = label,
                              linkattrd = linkattrd)

    return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
