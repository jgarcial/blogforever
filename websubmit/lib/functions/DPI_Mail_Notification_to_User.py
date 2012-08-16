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

from invenio.config import CFG_SITE_NAME, \
     CFG_SITE_URL, \
     CFG_SITE_SUPPORT_EMAIL, \
     CFG_SITE_RECORD

from invenio.websubmit_config import CFG_WEBSUBMIT_COPY_MAILS_TO_ADMIN
from invenio.websubmit_functions.Shared_Functions import get_nice_bibsched_related_message, ParamFromFile
from invenio.mailutils import send_email
from invenio.search_engine import get_fieldvalues

def DPI_Mail_Notification_to_User(parameters, curdir, form, user_info=None):
    """
    This function sends an email to the user who deleted a post record
    saying that the order has been received
    """

    global rn, sysno
    FROMADDR = '%s Submission Engine <%s>' % (CFG_SITE_NAME,CFG_SITE_SUPPORT_EMAIL)

    post_title = "".join(["%s" % title.strip() for title in \
                         get_fieldvalues(int(sysno), "245__a")])

    post_url = "".join(["%s" % url.strip() for url in \
                        get_fieldvalues(int(sysno), "520__u")])

    m_recipient = user_info["email"]

    # create email body
    email_txt = "\nThe order to delete the post record with URL [%s] and title '%s' has been correctly received.\n\n" % (post_url, post_title)
    if parameters['status'] == "APPROVAL":
        email_txt =  email_txt + "An email has been sent to the referee. You will be warned by email as soon as the referee takes his/her decision \nregarding your post record.\n\n"

    # email_txt += get_nice_bibsched_related_message(curdir)
    email_txt = email_txt + "Thank you for using %s Submission Interface.\n" % CFG_SITE_NAME

    email_subject = "Post record deletion order received: [%(id)s]"
    if post_title:
        email_subject = email_subject % {'id' : post_title}
    else:
        email_subject = email_subject % {'id' : post_url}

    ## send the mail, if there are any recipients or copy to admin
    if m_recipient or CFG_WEBSUBMIT_COPY_MAILS_TO_ADMIN:
        send_email(FROMADDR, m_recipient.strip(), email_subject, email_txt,
                    copy_to_admin=CFG_WEBSUBMIT_COPY_MAILS_TO_ADMIN)

    return ""
