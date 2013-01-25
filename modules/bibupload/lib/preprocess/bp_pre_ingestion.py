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

"""BlogForever ingestion post-processing.
   Inserts METS file in mongoDB.
"""

import sys
import os
import time
import fileinput
from invenio.config import CFG_BATCHUPLOADER_DAEMON_DIR, \
                           CFG_PREFIX

def transform_mets_to_marcxml(filename, mets_filename, attachments_dir, submissionID):
    marc_file = open(filename, 'w')
    marc_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    marc_file.write('<collection xmlns="http://www.loc.gov/MARC21/slim">\n')
    marc_file.write('<record>\n')
    ## JG: put submissionID in marc
    marc_file.write(submissionID_tag_template(submissionID))
    in_marc = False
    for line in fileinput.input(mets_filename):
        if line.find("</marc:") > -1:
            if line.find("</marc:record>") == -1:
                marc_file.write(line.replace("<marc:", "<").replace("</marc:", "</")+'\n')
            in_marc = False
        elif line.find("<marc:") > -1 or in_marc:
            if line.find("<marc:record>") == -1:
                marc_file.write(line.replace("<marc:", "<").replace("</marc:", "</")+'\n')
            in_marc = True
    ## JG: add FFT
    marc_file.write(produce_FFT_tags(attachments_dir))
    marc_file.write('</record>\n')
    marc_file.write('</collection>\n')
    marc_file.close()
    return 1

def submissionID_tag_template(submissionID):
    ## JG: assuming 002 is the tag for the submissionID
    out = """<controlfield tag="002">%s</controlfield>\n""" % (submissionID)
    return out

def get_submissionID(file_path):
    filename = os.path.basename(file_path)
    return filename[:filename.find(".xml")]

def FFT_tag_template(filename, attachments_dir):
    ## JG: The path needs to be absolute!
    out = """<datafield tag="FFT" ind1=" " ind2=" ">
                <subfield code="a">%s</subfield>
                <subfield code="t"></subfield>
                <subfield code="d"></subfield>
            </datafield>\n""" % (os.path.join(attachments_dir, filename))
    return out

def produce_FFT_tags(attachments_dir):
    ## JG: Has to check if the files are different copies of the same item
    ## and produce the tags accordingly

    out = ""
    files_list = os.listdir(attachments_dir)
    for attached_file in files_list:
        out += FFT_tag_template(attached_file, attachments_dir)
    return out

def bp_pre_ingestion(file_path):
    """

    @param: file_path
    @type: string
    """

    # attachments_dir = file_path[:-4]
    filename = os.path.basename(file_path)
    submissionID = get_submissionID(file_path)

    daemon_dir = CFG_BATCHUPLOADER_DAEMON_DIR[0] == '/' and CFG_BATCHUPLOADER_DAEMON_DIR \
                 or CFG_PREFIX + '/' + CFG_BATCHUPLOADER_DAEMON_DIR
    attachments_dir = daemon_dir + "/mets/" + submissionID

    ## JG: check md5

    ## JG: move mets to attached files dir
    mets_filename = os.path.join(attachments_dir, filename + '_mets')
    os.rename(file_path, mets_filename)

    ## JG: create marc
    transform_mets_to_marcxml(file_path, mets_filename, attachments_dir, submissionID)

    ## JG: remove style tagsq

    return 1
