#!/usr/bin/env python
# -*- coding: utf-8 -*-
## This file is part of CDS Invenio.
## Copyright (C) 2012, 2013 CERN.
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


from invenio.config import CFG_SITE_URL
from invenio.search_engine_utils import get_fieldvalues
from invenio.search_engine import perform_request_search

cfg_messages = {}
cfg_messages["in_issue"] = {"en": "Reference links",
                            "es": "Links de referencia"}

def format_element(bfo):
    """
Returns all the links used as references in a post
"""

    current_language = bfo.lang
    links = bfo.fields('856_0')
    menu_out = ""
    out = ""
    pop_id = 0

    if links:
        try:
            menu_title = '<h4>%s</h4>' % cfg_messages["in_issue"][current_language]
        except: # in english by default
            menu_title = '<h4>%s</h4>' % cfg_messages["in_issue"]["en"]

        out = """<div class="sidebar-nav">
                    <div class="well left-menu-well">
                    <ul class="nav nav-list">
                    <li class="nav-header"><div style="display:inline-block;">%s</div>
                    <div style="display:inline-block;">
                       <a id="see_all" href="javascript:void(0)" onclick="displayAllLinks()"></a>
                    </div></li>
                    """ % menu_title

        for link in links:
            link_url = link.get('u')
            link_data = link.get('y', link_url)
            link_title = link.get('z', '')
            pop_id = (pop_id+1)
            recid_in_archive = perform_request_search(p = link_url, f = '520__u')
            if link_data:
                if recid_in_archive:
                    link_icon = ''
                else:
                    link_icon = '  <i class="icon-external-link"></i>'
                menu_out += """<li class="divider"></li>"""
                menu_out += """<li><a href="%s"%s data-toggle="popover" id="pop_%s" >%s</a>""" % \
                    (link_url, link_title and ' title="%s"' % link_title or '' , pop_id, link_data + link_icon)
                # differentiate between links to sources inside
                # the archive and sources outside
                if recid_in_archive:
                    menu_out += \
                    '<script type="text/javascript"> $(function(){$("#pop_%s").popover({ trigger:"hover", title:"This content is also available in the archive ", html:true, delay: { show: 100, hide: 2000 }, ' % (pop_id)
                    try:
                        title = get_fieldvalues(recid_in_archive[0], "245__a")[0]
                    except:
                        title = "Unknown title"
                    archive_link = '<a href=%s/record/%s>%s</a>' % \
                                (CFG_SITE_URL, recid_in_archive[0], title)
                    menu_out += 'content: "%s" });}); </script>' % archive_link
                menu_out += """</li>"""
        menu_out += """<li class="divider"></li></ul></div></div>"""

        out += """
                <script type="text/javascript">
                function displayAllLinks(){
                    var reference_links = document.getElementById('reference_links');
                    var see_all = document.getElementById('see_all');
                    if (reference_links.style.display == 'none'){
                        reference_links.style.display = '';
                        see_all.innerHTML = '&nbsp; &nbsp;<i class="icon-double-angle-up big-icon"></i>'
                    } else {
                        reference_links.style.display = 'none';
                        see_all.innerHTML = ' &nbsp; &nbsp;<i class="icon-double-angle-down big-icon"></i>'
                    }
                }
                </script>
                """

        out += '<span id="reference_links" style="">' + menu_out + '</span>'
        out += '<script type="text/javascript">displayAllLinks()</script>'

    return out


def escape_values(bfo):
    """
Called by BibFormat in order to check if output of this element
should be escaped.
"""
    return 0
