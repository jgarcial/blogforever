#!/usr/bin/python
from ftplib import FTP
from os import mkdir
from invenio.bibtask import task_low_level_submission


def process_dir(dir_name, delete=False):
	ftp.cwd(dir_name)
	ls = ftp.nlst()
	local_dir = "/opt/invenio/var/batchupload/metadata/replace/"
	for line in ls:
		try:
			mkdir('/opt/invenio/var/batchupload/mets/' + dir_name)
		except:
			pass
		file_name = line.splitlines()[-1]
		file_name = line
		process_file(dir_name, file_name)
		if delete:
			try:
				ftp.delete(file_name)
			except:
				print "ERROR deleting file " + file_name
	ftp.cwd('..')

	task_low_level_submission('bibupload', 'batchupload', '--replace', local_dir+dir_name+'.xml', '--pre-plugin=bp_pre_ingestion', '')

	if delete:
		try:
			ftp.rmd(dir_name)
		except:
			print "ERROR deleting dir " + dir_name


def process_file(dir_name, file_name):
	if dir_name == file_name[:-4]:
		local_dir = "/opt/invenio/var/batchupload/metadata/replace/"
	else:
		local_dir = "/opt/invenio/var/batchupload/mets/" + dir_name
	print ftp.retrlines("RETR %s" % file_name, open(local_dir+file_name, 'w').write) + '\t' + local_dir+file_name


ftp = FTP('ftp.cyberwatcher.com')
ftp.login('bf', 'fRatrE8H')

for sd in ftp.nlst():
	process_dir(sd)

ftp.close()
