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

from suds.client import Client
from base64 import decodestring
from hashlib import md5
import os
import time
import tempfile
import sys
from invenio.bibtask import task_low_level_submission, task_update_progress
from invenio.bibupload_preprocess import bp_pre_ingestion
from invenio.config import CFG_TMPDIR, CFG_SPIDER_API_KEY, CFG_SPIDER_WEBSERVICE_URL
from invenio.webblog_utils import prepare_path, check_submitted_blog_urls_status
from invenio.dbquery import run_sql


batchupload_dir = bp_pre_ingestion.batchupload_dir
path_mets_attachedfiles = bp_pre_ingestion.path_mets_attachedfiles
path_metadata = bp_pre_ingestion.path_metadata


def validate_content(content, md5_hash):
    """
    Validates the retrieved content by checking its md5 hash
    """

    content_md5_hash = md5(content).hexdigest()
    return content_md5_hash == md5_hash


def process_record(client, api_key, match):
    """
    This function stores the METS file of the record in the right directory
    and then, gets its attached files and stores them. Once this is done,
    we call to bibupload in order to bring this record to the repository
    """

    # Let's store the METS of the corresponding match
    try:
        metadata = client.service.GetDocumentAsMets(api_key, match.Object.Id)
    except Exception:
        log_file = open("/tmp/log_file", "a")
        log_file.write("Error fetching METS document for %s, %s \n" % \
                         (match.Object.Id, match.Object.WatchPointId))
        log_file.close()
        return
    if validate_content(content=metadata.MetsXml.encode('utf-8'), md5_hash=metadata.MD5):
        prefix = match.Object.Type + "_" + time.strftime("%Y-%m-%d_%H:%M:%S")
        basedir = prepare_path(path_metadata, prefix)
        fd, path_metadata_file = tempfile.mkstemp(suffix=".xml", \
                                                  prefix= prefix, \
                                                  dir=basedir)
        metadata_file = os.path.basename(path_metadata_file)
        metadata_file_name, extension = os.path.splitext(metadata_file)
        task_update_progress("Preparing record %s to upload" % metadata_file_name)
        os.write(fd, metadata.MetsXml.encode('utf-8'))
        os.close(fd)
        # Let's create a subdirectory for each document fetched
        # to store in it all the files, images... within the METS
        # document

        ### path_mets_attachedfiles_doc = path_mets_attachedfiles + metadata_file_name + "/"
	path_mets_attachedfiles_doc = os.path.join(prepare_path(path_mets_attachedfiles, prefix),metadata_file_name)
        if not os.path.isdir(path_mets_attachedfiles_doc):
            os.mkdir(path_mets_attachedfiles_doc)

        # Let's store the files/attachments of the corresponding match
        try:
            docstorage = client.service.GetDocumentStorage(api_key, match.Object.DocumentId)
        except Exception:
            log_file = open(CFG_TMPDIR + "/log_file", "a")
            log_file.write("There are not attached files for %s, %s \n" % \
                             (metadata_file_name, match.Object.WatchPointId))
            log_file.close()

        if docstorage:
            for file in docstorage.FileInfos.StorageFileInfo:
                try:
                    attach = client.service.GetDocument(api_key, match.Object.DocumentId, file.Filename)
                    if validate_content(content=decodestring(attach), md5_hash=file.MD5):
                        f = open(os.path.join(path_mets_attachedfiles_doc, file.Type + "_" + file.Filename), 'w')
                        f.write(decodestring(attach))
                        f.close()
                    else:
                        log_file = open(CFG_TMPDIR + "/log_file", "a")
                        log_file.write("Attached file %s validation failed in %s \n" % \
                                         (file.Type + "_" + file.Filename, metadata_file_name))
                        log_file.close()
                except Exception:
                    log_file = open(CFG_TMPDIR + "/log_file", "a")
                    log_file.write("Fail retrieving attached files for %s, %s \n" % \
                                     (metadata_file_name, match.Object.WatchPointId))
                    log_file.close()

        # Let's save the last record id it was retrieved
        last_id_file = open(CFG_TMPDIR + "/last_id", "w")
        last_id_file.write(repr(match.Object.Id))
        last_id_file.close()

        # Let's stop the fetcher for a while in order
        # to clear the bibsched queue
        query = 'SELECT COUNT(*) FROM schTASK WHERE STATUS="WAITING"'
        queue_size = run_sql(query)[0][0]
        while queue_size > 1000:
            time.sleep(20)
            queue_size = run_sql(query)[0][0]

        # Double check if the file exists
        if os.path.exists(path_metadata_file):
            task_low_level_submission('bibupload', 'batchupload', '-c', \
                                      path_metadata_file, \
                                      '--pre-plugin=bp_pre_ingestion', \
                                      '--post-plugin=bp_post_ingestion')
        else:
            log_file = open(CFG_TMPDIR + "/log_file", "a")
            log_file.write("No such as file %s \n" % metadata_file_name)
            log_file.close()
    else:
        # TODO: write down this url to fetch this record again
        log_file = open(CFG_TMPDIR + "/log_file", "a")
        log_file.write("METS validation failed in %s, %s \n" % metadata_file_name, match.Object.WatchPointId)
        log_file.close()


