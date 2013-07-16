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

import unittest
from invenio.testutils import make_test_suite, \
                              run_test_suite
from invenio.bibarchive_dbapi import Database_Connection, Database_Access
from invenio.bibarchive_create_bagit import Docfile_Retriver, Bagit_Handler
from invenio.bibdocfile import BibDoc
from invenio.config import CFG_BAGIT_PATH
from fs.osfs import OSFS
from fs.zipfs import ZipFS
from invenio.bibarchive_config import InvenioBibArchiveError
from bagit import Bag, BagError

class Test_Server_Connection(unittest.TestCase):

	def test_connection_utils(self):
		self.assertTrue(Database_Connection())

		self.connection = Database_Connection()

		self.assertTrue(self.connection.kill())
		self.assertTrue(self.connection.restart_connection())

class Test_DB_Connection(unittest.TestCase):

	def setUp(self):
		self.connection = Database_Connection()

	def test_db_connection(self):
		try:
			Database_Access(self.connection, "mydb", "mycoll")
		except:
			self.assertTrue(False, "DB Connection Failed")

class Test_DB_Access(unittest.TestCase):

	first = True

	@classmethod
	def setUp(self):

		if self.first:
			self.first = False

			self.connection = Database_Connection()
			self.db_access = Database_Access(self.connection, "mydb", "mycoll")
			self.example_recid = "454847"
			self.example_data = "http://abc123.com/"
			self.example_data_2 = "foo"
			self.example_data_3 = "bar"

	@classmethod
	def tearDown(self):
		self.connection.kill()

	def test_a_db_create(self):
		self.db_access.create(recid=self.example_recid, version="1.0", data=self.example_data)
		self.assertEqual(self.db_access.get(recid=self.example_recid), self.example_data)

	def test_b_db_update(self):
		self.db_access.update(recid=self.example_recid, data=self.example_data_2)
		self.assertEqual(self.db_access.get(recid=self.example_recid), self.example_data_2)

		self.db_access.update(recid=self.example_recid, data=self.example_data_3, version="2.0")
		self.assertEqual(self.db_access.get(recid=self.example_recid), self.example_data_3)

	def test_c_db_remove(self):
		self.db_access.delete(recid=self.example_recid)
		self.assertEqual(self.db_access.get(recid=self.example_recid), False)

#-----------------------------------------------------------------------------------------------

class Test_Docfile_Retriever(unittest.TestCase):

	@classmethod
	def setUp(self):
		self.file_retriver = Docfile_Retriver()
		self.file_retriver.record = BibDoc(1)

	def test_record_selection(self):
		self.first = False
		self.assertEqual(self.file_retriver.record_selection(recid=1), BibDoc(1))

	def test_get_file_urls(self):
		self.assertEqual(self.file_retriver.get_file_urls(), \
			['/opt/invenio/var/data/files/g0/1/file.gif;icon;1',\
			 '/opt/invenio/var/data/files/g0/1/file.jpg;1'])

	def test_get_record_name(self):
		self.assertEqual(self.file_retriver.get_record_name(), '0106015_01')

	def test_get_metadata(self):
		self.assertEqual(self.file_retriver.get_record_metadata(), BibDoc(1).docfiles)

class Test_Bagit_Handler(unittest.TestCase):\

	@classmethod
	def setUp(self):
		self.file_retriver = Docfile_Retriver()
		self.bibdoc = self.file_retriver.record_selection(1)
		self.file_paths = self.file_retriver.get_file_urls()
		self.record_name = self.file_retriver.get_record_name()
		self.src_path =  self.bibdoc.get_base_dir()
		self.file_metadata = self.file_retriver.get_record_metadata()
		self.bag_handler = Bagit_Handler()

		self.bagit_path = "%s/%s" % (CFG_BAGIT_PATH, self.record_name)\

	def test_a_bag_creation(self):
		self.assertEqual(self.bag_handler.set_up_bag(self.record_name, self.file_paths, \
							self.src_path, self.file_metadata), self.bagit_path)

	def test_b_setup_bagit(self):
		self.bag_handler.set_up_bag(self.record_name, self.file_paths, \
							self.src_path, self.file_metadata)
		self.assertTrue(mount_folder_test(self.bagit_path))

	def test_c_generate_bagit(self):
		self.bag_handler.set_up_bag(self.record_name, self.file_paths, \
							self.src_path, self.file_metadata)
		self.bag_handler.generate_bagit(self.bagit_path)
		self.assertEqual(Bag(self.bagit_path).is_valid(), True)

	def test_d_zip_bagit(self):
		self.bag_handler.set_up_bag(self.record_name, self.file_paths, \
							self.src_path, self.file_metadata)
		self.bag_handler.generate_bagit(self.bagit_path)
		self.bag_handler.zip_bagit(self.bagit_path)
		self.assertTrue(mount_zip_test("%s.zip" % self.bagit_path))

		end_test(self.record_name)


def end_test(record_name):
	bagit_folder = OSFS(CFG_BAGIT_PATH)
	bagit_folder.remove('%s.zip' % record_name)


def mount_folder_test(path):
	try:
		OSFS(path)
		return True
	except:
		return False

def mount_zip_test(path):
	try:
		ZipFS(path, mode='r')
		return True
	except:
		return False


#-----------------------------------------------------------------------------------------------

TEST_SUITE = make_test_suite(Test_Server_Connection,
							Test_DB_Connection,
							Test_DB_Access,
							Test_Docfile_Retriever,
							Test_Bagit_Handler)

if __name__ == '__main__':
    run_test_suite(TEST_SUITE, warn_user=False)