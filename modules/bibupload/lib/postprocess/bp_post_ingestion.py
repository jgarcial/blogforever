# -*- coding: utf-8 -*-
##
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


"""BlogForever ingestion post-processing.
   Inserts METS file in mongoDB.
"""

import os
from invenio.search_engine import search_pattern
from invenio import bibingest as b
import datetime
from invenio.config import CFG_BATCHUPLOADER_DAEMON_DIR, \
                           CFG_PREFIX
from invenio.bibtask import  write_message, task_update_progress
from lxml import etree

def bp_post_ingestion(file_path):
    """
    Plugin to insert the given document/s in mongoDB
    @param file_path: file path
    @type file_path: string
    """

    file_name = os.path.basename(file_path)
    task_update_progress("Post-processing blog record %s" % file_name)
    submission_id = file_name[:file_name.find(".xml")]
    # Let's build the path where the corresponding METS is stored
    batchupload_dir = CFG_BATCHUPLOADER_DAEMON_DIR[0] == '/' and CFG_BATCHUPLOADER_DAEMON_DIR \
                          or CFG_PREFIX + '/' + CFG_BATCHUPLOADER_DAEMON_DIR
    path_mets_attachedfiles = batchupload_dir + "/mets/"
    file_path = path_mets_attachedfiles + submission_id + "/" + file_name + "_mets"
    # let's search for the corresponding record_id
    try:
        record_id = search_pattern(p = '002__:%s' % submission_id)[0]
    except:
        raise Exception("Record not found in the database")
    # let's open the mets xml file from the filesystem
    f = open(file_path, 'r')
    mets_file = f.read()
    f.close()
    # let's create the xml tree
    xml_tree = etree.XML(mets_file)
    # to define the namespaces
    namespaces = {'mets': 'http://www.loc.gov/mets/', 'marc': 'http://www.loc.gov/marc/'}
    try:
        # let's get in which collection we have to store the given document by using xpath
        record_collection = xml_tree.xpath("mets:dmdSec/mets:mdWrap/mets:xmlData/marc:record/marc:datafield[@tag='980']/marc:subfield[@code='a']/text()", \
                                            namespaces=namespaces)[0].strip()
    except:
        error_file = open("/tmp/error_file", "a")
        error_file.write("METS file not found %s" % file_path +"\n")
        error_file.close()
        record_collection = "DEFAULT"
    # to get the final XML without the xml declaration header
    final_xml = etree.tostring(xml_tree, pretty_print=True, xml_declaration=True)
    # to save the final xml with bibingest
    if record_collection:
        # let's get the ingestion package instance which corresponds
        # to this collection
        date = datetime.datetime.now()
        ingestion_pack = b.select(record_collection)
        # once we have all we need let's store the document
        # in its corresponding storage instance
        ingestion_pack.store_one(subid=submission_id, recid=record_id, content=final_xml, date=date)

    return 1
