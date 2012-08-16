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

def SBI_Mail_Notification_to_User(parameters, curdir, form, user_info=None):
    """
    This function sends an email to the user who submitted a new blog record
    saying that it was correctly received

    Parameters:

      * titleFile: Name of the file containing the title of the
                   blog record

      * emailFile: Name of the file containing the email of the user

      * status: Depending on the value of this parameter, the function
                adds an additional text to the email.  This parameter
                can be one of: ADDED: The file has been integrated in
                the database.  APPROVAL: The file has been sent for
                approval to a referee.  or can stay empty.

      * edsrn: Name of the file containing the reference of the
               blog record

    """

    global rn
    FROMADDR = '%s Submission Engine <%s>' % (CFG_SITE_NAME,CFG_SITE_SUPPORT_EMAIL)
    sequence_id = bibtask_allocate_sequenceid(curdir)

    # The title is read from the file specified by 'titlefile'
    try:
        fp = open("%s/%s" % (curdir,parameters['titleFile']),"r")
        blog_title = fp.read().replace("\n"," ")
        fp.close()
    except:
        blog_title = "-"

    # The submitters email address is read from the file specified by 'emailFile'
    try:
        fp = open("%s/%s" % (curdir,parameters['emailFile']),"r")
        m_recipient = fp.read().replace ("\n"," ")
        fp.close()
    except:
        m_recipient = ""

    try:
        fp = open("%s/BSI_URL" % curdir,"r")
        blog_url = fp.read().replace ("\n"," ")
        fp.close()
    except:
        blog_url = ""

    try:
        fp = open("%s/BSI_LICENSE" % curdir,"r")
        blog_license = fp.read().replace ("\n"," ")
        fp.close()
    except:
        blog_license = ""

    try:
        fp = open("%s/BSI_TOPIC" % curdir,"r")
        blog_topic = fp.read().replace ("\n"," ")
        fp.close()
    except:
        blog_topic = ""

    # create email body
    email_txt = "\nThe blog record with reference number [%s] has been correctly received.\n" % rn
    email_txt += """The details of the blog record are as follows:\n
       Title: '%s'
       Blog URL: [%s]
       Topic: %s
       License: %s
       \n""" % (blog_title, blog_url, blog_topic, blog_license)
    # The user is either informed that the document has been added to the database, or sent for approval
    if parameters['status'] == "APPROVAL":
        email_txt =  email_txt + "An email has been sent to the referee. You will be warned by email as soon as the referee takes his/her decision \nregarding your blog record.\n"
    elif parameters['status'] == "ADDED":
        email_txt = email_txt + """It will be soon added to the repository.\n\nOnce inserted, it will be available at this URL: <%s/%s/%s>\n\
If you detect an error please let us know by sending an email to %s.\n\n """ % (CFG_SITE_URL,CFG_SITE_RECORD,sysno,CFG_SITE_SUPPORT_EMAIL)
    #email_txt += get_nice_bibsched_related_message(curdir)
    email_txt = email_txt + "Thank you for using %s Submission Interface.\n" % CFG_SITE_NAME

    ## send the mail, if there are any recipients or copy to admin
    if m_recipient or CFG_WEBSUBMIT_COPY_MAILS_TO_ADMIN:
        scheduled_send_email(FROMADDR, m_recipient.strip(), "Blog received: [%s]" % rn, email_txt,
                             copy_to_admin=CFG_WEBSUBMIT_COPY_MAILS_TO_ADMIN,
                             other_bibtasklet_arguments=['-I', str(sequence_id)])

    return ""

