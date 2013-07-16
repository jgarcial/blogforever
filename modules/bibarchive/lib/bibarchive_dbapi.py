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

from invenio.bibarchive_config import InvenioBibArchiveError
from invenio.config import CFG_MONGO_HOST, CFG_MONGO_PORT, \
                            CFG_MONGO_BAGIT_DB_NAME, \
                            CFG_MONGO_BAGIT_DB_COLLECTION_NAME
import pymongo
from pymongo.errors import ConnectionFailure, AutoReconnect
from pymongo import Connection
from datetime import datetime
import bson
import hashlib
import traceback

class Database_Connection:
    '''
    Handles the connection to the mongo server
    '''

    def __init__(self, host=CFG_MONGO_HOST, port=CFG_MONGO_PORT, max_pool_size=10, network_timeout=None, document_class=dict, tz_aware=False, **kwargs):

            try:
                self.connection = Connection(host, port, max_pool_size, network_timeout,document_class,tz_aware, **kwargs)

            except:
                raise InvenioBibArchiveError, "Connection to %s on %s failed!" % (host, port)

    def __str__(self):
        return "%s @ port %s" % (self.connection.HOST, self.connection.PORT)

    def kill(self):
        try:
            self.connection.end_request()
            self.connection.disconnect()

        except:
            raise InvenioBibArchiveError, "Killing of %s connection failed" % str(self)

    def restart_connection(self):
        '''This can also be used to start a killed connection'''
        try:
            self.kill()
            self.__init__()

        except:
            raise InvenioBibArchiveError, "Restarting of %s connection failed" % str(self)


# ------------------------------------------------------------------------------------------------

class Database_Access:
    '''
    Handles querying of the database
    '''

    def __init__(self, connector, db_name=CFG_MONGO_BAGIT_DB_NAME, \
                    collection_name=CFG_MONGO_BAGIT_DB_COLLECTION_NAME):
        '''
        NOTE: Although this creates a database and collection, it must be initialised with a document before
        it can be seen on the server!
        '''
        # try:
        connector.restart_connection()
        self.db = connector.connection[db_name]
        self.collection = self.db[collection_name]

        # except:
        #     raise InvenioBibArchiveError, "Access to collection %s in %s using %s connection failed!" % \
        #                                     (collection_name, db_name, connector)

    def save(self, recid, data):

        version = self.get_latest_version_number(recid)
        recid = str(recid)
        checksum = hashlib.md5(data).hexdigest()
        data = bson.Binary(data)
        try:
            self.collection.save({"recid":recid, "version":str(version+1), "creation_date":str(datetime.now()),\
                                  "data":data, "checksum":str(checksum)})
        except:
            raise InvenioBibArchiveError, "Creation of record %s failed" % recid
            

    def get_all(self, recid):
        '''
        Takes a recid as a param
        Returns a list of {"version":version, "data":data} dictionaries
        '''

        recid=str(recid)

        try:
            results = self.collection.find({"recid":recid},{"version":1, "data":1, "_id":0}).sort("version", pymongo.DESCENDING)
            return [result for result in results]

        except:
            raise InvenioBibArchiveError, "Retrival of record %s failed" % recid

    def get(self, recid):
        '''
        Takes a recid as a param
        Returns a {"version":version, "data":data} dictionary
        '''

        recid=str(recid)
        version = self.get_latest_version_number(recid)
        try:
            result = self.collection.find_one({"recid":recid, "version":str(version)},{"version":1, "data":1, "_id":0})
            return result

        except:
            raise InvenioBibArchiveError, "Retrival of record %s failed" % recid

    def get_latest_version_number(self, recid):
        '''
        Takes a recid as a param
        Returns version field of the latest version
        '''

        recid=str(recid)

        try:
            result = self.collection.find({"recid":recid}, {"version":1, "_id":0}).sort("version", pymongo.DESCENDING).next()
            return int(result['version'])

        except:
            return 0
    
    def update(self, recid, data, version=None):
        '''
        Will update the creation_date, data and checksum columns of the latest stored version
        '''
        
        recid=str(recid)

        # Create the MD5 checksum for the new data
        checksum = hashlib.md5(data).hexdigest()

        if version is None: # Do not try to update the version
            file_found = self.collection.find_and_modify(query={"recid":recid},
                                                        update={"$set": {"creation_date":str(datetime.now()), "data":data, "checksum":checksum}})
        else: # Update the version
            file_found = self.collection.insert({"recid":recid, "creation_date":str(datetime.now()), "data":data, "version":version, "checksum":checksum})

        # If the return from the find_and_modify function is None
        # return false. If a document is found, return true.
        if file_found is None:
            raise InvenioBibArchiveError, "Record %s not found" % recid


    def delete(self, recid):
        '''
        Will delete a specific version of the stored data for a given record.
        '''

        recid=str(recid)
        
        file_found = self.collection.find_one({"recid":recid})

        if file_found is None:
            raise InvenioBibArchiveError, "Record %s not found" % recid

        self.collection.remove({"recid":str(recid)})
        return True


#-------------------------------------------------------------------------------------------------

