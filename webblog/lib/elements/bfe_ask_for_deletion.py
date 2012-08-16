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

"""BibFormat element - Offers action to delete a blog or a post
"""

__revision__ = "$Id$"


from invenio.urlutils import create_html_link
from invenio.messages import gettext_set_language
from invenio.config import CFG_SITE_URL
from invenio.access_control_config import SUPERADMINROLE
from invenio.access_control_admin import acc_is_user_in_role, acc_get_role_id

def format_element(bfo, style):
    """
    Offers action to delete a blog or a post
    @param style: the CSS style to be applied to the link.
    """

    _ = gettext_set_language(bfo.lang)

    out = ""
    if bfo.user_info['email'] not in ["guest"]:
        coll = bfo.fields("980__a")[0]
        if coll in ['BLOG', 'BLOGPOST']:
            linkattrd = {}
            if style != '':
                linkattrd['style'] = style
    
            try:
                recid = bfo.control_field('001')[0]
            except:
                raise Exception("Record not found")
    
            if coll == 'BLOG':
                act = 'DBI'
                if acc_is_user_in_role(bfo.user_info, acc_get_role_id(SUPERADMINROLE)):
                    doctype = 'BSI'
                    sub =  'DBIBSI'
                else:
                    doctype = 'BSIREF'
                    sub =  'DBIBSIREF'
    
            elif coll == 'BLOGPOST':
                act = 'DPI'
                if acc_is_user_in_role(bfo.user_info, acc_get_role_id(SUPERADMINROLE)):
                    doctype = 'BSI'
                    sub =  'DPIBSI'
                else:
                    doctype = 'BSIREF'
                    sub =  'DPIBSIREF'
    
            out += create_html_link(CFG_SITE_URL + "/submit",
                                    {'ln': bfo.lang,
                                    'doctype': doctype,
                                    'indir': 'delete',
                                    'act': act,
                                    'sub': sub,
                                    'BSI_RN': recid},
                                    link_label = _("Ask for Deletion"),
                                    linkattrd = linkattrd)

    return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
