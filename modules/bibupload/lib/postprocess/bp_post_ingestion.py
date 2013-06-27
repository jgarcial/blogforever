# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2012, 2013 CERN.
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

import os
from invenio.search_engine import search_pattern
from invenio import bibingest as b
import datetime
from invenio.bibtask import task_update_progress
from lxml import etree
from invenio.bibupload_preprocess import bp_pre_ingestion
from invenio.config import CFG_TMPDIR


path_mets_attachedfiles = bp_pre_ingestion.path_mets_attachedfiles
path_metadata = bp_pre_ingestion.path_metadata


def bp_post_ingestion(file_path):
    """
    Plugin to insert the given document/s in mongoDB
    @param file_path: absolute path of the METS file to post-process
    @type file_path: string
    """

    # build the path of the corresponding METS file
    file_name = os.path.basename(file_path)
    task_update_progress("Started post-processing record %s" % file_name)
    submission_id = file_name[:file_name.find(".xml")]
    # let's build the path where the corresponding METS is stored
    mets_file_path = path_mets_attachedfiles + submission_id + "/" + file_name + "_mets"
    # let's open the mets xml file from the filesystem
    try:
        f = open(mets_file_path, 'r')
        mets_file = f.read()
        f.close()
    except:
        error_file = open(CFG_TMPDIR + "/error_file", "a")
        error_file.write("Could not find the METS file %s" % mets_file_path +"\n")
        error_file.close()

    # let's get the METS file with the enriched MARC embedded (created at pre-ingestion time)
    # let's get the attached files
    # let's create BatIt

    # let's create the xml tree
    xml_tree = etree.XML(mets_file)
    # to define the namespaces
    namespaces = {'mets': 'http://www.loc.gov/mets/', 'marc': 'http://www.loc.gov/marc/'}
    try:
        # let's figure out in which collection we have to store the given document by using xpath
        record_collection = xml_tree.xpath("mets:dmdSec/mets:mdWrap/mets:xmlData/marc:record/marc:datafield[@tag='980']/marc:subfield[@code='a']/text()", \
                                            namespaces=namespaces)[0].strip()
    except:
        error_file = open(CFG_TMPDIR + "/error_file", "a")
        error_file.write("Could not find the METS file %s" % mets_file_path +"\n")
        error_file.close()
        record_collection = "DEFAULT"

    # to get the final XML without the xml declaration header
    final_xml = etree.tostring(xml_tree, pretty_print=True, xml_declaration=True)

    # let's search for the corresponding record_id by submission_id
    try:
        record_id = search_pattern(p = '002__:%s' % submission_id)[0]
    except:
        raise Exception("Record not found in the database")

    # to save the final xml by using bibingest
    if record_collection:
        # let's get the ingestion package instance which corresponds
        # to this collection
        date = datetime.datetime.now()
        ingestion_pack = b.select(record_collection)
        # once we have all we need let's store the document
        # in its corresponding storage instance
        ingestion_pack.store_one(subid=submission_id, recid=record_id, content=final_xml, date=date)
        task_update_progress("Finished post-processing record %s" % file_name)

    # once the original METS file and the attached files have been stored in mongoDB for preservation reasons,
    # let's remove them from the corresponding temporary folders created under /batchupload/files and /batchupload/metadata
    metadata_file_path = file_path
    if os.path.exists(metadata_file_path):
        os.remove(metadata_file_path)
    else:
        error_file = open(CFG_TMPDIR + "/error_file", "a")
        error_file.write("Could not find the file %s" % metadata_file_path +"\n")
        error_file.close()

    files_dir_path = path_mets_attachedfiles + submission_id
    if os.path.exists(files_dir_path):
        file_list = os.listdir(files_dir_path)
        for file_name in file_list:
            os.remove(files_dir_path + "/" + file_name)
        os.rmdir(files_dir_path)
    else:
        error_file = open(CFG_TMPDIR + "/error_file", "a")
        error_file.write("Could not find the directory %s" % files_dir_path +"\n")
        error_file.close()


    return 1
