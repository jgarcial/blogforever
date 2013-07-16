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
from invenio.mailutils import scheduled_send_email
from invenio.bibtask import bibtask_allocate_sequenceid
from invenio.search_engine import get_fieldvalues
from invenio.bibrecord import create_record, record_get_field_values

def MBI_Mail_Notification_to_User(parameters, curdir, form, user_info=None):
    """
    This function sends an email to the user who modified any metadata of
    a blog record saying that those modifications were correctly received

    Parameters:

      * emailFile: Name of the file containing the email of the user
    """

    global rn, sysno

    FROMADDR = '%s Submission Engine <%s>' % (CFG_SITE_NAME,CFG_SITE_SUPPORT_EMAIL)
    sequence_id = bibtask_allocate_sequenceid(curdir)

    blog_title = "".join(["%s" % title.strip() for title in \
                         get_fieldvalues(int(sysno), "245__a")])

    blog_url = "".join(["%s" % url.strip() for url in \
                         get_fieldvalues(int(sysno), "520__u")])

    # The submitters email address is read from the file specified by 'emailFile'
    try:
        fp = open("%s/%s" % (curdir,parameters['emailFile']),"r")
        m_recipient = fp.read().replace ("\n"," ")
        fp.close()
    except:
        m_recipient = ""

    # create email body
    email_txt = "\nModifications on the blog record with URL [%s] and title '%s' have been correctly received.\n\n" % (blog_url, blog_title)
    # The user is either informed that the document has been added to the database, or sent for approval
    if parameters['status'] == "APPROVAL":
        email_txt =  email_txt + "An email has been sent to the referee. You will be warned by email as soon as the referee takes his/her decision regarding your blog record.\n\n"

    if os.path.exists("%s/recmysql" % curdir):
        fp = open("%s/recmysql" % curdir,"r")
        modifiedrec_xml = fp.read()
        fp.close()
    else:
        raise InvenioWebSubmitFunctionError("Cannot create database record")

    modifiedrec = create_record(modifiedrec_xml)[0]
    new_title = record_get_field_values(modifiedrec, "245", code = "a")
    new_topics = record_get_field_values(modifiedrec, "654", code = "a")
    new_topics = ', '.join(new_topics)
    new_license = record_get_field_values(modifiedrec, "542", code = "f")

    modified_fields = ""
    if new_title:
        modified_fields += "New title: '%s'\n" % new_title[0]
    if new_topics:
        modified_fields += "   New topics: '%s'\n" % new_topics
    if new_license:
        modified_fields += "   New license: '%s'" % new_license[0]

    email_txt += "Here you can see the fields that were modified:\n\n   %(modified_fields)s\n" % {'modified_fields': modified_fields}
    email_txt += "It will be soon accessible here: <%s/%s/%s>\n\n" % (CFG_SITE_URL, CFG_SITE_RECORD, sysno)

    # email_txt += get_nice_bibsched_related_message(curdir)
    email_txt = email_txt + "Thank you for using %s Submission Interface.\n" % CFG_SITE_NAME

    email_subject = "Blog record modifications received: [%(id)s]"

    if blog_title:
        email_subject = email_subject % {'id' : blog_title}
    else:
        email_subject = email_subject % {'id' : blog_url}

    ## send the mail, if there are any recipients or copy to admin
    if m_recipient or CFG_WEBSUBMIT_COPY_MAILS_TO_ADMIN:
        scheduled_send_email(FROMADDR, m_recipient.strip(), email_subject, email_txt,
                             copy_to_admin=CFG_WEBSUBMIT_COPY_MAILS_TO_ADMIN,
                             other_bibtasklet_arguments=['-I', str(sequence_id)])

    return ""
