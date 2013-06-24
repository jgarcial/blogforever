# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2009, 2010, 2011 CERN.
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

"""BlogForever Tasklet Example.
Demonstrates format migration.
"""

import sys
import time
import os
import datetime
from invenio.bibtask import write_message, task_set_option, \
        task_get_option, task_update_progress, task_has_option, \
        task_get_task_param, task_sleep_now_if_required, \
	task_low_level_submission, get_modified_records_since
from invenio.bibdocfile import BibRecDocs
#from invenio.bibdocfilecli import bibupload_ffts
from tempfile import mkstemp
from invenio.config import CFG_TMPDIR, CFG_PYLIBDIR, \
			   CFG_FORMAT_MIGRATION_PLUGINS_MAPPING

from invenio.pluginutils import PluginContainer
# Container of format migration utiles
format_migration_plugins_container = PluginContainer\
            (os.path.join(CFG_PYLIBDIR, 'invenio', 'format_migration_plugins', '*.py'))

def get_last_date():
    """
    Read from the file format_migration_last_run_date the date of the last 
    time the tasklet run
    """
    file_path = CFG_TMPDIR + '/' + 'format_migration_last_run_date'
    # Let's read the last time the tasklet run
    if os.path.isfile(file_path):
        last_run_date_file = open(file_path, "r")
        if os.path.getsize(file_path) > 0:
            last_run_date = datetime.datetime.strptime(last_run_date_file.read(),"%Y-%m-%d %H:%M:%S")
            last_run_date_file.close()
        # It is the first iteration
        else:
            last_run_date = datetime.datetime.strptime("1900-01-01 00:00:00","%Y-%m-%d %H:%M:%S")
    else: # It is the first iteration
        last_run_date = datetime.datetime.strptime("1900-01-01 00:00:00","%Y-%m-%d %H:%M:%S")

    return last_run_date

def save_last_date(date=datetime.datetime.now()):
    file_path = CFG_TMPDIR + '/' + 'format_migration_last_run_date'
    last_run_date_file = open(file_path, "w")
    last_run_date_file.write(datetime.datetime.strftime(date, "%Y-%m-%d %H:%M:%S"))
    last_run_date_file.close()

def get_record_list():
    """Performs a search and returns the list of recids"""
    recids = get_modified_records_since(get_last_date())
    return recids

def generate_marc_records(results):
    out = """<collection xmlns="http://www.loc.gov/MARC21/slim">"""
    for record in results:
	(recid, migrated) = record
	out += """<record>"""
	out += """<controlfield tag="001">%s</controlfield>""" % recid
	for path in migrated:
	    out += """
	        <datafield tag="FFT" ind1=" " ind2=" ">
	            <subfield code="a">%s</subfield>
	            </subfield>
	        </datafield>
		""" % path

        out += """</record>"""
    out += """</collection>"""
    return out

def bst_format_migration():
    """
    Small tasklet that performs format migration on files
    """
    write_message("Retrieving record list...", verbose=9)
    #write_message("Error: water in the CPU.  Ignoring and continuing.", sys.stderr, verbose=3)
    last_date = datetime.datetime.now()
    recids = get_record_list()
    results = []
    #ffts = {}
    i = 0
    write_message("Converting...", verbose=9)
    for recid in recids:
	brd = BibRecDocs(recid)
	migrated = []
	for file in brd.list_latest_files():
	    img_dest_dir = CFG_TMPDIR + '/' + str(recid)
	    if file.mime in CFG_FORMAT_MIGRATION_PLUGINS_MAPPING.keys():
		if not os.path.exists(img_dest_dir):
		    os.mkdir(img_dest_dir)
		plugin = format_migration_plugins_container.get_plugin(CFG_FORMAT_MIGRATION_PLUGINS_MAPPING[file.mime])
		new_file_path = plugin(file.fullpath, img_dest_dir, file.name, file.mime)
		migrated.append(new_file_path)
	if migrated is not []:
	    #ffts[recid]= [{'url' : new_file_path}]
	    results.append((recid, migrated))		
	i+=1
        task_update_progress("Converted %d out of %d." % (i, len(recids)))
        task_sleep_now_if_required(can_stop_too=True)
    
        
    if results is not []:
	(marc_fd, marc_path) = mkstemp(suffix='.xml', prefix='format_migration', dir=CFG_TMPDIR)
	tmpfile = os.fdopen(marc_fd, 'w')
	tmpfile.write(generate_marc_records(results))
	tmpfile.close()

#    bibupload_ffts(ffts, append=True, interactive=True)
    
    # Double check if the file exists
	if os.path.exists(marc_path):
            task_low_level_submission('bibupload', 'batchupload', '-a', marc_path)
    save_last_date(last_date)
    return 1

