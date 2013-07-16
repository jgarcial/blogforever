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
BibArchive tasklet.
Used by the BlogForever project to update the archived version
of the modified (or new) records.

Usage:
    ** If no parameters are provided (recids or colls) then the
    BibArchive updater task will check just those records that were modified
    after the last time that the task was run (last_bibarchive_checking_date).
    sudo -u www-data /opt/invenio/bin/bibtasklet -T bst_bibarchive_updater.py
    sudo -u www-data /opt/invenio/bin/bibtasklet -T bst_bibarchive_updater.py -a recids='1,5,70,90-100'
    sudo -u www-data /opt/invenio/bin/bibtasklet -T bst_bibarchive_updater.py -a colls='Posts,Comments'
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
from invenio.bibarchive_archiver import archive_record
from invenio.bibsched_tasklets.bst_spam_detection import get_records_to_check

def get_last_bibarchive_checking_date():
    """
    Gets the last date in which the spam filtering
    task was run (date format= "%Y-%m-%d %H:%M:%S").
    """

    if os.path.isfile(CFG_TMPDIR + "/last_bibarchive_checking_date"):
        f = open(CFG_TMPDIR + "/last_bibarchive_checking_date", "r")
        date = f.read()
        last_bibarchive_checking_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        f.close()
    else:
        last_bibarchive_checking_date = "0000-00-00 00:00:00"

    return last_bibarchive_checking_date


def store_last_bibarchive_checking_date():
    """
    Stores the last date in which the spam filtering
    task was run (date format= "%Y-%m-%d %H:%M:%S").
    """

    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f = open(CFG_TMPDIR + "/last_bibarchive_checking_date", "w")
    f.write(today)
    f.close()


def bst_bibarchive_updater(recids="", colls=""):
    """ Runs the BibArchive updater task.
    @param recids: list of integer numbers (record ids)
    but can also contain intervals (recids='1,2-56,72')
    @param colls: list of collections (colls='Posts,Comments')
    """

    # let's get the set of records to be checked out
    recids_to_check = get_records_to_check(recids, colls, get_last_bibarchive_checking_date())

    if recids_to_check:
        for recid in recids_to_check:
            archive_record(recid)

    if not recids and not colls:
        store_last_bibarchive_checking_date()
