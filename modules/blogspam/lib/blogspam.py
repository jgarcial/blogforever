## -*- coding: utf-8; -*-
##
## This file is part of Invenio.
## Copyright (C) 2007, 2008, 2010, 2011 CERN.
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

"""
BlogSpam daemon.
Used by the BlogForever project to do spam detection using record URL

Procedure:
    1. BlogSpam iterates over all records
    2. For each record, it checks if metadata element 520 u exists (URL).
        If not the record is skipped because the spam classification is
        performed based on the record URL
    3. If there is a URL, it checks if the metadata element 911 u
        (the spam flag) exists. If True, this item is already classified
        and its skipped.
    3. If the record does not have 911 $u, the spam classifier is checking
        if it is spam and it is saving the outcome in element 911 u

    After the daemon process has been completed, the admin should run
    bibindex and webcol to see the changes in the records

Configuration:
    /opt/invenio/etc/blogspam/blogspam.cfg

Usage:
    sudo -u www-data /opt/invenio/bin/blogspam
"""

__revision__ = "$Id$"

import ConfigParser
from datetime import datetime
import os
from tempfile import mkstemp

from invenio.bibrecord import record_get_field_value
from invenio.bibtask import task_init, write_message, \
    task_low_level_submission
from invenio.config import CFG_ETCDIR, CFG_TMPDIR
from invenio.dbquery import run_sql
from invenio.intbitset import intbitset
from invenio.search_engine import get_record

from blogspam_dns_based import SpamDnsBase


def task_run_core():
    """ Run the spam detection task.
        select all records without a metadata spam flag set
        for each one of them, query services
        save metadata spam flag (True or False)
    """
    config = ConfigParser.ConfigParser()
    filename = CFG_ETCDIR + "/blogspam/blogspam.cfg"
    write_message("Getting configuration from file: %s" % filename)
    try:
        config.readfp(open(filename))
    except StandardError:
        write_message("Cannot find configuration file: %s." % filename)
        raise StandardError
    spamd_host = config.get("blogspam", "CFG_SPAM_DETECTION_HOST")
    spamd = SpamDnsBase(spamd_host)

    res1 = run_sql("SELECT COUNT(*) FROM bibrec")
    total_recids = int(res1[0][0])
    step = int(config.get("blogspam", "CFG_SPAM_ITERATION_STEP"))
    for start in range(0, total_recids, step):
        end = start + step
        sql = "SELECT id FROM bibrec LIMIT %d, %d" % (start, end)
        recids = intbitset(run_sql(sql))
        for cursor, recid in enumerate(recids):
            record = get_record(recid)
            uri = record_get_field_value(record, '520', '', '', 'u')
            if not uri:
                write_message("Record %d does not have a URI, it cannot be classified." % cursor)
                continue

            has_spam_field = record_get_field_value(record, '911', ' ', ' ', 's')
            if has_spam_field:
                write_message("Record %d has URI %s and is already classified as spam=%s" % (cursor, uri, str(has_spam_field)))
                continue

            if spamd.is_spam(uri):
                spam_value = 1
            else:
                spam_value = 0

            write_message("Record %d has URI %s and is classified now as spam=%d" % (cursor, uri, spam_value))

            # create a minimal xml record file with the new spam flag field
            # create a temporary file to write the xml record
            # call to bibupload to upload the changes with
            # option -a since we are adding a new field to an existing record
            #
            # after all updates, you should run bibindex and webcoll in order to
            # see the changes you did
            marcxml_output = """<?xml version="1.0" encoding="UTF-8"?>\n"""
            marcxml_output += """<collection xmlns="http://www.loc.gov/MARC21/slim">
                                <record>
                                <controlfield tag="001">%(recid)d</controlfield>
                                <datafield tag="911" ind1=" " ind2=" ">
                                    <subfield code="s">%(spam_value)d</subfield>
                                </datafield>
                                </record>
                                </collection>""" % {'recid': recid, 'spam_value': spam_value}
            current_date = datetime.now()
            file_path_fd, file_path_name = mkstemp(suffix='.xml',
                                                prefix="record_with_spam_tag_%s" %
                                                current_date.strftime("%Y-%m-%d_%H:%M:%S"),
                                                dir=CFG_TMPDIR)
            os.write(file_path_fd, marcxml_output)
            os.close(file_path_fd)
            task_low_level_submission('bibupload', 'blogspam', '-a', \
                                            file_path_name)

def main():
    """ Main function that constructs the blogspamtask. """
    task_init(authorization_action='blogspam',
            authorization_msg='BlogSpam Task Submission',
            description="""BlogSpam is using the URL of records (blogs, posts)\
                        to identify if they are spam using web based services:\
                        www.spamhaus.org
                        ...""",
            help_specific_usage="""Check etc/blogspam/blogspam.cfg for options""",
            version=__revision__,
            specific_params=("t", ["test"]),
            task_run_fnc=task_run_core)
