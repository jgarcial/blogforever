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
import cgi
from invenio.errorlib import register_exception

def APS_Print_Success(parameters, curdir, form, user_info=None):
    """Return a message to the referee saying that his/her
    decision has been taken into account.
    """

    global rn
    ## Get the name of the decision file:
    try:
        decision_filename = parameters['decision_file']
    except KeyError:
        decision_filename = ""

    ## Now try to read the decision from the decision_filename:
    if decision_filename in (None, "", "NULL"):
        ## We don't have a name for the decision file.
        ## For backward compatibility reasons, try to read the decision from
        ## a file called 'decision' in curdir:
        if os.path.exists("%s/decision" % curdir):
            try:
                fh_decision = open("%s/decision" % curdir, "r")
                decision = fh_decision.read()
                fh_decision.close()
            except IOError:
                ## Unable to open the decision file
                exception_prefix = "Error in WebSubmit function " \
                                   "APP_Print_Success. Tried to open " \
                                   "decision file [%s/decision] but was " \
                                   "unable to." % curdir
                register_exception(prefix=exception_prefix)
                decision = ""
            else:
                decision = decision.strip()
        else:
            decision = ""
    else:
        ## Try to read the decision from the decision file:
        try:
            fh_decision = open("%s/%s" % (curdir, decision_filename), "r")
            decision = fh_decision.read()
            fh_decision.close()
        except IOError:
            ## Oops, unable to open the decision file.
            decision = ""
            exception_prefix = "Error in WebSubmit function " \
                               "APP_Print_Success. Tried to open decision " \
                               "file [%s/%s] but was unable to." \
                               % (curdir, decision_filename)
            register_exception(prefix=exception_prefix)
        else:
            decision = decision.strip()

    ## Create the message:
    if decision != "":
        if decision == "approve":
            additional_info = "The blog record with reference number <b>%s</b> will be integrated into " \
                                "the repository ." % cgi.escape(rn)
        else:
            additional_info =  "The blog record with reference number <b>%s</b> will not be integrated into " \
                                      "the repository ."  % cgi.escape(rn)
        thanks = """<br />Thank you for your decision.<br />"""
        msg = """<br /><div style="padding-left:10px;">Your decision has been: <b>%(decision)s</b><br /><br /> %(additional_info)s <br /><br /> %(thanks)s</div><br /> """ \
              % {'decision': cgi.escape(decision),
                 'additional_info': additional_info,
                 'thanks': thanks
                }
    return msg
