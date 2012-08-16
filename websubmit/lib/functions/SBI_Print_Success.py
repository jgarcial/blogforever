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

from invenio.config import CFG_SITE_NAME
from invenio.websubmit_functions.Shared_Functions import get_nice_bibsched_related_message, txt2html


def SBI_Print_Success(parameters, curdir, form, user_info=None):
    """
    This function simply displays a text on the screen telling the
    user that the submission went fine.

    Parameters:

       * status: Depending on the value of this parameter, the
         function adds an additional text to the email.
         This parameter can be one of:
           - ADDED: The file has been integrated in the database.
           - APPROVAL: The file has been sent for approval to a referee.
                       or can stay empty.

       * edsrn: Name of the file containing the reference of the
                blog record

    """

    global rn
    t = ""
    status = parameters['status']
    t += Request_Print("A",  """<br /><br /><span style="padding-left:10px;"><b>Submission complete!</b></span><br /><br />""")
    t += Request_Print("A",  """<span style="padding-left:10px;">Your blog record has the following reference number: <b>%s</b></span>&nbsp;&nbsp;<br /><br />""" % (rn))
    if status == "APPROVAL":
        t += Request_Print("A",  """<span style="padding-left:10px;">An email has been sent to the referee.</span><br />""")
        t += Request_Print("A",  """<span style="padding-left:10px;">You will be warned by email as soon as the referee takes his/her decision regarding your blog record.&nbsp;&nbsp;</span><br /><br />""")
    if status == "ADDED":
        t += Request_Print("A",  """<span style="padding-left:10px;">It will be soon available on our repository.</span><br /><br />\n""")
    t += Request_Print("A",  """<span style="padding-left:10px;">Thank you for using %s!&nbsp;&nbsp;</span>""" % CFG_SITE_NAME)
    t += Request_Print("A",  "<br /><br /><br /><br />")
    # t += txt2html(get_nice_bibsched_related_message(curdir))
    return t