def connect_to_webservice(url):
    """
    Creates client to connect to the CW webservice
    @param url: WSDL url
    """

    try:
        client = Client(url)
    except:
        raise Exception("Imposible to connect to the webservice")
    return client


def create_log_file():
    """
    Create an error logging file
    """

    log_file = open(CFG_TMPDIR + "/log_file", "a")
    log_file.write("----- Start error file -----\n")
    log_file.close()


def create_metadata_dirs():
    """
    Create the two directories used to store all the METS files and 
    the attached files, as well as the batchupload subdirectory
    """

    # Let's create batchupload subdirectory (/opt/invenio/var/batchupload)
    if not os.path.isdir(batchupload_dir):
        os.mkdir(batchupload_dir)
    # In this directory will be created a subdirectory for each document
    # fetched storing in it all the files, images... within the METS
    # document (/opt/invenio/var/batchupload/mets)
    if not os.path.isdir(path_mets_attachedfiles):
        os.mkdir(path_mets_attachedfiles)
    # In this directory will be stored all the METS documents as
    # .xml files. Once the pre-ingestion is done, in this directory
    # will be stored the MARC extracted from those mets files during
    # the pre-ingestion process (/opt/invenio/var/batchupload/metadata/replace)
    if not os.path.isdir(path_metadata):
        os.makedirs(path_metadata)


def create_sort_order(client):
    """
    Create sort order parameter used by the search request
    """

    # set SortOrderTypes
    sot = client.factory.create('ns4:SortOrderTypes')
    # set SortTypes
    st = client.factory.create('ns4:SortTypes')
    # set Sort
    so = client.factory.create('ns4:Sort')
    so.Field = "Id"
    so.SortType = st.Field
    so.OrderBy = sot.Ascending

    return so


def create_search_request(client, page_size, page_number, query):
    """
    Create a new search request
    """

    sr = client.factory.create('ns4:SearchRequest')
    sr.SortOrder = create_sort_order(client)
    sr.PageSize = page_size
    sr.PageNumber = page_number
    sr.Query = query

    return sr


def get_last_id():
    """
    Read from the file last_id the id of the last 
    record that was gathered
    """

    # Let's read the last id that was fetched
    if os.path.isfile(CFG_TMPDIR + "/last_id"):
        last_id_file = open(CFG_TMPDIR + "/last_id", "r")
        if os.path.getsize(CFG_TMPDIR + "/last_id") > 0:
            last_id = int(last_id_file.read()) + 1
            last_id_file.close()
        # It is the first iteration
        else:
            last_id = 0
    else: # It is the first iteration
        last_id = 0

    return last_id


