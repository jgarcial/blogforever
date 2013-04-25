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
BibFormat Element - creates a menu containing all the links in a post
"""


from invenio.config import CFG_SITE_SECURE_URL
from invenio.search_engine_utils import get_fieldvalues
from invenio.search_engine import perform_request_search

cfg_messages = {}
cfg_messages["in_issue"] = {"en": "Reference links on this post",
                            "es": "Links de referencia en este post"}

def format_element(bfo):
    """
Returns all the links used as references in a post
"""

    current_language = bfo.lang
    links = bfo.fields('856_0')
    menu_out = ""
    pop_id = 0

    if links:
        try:
            menu_out += '<h4>%s:</h4>' % cfg_messages["in_issue"][current_language]
        except: # in english by default
            menu_out += '<h4>%s:</h4>' % cfg_messages["in_issue"]["en"]

    for link in links:
        link_url = link.get('u')
        link_data = link.get('y', link_url)
        link_title = link.get('z', '')
        pop_id = (pop_id+1)
        if link_data:
            menu_out += '<div class="litem"><a href="%s"%s data-toggle="popover" id="pop_%s" >%s</a>' % \
                (link_url, link_title and ' title="%s"' % link_title or '' , pop_id, link_data)
            recid_in_archive = perform_request_search(p = link_url, f = '520__u')
            # differentiate between links to sources inside
            # the archive and sources outside
            if recid_in_archive:
                menu_out += ' <i class="icon-asterisk"></i>'
                menu_out += \
                '<script type="text/javascript"> $(function(){$("#pop_%s").popover({ trigger:"hover", title:"This content is also available in the archive: ", html:true, delay: { show: 100, hide: 5000 }, ' % (pop_id)
                try:
                    title = get_fieldvalues(recid_in_archive[0], "245__a")[0]
                except:
                    title = "Untitled"
                archive_link = '<a href=%s/record/%s><i class=icon-arrow-right></i> %s</a>' % \
                            (CFG_SITE_SECURE_URL, recid_in_archive[0], title)
                menu_out += 'content: "%s" });}); </script>' % \
                    (archive_link)
            menu_out += '</div>'
    return menu_out



def escape_values(bfo):
    """
Called by BibFormat in order to check if output of this element
should be escaped.
"""
    return 0