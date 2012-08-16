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

__revision__ = "$Id$"

import os
import re
from invenio.errorlib import register_exception
from invenio.search_engine import perform_request_search, record_exists
from invenio.search_engine_utils import get_fieldvalues
from invenio.websubmit_config import InvenioWebSubmitFunctionStop

CFG_ALERT_RECORD_NOT_FOUND = """\n<script type="text/javascript">
document.forms[0].action="/submit";
document.forms[0].curpage.value=1;
document.forms[0].step.value=0;
user_must_confirm_before_leaving_page = false;
alert('The record with record ID [%s] cannot be found in our """ \
"""database.\\n\\nPerhaps it has been deleted or it has not been integrated yet.\\n""" \
"""You can choose another record ID or retry this action in a few minutes.');\n
document.forms[0].submit();
</script>"""

CFG_MODIFY_BLOG_ERROR = """
            <SCRIPT>
               document.forms[0].action="/submit";
               document.forms[0].curpage.value = 1;
               document.forms[0].step.value = 0;
               user_must_confirm_before_leaving_page = false;
               alert('It is just possible to modify blog metadata. \\nPlease enter a blog recid.');
               document.forms[0].submit();
            </SCRIPT>"""

CFG_DELETE_BLOG_ERROR = """
            <SCRIPT>
               document.forms[0].action="/submit";
               document.forms[0].curpage.value = 1;
               document.forms[0].step.value = 0;
               user_must_confirm_before_leaving_page = false;
               alert('It is just possible to delete a blog record. \\nPlease enter a blog recid.');
               document.forms[0].submit();
            </SCRIPT>"""

CFG_DELETE_POST_ERROR = """
            <SCRIPT>
               document.forms[0].action="/submit";
               document.forms[0].curpage.value = 1;
               document.forms[0].step.value = 0;
               user_must_confirm_before_leaving_page = false;
               alert('It is just possible to delete a post record. \\nPlease enter a post recid.');
               document.forms[0].submit();
            </SCRIPT>"""

def Get_Recid_Number(parameters, curdir, form, user_info=None):
    """
    This function gets the value contained in the [edsrn] file and
    stores it in the 'rn' global variable which is the recid of the
    corresponding record.

    Parameters:

    * edsrn: Name of the file which stores the reference.  This
    value depends on the web form configuration you
    did. It should contain the name of the form element
    used for storing the reference of the document.
    """

    global rn, sysno

    # Path of file containing recid
    if os.path.exists("%s/%s" % (curdir, parameters['edsrn'])):
        try:
            fp = open("%s/%s" % (curdir, parameters['edsrn']), "r")
            rn = fp.read()
            rn = re.sub("[\n\r ]+", "", rn)
        except IOError:
            exception_prefix = "Error in WebSubmit function " \
                                "Get_Recid_Number. Tried to open " \
                                "edsrn file [%s/edsrn] but was " \
                                "unable to." % curdir
            register_exception(prefix=exception_prefix)
            rn = ""

    else:
        rn = ""

    if rn:
        act = form['act']
        if act not in ['APS']:
            try:
                if record_exists(int(rn)) == 1:
                    sysno = int(rn)
                    coll = get_fieldvalues(sysno, '980__a')[0]
                    if act == 'MBI':
                        if coll not in ['BLOG']:
                            raise InvenioWebSubmitFunctionStop(CFG_MODIFY_BLOG_ERROR)
                    if act == 'DBI':
                        if coll not in ['BLOG']:
                            raise InvenioWebSubmitFunctionStop(CFG_DELETE_BLOG_ERROR)
                    if act == 'DPI':
                        if coll not in ['BLOGPOST']:
                            raise InvenioWebSubmitFunctionStop(CFG_DELETE_POST_ERROR)
                else:
                    raise InvenioWebSubmitFunctionStop(CFG_ALERT_RECORD_NOT_FOUND % rn)
            except:
                raise InvenioWebSubmitFunctionStop(CFG_ALERT_RECORD_NOT_FOUND % rn)

    return ""
