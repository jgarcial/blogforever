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
from invenio.dbquery import run_sql
from invenio.access_control_admin import acc_get_role_users,acc_get_role_id
from invenio.websubmit_config import CFG_WEBSUBMIT_COPY_MAILS_TO_ADMIN
from invenio.mailutils import send_email
from invenio.websubmit_functions.Shared_Functions import ParamFromFile
from invenio.search_engine import get_fieldvalues

CFG_MAIL_BODY = """
A request for the approval of the deletion of a blog record in the %(site_name)s has been
made and requires your attention as a referee.  The details of the blog record are as follows:

   Title: %(title)s
   Blog URL: [%(blog_url)s]

You can see the details of the blog record at the following address:
 <%(site_url)s/record/%(record_id)s>

Please register your decision by following the instructions at the following address:
 <%(site_url)s/submit?doctype=%(doctype)s&indir=approve&access=%(access)s&act=%(approval_action)s&BSI_RN=%(rn)s>
"""

def DBI_Mail_Approval_Request_to_Referee(parameters, curdir, form, user_info=None):
    """
    This function sends an email to the referee in order to start the
    approval process related to the deletion of a blog record.

    Parameters:

       * addressesDAM: email addresses of the people who will receive
                       this email (comma separated list). this
                       parameter may contain the <CATEG> string. In
                       which case the variable computed from the
                       [categformatDAM] parameter replaces this
                       string.
                       eg.:"<CATEG>-email@cern.ch"

       * categformatDAM: contains a regular expression used to compute
                         the category of the document given the
                         reference of the document.

                         eg.: if [categformatAFP]="TEST-<CATEG>-.*"
                         and the reference of the document is
                         "TEST-CATEGORY1-2001-001", then the computed
                         category equals "CATEGORY1"

       * directory: parameter used to create the URL to access the
                    files.
    """

    global rn, sysno
    doctype = 'BSIREF'
    approval_action = 'APP'
    action = ParamFromFile("%s/%s" % (curdir,'act')).strip()
    otheraddresses = parameters['addressesDAM']
    categformat = parameters['categformatDAM']
    # retrieve category
    categformat = categformat.replace("<CATEG>","([^-]*)")
    m_categ_search = re.match(categformat, rn)
    if m_categ_search is not None:
        if len(m_categ_search.groups()) > 0:
            ## Found a match for the category of this document. Get it:
            category = m_categ_search.group(1)
        else:
            ## This document has no category.
            category = "unknown"
    else:
        category = "unknown"

    blog_title = "".join(["%s" % title.strip() for title in \
                         get_fieldvalues(int(sysno), "245__a")])
    blog_url = "".join(["%s" % url.strip() for url in \
                         get_fieldvalues(int(sysno), "520__u")])

    # we get the referee password
    sth = run_sql("SELECT access FROM sbmAPPROVAL WHERE rn=%s", (rn,))
    if len(sth) >0:
        access = sth[0][0]

    # Build referee's email address
    refereeaddress = ""
    # Try to retrieve the referee's email from the referee's database
    for user in acc_get_role_users(acc_get_role_id("referee_%s_%s" % (doctype,category))):
        refereeaddress += user[1] + ","
    # And if there are general referees
    for user in acc_get_role_users(acc_get_role_id("referee_%s_*" % doctype)):
        refereeaddress += user[1] + ","

    refereeaddress = re.sub(",$","",refereeaddress)
    # Creation of the e-mail for the referee
    addresses = ""
    if refereeaddress != "":
        addresses = refereeaddress + ","
    if otheraddresses != "":
        addresses += otheraddresses
    else:
        addresses = re.sub(",$","",addresses)

    # Send the email:
    mail_subject = "Request for blog deletion approval : [%(id)s]"
    if blog_title:
        mail_subject = mail_subject % {'id': blog_title}
    else:
        mail_subject = mail_subject % {'id': blog_url}

    mail_body = CFG_MAIL_BODY % \
                {'title': blog_title,
                 'blog_url': blog_url,
                 'record_id': sysno,
                 'site_name' : CFG_SITE_NAME,
                 'site_url': CFG_SITE_URL,
                 'doctype': doctype,
                 'access': access,
                 'approval_action': approval_action,
                 'rn': rn
                 }
    send_email(CFG_SITE_SUPPORT_EMAIL, addresses,
               mail_subject, mail_body, copy_to_admin=CFG_WEBSUBMIT_COPY_MAILS_TO_ADMIN)
    return ""