def get_total_nb_records(client, api_key, sr):
    """
    Get the total number of records to fetch
    """

    try:
        result = client.service.SearchEntities(api_key, sr)
    except Exception: # no more results were found
        raise Exception ("Server raised fault: 'The server was unable to process the request due to an internal error")

    return result.HitTotal


def bst_fetch_records_from_spider(api_key=CFG_SPIDER_API_KEY, url=CFG_SPIDER_WEBSERVICE_URL,\
                                  constant_set=100, id_max=2147483647):
    """
    Bibtasklet responsible of the communication spider-repository: 
    the goal is to fetch all records crawled
    by the spider and to store them into the repository
    @param api_key: unique api key to access to the web service
    @param url: web service url
    @param constant_set: records are fetched in groups
    of "constant_set" records
    @param id_max: maximum int value
    """

    client = connect_to_webservice(url)
    create_log_file()

    # Let's check which is the status of the URLs that
    # have been submitted and clean up the PROVISIONAL BLOGS
    # collection as needed
    task_update_progress("Start checking submitted urls status")
    check_submitted_blog_urls_status(client)
    task_update_progress("Finished checking submitted urls status")

    create_metadata_dirs()
    last_id = get_last_id()
    # Set limits to get the total of results to retrieve
    id_start = last_id
    sr = create_search_request(client, page_size = 1, page_number = 0, \
                                query = "Type:(Post OR Comment OR Blog) AND Id:["+str(id_start)\
                                +" TO "+str(id_max)+"]")
    total_records = get_total_nb_records(client, api_key, sr)

    if total_records <= int(constant_set):
        id_max = last_id + total_records
        constant_set = total_records
    else:
        id_max = last_id + int(constant_set)

    # Let's fetch all records/documents from the spider in
    # small groups of constant_set records
    while total_records > 0:
        task_update_progress("Fetching blog records from %s to %s" % (id_start, id_max))
        blogs = []
        posts = []
        comments = []
        final_matches = []
        sr.Query = "Type:(Post OR Comment OR Blog) AND Id:["+str(id_start) +" TO "+str(id_max)+"]"
        for i in range(int(constant_set)+1):
            try:
                result = client.service.SearchEntities(api_key, sr)
                matches = result.Matches.BlogSearchMatch
            except Exception: # no more results were found
                log_file = open(CFG_TMPDIR + "/log_file", "a")
                log_file.write("No more results were found \n")
                log_file.close()
                break
            # Let's go to the next page
            sr.PageNumber = sr.PageNumber + 1
            final_matches.extend([match for match in matches])

        task_update_progress("Start processing blog records from %s to %s" % (id_start, id_max))

        if final_matches:
            for match in final_matches:
                if match.Object.Type == 'Blog':
                    blogs.append(match)
                elif match.Object.Type == 'Post':
                    posts.append(match)
                elif match.Object.Type == 'Comment':
                    comments.append(match)
                else:
                    raise Exception("Invalid record type")

        if blogs:
            for blog in blogs:
                total_records -= 1
                process_record(client, api_key, blog)

        if posts:
            for post in posts:
                total_records -= 1
                process_record(client, api_key, post)

        if comments:
            for comment in comments:
                total_records -= 1
                process_record(client, api_key, comment)

        # Set new limits to get the next group of records
        id_start = id_max + 1
        id_max = id_start + int(constant_set)
        sr.PageNumber = 0

        if final_matches:
            task_low_level_submission('bibindex', 'admin')
            task_low_level_submission('webcoll', 'admin', '-p1')

    task_update_progress("Finish fetching blog records")
    last_id_file = open(CFG_TMPDIR + "/last_id", "r")
    last_id = int(last_id_file.read())
    last_id_file.close()
    log_file = open(CFG_TMPDIR + "/log_file", "a")
    log_file.write("Finished fetching blog records. The last blog record retrieved was %s \n" % last_id)
    log_file.close()
