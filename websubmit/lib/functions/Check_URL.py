## This file is part of Invenio.
## Copyright (C) 2007, 2008, 2009, 2010, 2011 CERN.
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

import cgi
import urllib
from httplib import urlsplit, HTTPConnection
from invenio.websubmit_config import InvenioWebSubmitFunctionStop
# from invenio.webbasket import url_is_valid

CFG_INVALID_URL = """
            <SCRIPT>
               document.forms[0].action="/submit";
               document.forms[0].curpage.value = 1;
               document.forms[0].step.value = 0;
               user_must_confirm_before_leaving_page = false;
               alert('The given url (%s) is invalid.');
               document.forms[0].submit();
            </SCRIPT>"""

def Check_URL(parameters, curdir, form, user_info=None):
    """Returns (True, status, reason) if the url is valid or
    (False, status, reason) if different."""


    try:
        f = open("%s/%s" % (curdir, parameters['url']), "r")
        url = f.read().replace("\n"," ")
        f.close()
    except:
        url = "The URL is needed"

    common_errors_list = [400, 404, 500]
    url_tuple = urlsplit(url)
    if not url_tuple[0]:
        url = "http://" + url
        url_tuple =  urlsplit(url)

    if not url_tuple[0] and not url_tuple[1]:
        #return (False, 000, "Not Valid")
        raise InvenioWebSubmitFunctionStop(CFG_INVALID_URL % (url,))
        
    # HTTPConnection had the timeout parameter introduced in python 2.6
    # for the older versions we have to get and set the default timeout
    # In order to use a custom timeout pass it as an extra argument to this function
    #old_timeout = getdefaulttimeout()
    #setdefaulttimeout(timeout)
    conn = HTTPConnection(url_tuple[1])
    #setdefaulttimeout(old_timeout)
    try:
        conn.request("GET", url_tuple[2])
    except:
        #return (False, 000, "Not Valid")
        raise InvenioWebSubmitFunctionStop(CFG_INVALID_URL % (url,))

    response = conn.getresponse()
    status = response.status
    reason = response.reason

    if str(status).startswith('1') or str(status).startswith('2') or str(status).startswith('3'):
        #return (True, status, reason)
        return ""

    elif str(status).startswith('4') or str(status).startswith('5'):
        if status in common_errors_list:
            #return (False, status, reason)
            raise InvenioWebSubmitFunctionStop(CFG_INVALID_URL % (url,))
        else:
            #return (True, status, reason)
            return ""
