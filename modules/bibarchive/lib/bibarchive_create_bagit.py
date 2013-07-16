# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2011, 2012 CERN.
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

from invenio.flaskshell import *
from invenio.config import CFG_TMPDIR
from invenio.bibdocfile import BibDoc, BibRecDocs
from invenio.bibarchive_config import InvenioBibArchiveError
from invenio.bibrecord import record_xml_output
from invenio.search_engine import get_record
from fs.opener import opener
from fs.osfs import OSFS
from fs.zipfs import ZipFS
from fs.utils import copyfile, copydir
from bagit import make_bag, Bag
import shutil
import os

class Bagit_Handler:
    '''
    Handles all bagit related operations
    '''

    def remove_dir(self, path):
        '''
        Removes a folder at a given path
        '''
        try:
            file_to_delete = os.path.basename(path)
            to_delete_from = OSFS(os.path.dirname(path))
            to_delete_from.removedir(file_to_delete, recursive = True, force = True)
        except ResourceNotFoundError:
            raise InvenioBibArchiveError, "Folder %s not found" % path

    def zip_bagit(self, path):
        '''
        Compresses a bagit file
        '''
        # Removes the final forwardslash if there is one
        if path.endswith('/'):
            path = path[:-1]

        try:
            # Create and FS object
            with OSFS(path) as to_zip_fs:
                with ZipFS("%s.zip" % path, mode = 'w') as zip_fs:
                    copydir(to_zip_fs, zip_fs, overwrite = True)
            self.remove_dir(path)
            return True

        except:
            raise InvenioBibArchiveError, "Zipping of %s failed." % path

    def generate_bagit(self, path):
        '''
        Turns a folder into bagit form and compresses
        '''
        try:
            bag = make_bag(path)

        except RuntimeError:
            raise InvenioBibArchiveError, "No such bag directory %s" % path

    def transfer_data_files(self):
        '''
        Transfers a files in a list from one fs object to another
        maintaining the same filename.
        '''

        try:
            for f in self.docfiles:
                shutil.copy(f.get_path(), os.path.join(self.bagit_folder_path, f.name + f.format))
        except:
            raise InvenioBibArchiveError, "Error while copying %s to %s" \
                    % (f.get_path(), os.path.join(self.bagit_folder_path, f.name + f.format))
        return True

    def tranfer_marc(self):
        xml = record_xml_output(get_record(self.recid))
        file_writer = open("%s/%s.xml" % (self.bagit_folder_path, self.name), mode = 'w')
        file_writer.write(xml)
        file_writer.close()

    def transfer_metadata(self):
        '''
        Copies the metadata of the record to a file called
        meta.txt stored in /data/ of the bagit folder
        '''

        for f in self.docfiles:
            file_writer = open("%s/%s.metadata" % (self.bagit_folder_path, f.name), mode = 'w')
            file_writer.write(str(f))
            file_writer.close()


    def set_up_bag(self, recid, name, docfiles):
        '''
        Creates the folder for the bag (and the bagit folder in tmp
        if it doesn't already exist)
        '''
        self.docfiles = docfiles
        self.name = name
        self.recid = recid
        self.bagit_folder_path = os.path.join(CFG_TMPDIR, "bagit", name)
        os.makedirs(self.bagit_folder_path)
        self.transfer_data_files()
        self.tranfer_marc()
        self.transfer_metadata()

        return self.bagit_folder_path

#------------------------------------------------------------------------------------

class Docfile_Retriever:
    '''
    Handles all Docfile related operations
    '''

    def __init__(self, recid):
        self.recid = recid
        #try:
        bibdocs = BibRecDocs(recid)
        self.docfiles = bibdocs.list_latest_files()
        #except:
        #    raise InvenioBibArchiveError, "Record %d not found." % recid

    def get_file_urls(self):
        '''
        Returns a list of the local URLs for the files found
        '''
        self.filepaths = []
        map(lambda x:self.filepaths.append(x.fullpath), self.docfiles)
        return self.filepaths

    def get_record_name(self):
        '''
        Get the records name so the bagit can take this name rather than
        be named under the recid
        '''
        return "record_" + str(self.recid)

    def get_record_metadata(self):
        return self.docfiles


#--------------------------------------------------------------------------------------


def create_bagit(recid, version=None):
    '''
    Given a recid will create a compressed bagit.
    '''
    
    file_retriever = Docfile_Retriever(recid)
    name = file_retriever.get_record_name()
    if version:
        name = name + "_v" + str(version)
    bag_handler = Bagit_Handler()
    bag_path = bag_handler.set_up_bag(recid, name, file_retriever.docfiles)
    bag_handler.generate_bagit(bag_path)
    bag_handler.zip_bagit(bag_path)

    return "%s.zip" % bag_path
