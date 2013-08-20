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

from invenio.bibarchive_create_bagit import create_bagit
from invenio.bibarchive_dbapi import Database_Connection, Database_Access
from invenio.bibarchive_config import InvenioBibArchiveError
from invenio.config import CFG_TMPDIR
from fs.osfs import OSFS
import os

def archive_record(recid):
    '''
    Takes recid and version and produced a zipped bagit folder at
    CFG_TMPDIR and stores the address in database hosted at
    CFG_MONGO_HOST on port CFG_MONGO_PORT in database
    CFG_MONGO_BAGIT_DB_NAME, CFG_MONGO_BAGIT_DB_COLLECTION_NAME
    collection.
    '''
    #try:
    connector = Database_Connection()
    db_access = Database_Access(connector)
    version = db_access.get_latest_version_number(recid)
    bagit = create_bagit(recid, version+1)
    data = open(bagit, 'rb').read()
    db_access.save(recid, data)

    #except:
    #     raise InvenioBibArchiveError, "Archiving of record %s failed" % recid

def get_record(recid):
    connector = Database_Connection()
    db_access = Database_Access(connector)
    res = db_access.get(recid)
    if res:
        path = os.path.join(CFG_TMPDIR, "bagit", "record_%d_v%s.zip" % (recid, res['version']))
        f = open(path, 'wb')
        f.write(res['data'])
        f.close()
        return path
    else:
        return None

def delete_archive(recid):
    '''
    CAUTION!
    This will delete both the compressed bagit and the entry in the database
    '''

    try:
        connector = Database_Connection()
        db_access = Database_Access(connector)

        file_url = db_access.get(recid)
        file_url = file_url.split('/')

        file_to_delete = file_url.pop()

        bagit_location_fs = OSFS("/".join(file_url))
        bagit_location_fs.remove(file_to_delete)

        db_access.delete(recid)

    except :
        raise InvenioBibArchiveError, "Deletion of archive under record id %s failed" % recid
