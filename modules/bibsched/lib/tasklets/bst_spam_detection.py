# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013 CERN.
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
BibSpam tasklet.
Used by the BlogForever project to do spam detection using record URL

Configuration:
    /opt/invenio/etc/bibspam/bibspam.cfg

Usage:
    ** If no parameters are provided (recids or colls) then the
    spam detection task will check just those records that were ingested
    after the last time (last_spam_checking_date) the task was run.
    sudo -u www-data /opt/invenio/bin/bibtasklet -T bst_spam_detection.py
    sudo -u www-data /opt/invenio/bin/bibtasklet -T bst_spam_detection.py -a recids='1,5,70,90-100'
    sudo -u www-data /opt/invenio/bin/bibtasklet -T bst_spam_detection.py -a colls='Posts,Comments'
"""

__revision__ = "$Id$"

import ConfigParser
from datetime import datetime
import os
from tempfile import mkstemp
from invenio.bibtask import write_message, task_low_level_submission
from invenio.config import CFG_ETCDIR, CFG_TMPDIR
from invenio.dbquery import run_sql
from invenio.search_engine import get_record, get_fieldvalues, perform_request_search
from invenio.bibspam_dns_based import SpamDnsBase


def create_marcxml_header():
    """
    Creates the MARC xml header
    @return: the marcxml header
    @rtype: string
    """

    marcxml_output = '<?xml version="1.0" encoding="UTF-8"?>\n'
    marcxml_output += '<collection xmlns="http://www.loc.gov/MARC21/slim">'
    return marcxml_output


def create_marcxml_footer(marcxml_output):
    """
    Creates the MARC xml footer.
    @param marcxml_output: the final marcxml output
    @type param: string
    @return: the final marcxml output plus marcxml footer
    @rtype: string
    """

    marcxml_output += '\n</collection>\n'
    return marcxml_output


def load_configuration():
    """
    Returns CFG_SPAM_DETECTION_HOST and
    CFG_SPAM_ITERATION_STEP values.
    """

    config = ConfigParser.ConfigParser()
    filename = CFG_ETCDIR + "/bibspam/bibspam.cfg"
    write_message("Getting configuration from file: %s" % filename)
    try:
        config.readfp(open(filename))
    except StandardError:
        write_message("Cannot find configuration file: %s." % filename)
        raise StandardError

    spamd_host = config.get("bibspam", "CFG_SPAM_DETECTION_HOST")
    set = int(config.get("bibspam", "CFG_SPAM_ITERATION_STEP"))

    return (spamd_host, set)


def get_last_spam_checking_date():
    """
    Gets the last date in which the spam filtering
    task was run (date format= "%Y-%m-%d %H:%M:%S").
    """

    if os.path.isfile(CFG_TMPDIR + "/last_spam_checking_date"):
        f = open(CFG_TMPDIR + "/last_spam_checking_date", "r")
        date = f.read()
        last_spam_checking_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        f.close()
    else:
        last_spam_checking_date = "0000-00-00 00:00:00"

    return last_spam_checking_date


def store_last_spam_checking_date():
    """
    Stores the last date in which the spam filtering
    task was run (date format= "%Y-%m-%d %H:%M:%S").
    """

    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f = open(CFG_TMPDIR + "/last_spam_checking_date", "w")
    f.write(today)
    f.close()


def get_records_to_check(recids, colls):
    """
    Gets the recids of those records to be checked.
    @param recids: list of integer numbers (record ids)
    but can also contain intervals (recids='1,2-56,72')
    @param colls: list of collections (colls='Posts,Comments')
    """

    if not recids and not colls:
        last_spam_checking_date = get_last_spam_checking_date()
        recids_to_check = run_sql("select id from bibrec where creation_date > %s", \
                                  (last_spam_checking_date, ))
    elif recids and colls:
        raise Exception("Please introduce either a list of recids or a list of collections, not both of them")
    elif recids:
        recid_list = []
        cli_recid_list = recids.strip().split(',')
        for recid in cli_recid_list:
            if recid.find('-') > 0:
                rec_range = recid.split('-')
                try:
                    recid_min = int(rec_range[0])
                    recid_max = int(rec_range[1])
                    for rec in range(recid_min, recid_max + 1):
                        recid_list.append(rec)
                except Error, err:
                    write_message("Error: [%s] occured while trying \
                          to parse the recids argument." %err, sys.stderr)
                    return False
            else:
                recid_list.append(int(recid))
        recids_to_check = recid_list
    elif colls:
        cli_coll_list = colls.strip().split(',')
        recids_to_check = perform_request_search(c=cli_coll_list)

    return recids_to_check


def bst_spam_detection(recids="", colls=""):
    """ Runs the spam detection task.
    @param recids: list of integer numbers (record ids)
    but can also contain intervals (recids='1,2-56,72')
    @param colls: list of collections (colls='Posts,Comments')
    """

    # let's get config variables previously set
    (spamd_host, set) = load_configuration()
    # let's get the spam service we will use
    spamd = SpamDnsBase(spamd_host)
    # let's get the set of records to be checked out
    recids_to_check = get_records_to_check(recids, colls)

    if recids_to_check:
        if len(recids_to_check) > set:
            recids = recids_to_check[:set]
        else:
            recids = recids_to_check

        while len(recids_to_check) > 0:
            marcxml_output = create_marcxml_header()
            for recid in recids:
                try:
                    record_url = get_fieldvalues(recid, "520__u")[0]
                    print record_url
                except:
                    write_message("Record %d does not have URL, it cannot be classified." % recid)

                if not spamd.is_spam(record_url):
                    record_spam_xml = """
                    <record>
                        <controlfield tag="001">%(recid)s</controlfield>
                        <datafield tag="911" ind1=" " ind2=" ">
                            <subfield code="s">%(spam_value)s</subfield>
                        </datafield>
                    </record>
                    """ % {'recid': recid, 'spam_value': 'SPAM'}
                    marcxml_output += record_spam_xml

            marcxml_output = create_marcxml_footer(marcxml_output)
            current_date = datetime.now()
            file_path_fd, file_path_name = mkstemp(suffix='.xml',
                                                   prefix="record_with_spam_tag_%s" %
                                                   current_date.strftime("%Y-%m-%d_%H:%M:%S"),
                                                   dir=CFG_TMPDIR)
            os.write(file_path_fd, marcxml_output)
            os.close(file_path_fd)
            task_low_level_submission('bibupload', 'bibspam', '-a', file_path_name)

            recids_to_check = recids_to_check[set:]
            if len(recids_to_check) > set:
                recids = recids_to_check[:set]
            else:
                recids = recids_to_check

    if not recids and not colls:
        store_last_spam_checking_date()
