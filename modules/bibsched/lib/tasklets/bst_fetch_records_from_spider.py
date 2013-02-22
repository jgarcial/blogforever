#!/usr/bin/python
from invenio.flaskshell import db
from suds.client import Client
from base64 import decodestring
from hashlib import md5
import os
import time
import sys
from invenio.config import CFG_BATCHUPLOADER_DAEMON_DIR, \
                           CFG_PREFIX
from invenio.bibtask import task_low_level_submission, write_message, task_update_progress


# Parameters CS 1, 2
# url = 'http://bf.cyberwatcher.com/System3/SpiderService.svc?wsdl'
# api_key = "0GTCnOVdR2sF8hwo/wWr/lsUxKYHogdX2OzlV1PTHBU="

# Parameters CS 3
# url = 'http://bf.cyberwatcher.com/System3/SpiderService.svc?wsdl'
# api_key = 'nJ/QRIBl6GsPXZyLfEndQvjyMgIHtO/gE0/CoFt13sw='

# Parameters CS 4
# url='http://bf4.itc.auth.gr/Spider/SpiderService.svc?wsdl'
# Instance 1
# api_key = 'YeNN9sP3ww+QEOpyz2pz2liyixkzaplAM/dhky72OGI='
# Instance 2
# api_key = 'nXkTqQdj/o2d2BL2r+ZEAg7vgtXhRZqB4UhpkiXWxiE='
# Instance 3
# api_key = 'WdQJ5CppFpA0n7cBDV8QNILBwrb4mINQ5nY4viofrUI='
# Instance 4
# api_key = '0I72nbVFdrDbclOX83/WJe1WLu6cHLb6LF2Rb7FEY0c='

# Parameters CS 5
# url='http://bf4.itc.auth.gr/Spider/SpiderService.svc?wsdl'
# api_key='nXkTqQdj/o2d2BL2r+ZEAg7vgtXhRZqB4UhpkiXWxiE='

batchupload_dir = CFG_BATCHUPLOADER_DAEMON_DIR[0] == '/' and CFG_BATCHUPLOADER_DAEMON_DIR \
                          or CFG_PREFIX + '/' + CFG_BATCHUPLOADER_DAEMON_DIR
path_mets_attachedfiles = batchupload_dir + "/mets/"
path_metadata = batchupload_dir + "/metadata/replace/"


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
    metadata = client.service.GetDocumentAsMets(api_key, match.Object.Id)
    metadata_file_name = match.Object.Type + "_" + time.strftime("%Y-%m-%d_%H:%M:%S")
    if validate_content(content=metadata.MetsXml.encode('utf-8'), md5_hash=metadata.MD5):
        task_update_progress("Uploading blog record %s" % metadata_file_name)
        path_metadata_file = path_metadata + metadata_file_name + '.xml'
        f = open(path_metadata_file, "w")
        f.write(metadata.MetsXml.encode('utf-8'))
        f.close()
        # Let's create a subdirectory for each document fetched
        # to store in it all the files, images... within the METS
        # document
        path_mets_attachedfiles_doc = path_mets_attachedfiles + "/" + metadata_file_name + "/"
        if not os.path.isdir(path_mets_attachedfiles_doc):
            os.mkdir(path_mets_attachedfiles_doc)

        # Let's store the files/attachments of the corresponding match
        docstorage = client.service.GetDocumentStorage(api_key, match.Object.DocumentId)
        try:
            for file in docstorage.FileInfos.StorageFileInfo:
                attach = client.service.GetDocument(api_key, match.Object.DocumentId, file.Filename)
                if validate_content(content=decodestring(attach), md5_hash=file.MD5):
                    f = open(path_mets_attachedfiles_doc + \
                                time.strftime("%Y-%m-%d_%H:%M:%S") + "_" + file.Filename, 'w')
                    f.write(decodestring(attach))
                    f.close()
                else:
                    error_file = open("/tmp/error_file", "a")
                    error_file.write("Attached file %s validation failed in %s \n" % (file.Filename, metadata_file_name))
                    error_file.close()
        except Exception, e:
            error_file = open("/tmp/error_file", "a")
            error_file.write("SubmissionID: " + \
                                str(match.Object.Id) + "\tFailed to retrieve attached files\n")
            error_file.close()

#        sys.stdout.write("\r"+str(match.Object.Id))
#        time.sleep(0.01)
#        sys.stdout.flush()

        # Let's save the last record id it was retrieved
        last_id_file = open("/tmp/last_id", "w")
        last_id_file.write(repr(match.Object.Id))
        last_id_file.close()
        task_low_level_submission('bibupload', 'batchupload', '-r', \
                                    path_metadata_file, '--pre-plugin=bp_pre_ingestion', '--post-plugin=bp_post_ingestion')
        write_message("Uploaded blog record %s " % metadata_file_name)
    else:
        error_file = open("/tmp/error_file", "a")
        error_file.write("METS validation failed in %s \n" % metadata_file_name)
        error_file.close()
        # write down this url to fetch this record again


def connect_to_webservice(url, api_key):
    """
    Creates client to connect to the CW webservice
    @param url: WSDL url
    @param api_key: 
    """

    try:
        client = Client(url)
    except:
        raise "Imposible to connect to the webservice"
    return client


def create_error_file():
    """
    Create an error logging file
    """

    error_file = open("/tmp/error_file", "a")
    error_file.write("----- Start error file -----\n")
    error_file.close()


def create_metadata_dirs(path_mets_attachedfiles, path_metadata):
    """
    Create the two directories used to store all the METS files and 
    the attached files
    """

    # In this directory will be created a subdirectory for each document
    # fetched storing in it all the files, images... within the METS
    # document
    if not os.path.isdir(path_mets_attachedfiles):
        os.mkdir(path_mets_attachedfiles)
    # In this directory will be stored all the METS documents as
    # .xml files. Once the pre-ingestion is done, in this directory
    # will be stored the MARC extracted from those mets files during
    # the pre-ingestion process
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
    if os.path.isfile("/tmp/last_id"):
        last_id_file = open("/tmp/last_id", "r")
        if os.path.getsize("/tmp/last_id") > 0:
            last_id = int(last_id_file.read()) + 1
            last_id_file.close()
        # It is the first iteration
        else:
            last_id = 0
    else: # It is the first iteration
        last_id = 0
    
    return last_id


def bst_fetch_records_from_spider(api_key, url):
    """
    Bibtasklet responsible of the communication spider-repository: 
    the goal is to fetch all records crawled
    by the spider and to store them into the repository
    """

    client = connect_to_webservice(url, api_key)
    create_error_file()
    create_metadata_dirs(path_mets_attachedfiles, path_metadata)
    last_id = get_last_id()
    # Set limits to get the total of results to retrieved
    id_start = last_id
    id_max = sys.maxint
    sr = create_search_request(client, page_size = 1, page_number = 0, \
                                query = "Type:(Post OR Comment OR Blog) AND Id:["+str(id_start)\
                                +" TO "+str(id_max)+"]")
    # Let's get the total number of records to fetch
    result = client.service.SearchEntities(api_key, sr)
    total_records = result.HitTotal
    constant_set = 10
    if total_records <= constant_set:
        id_max = last_id + total_records
        constant_set = total_records
    else:
        id_max = last_id + constant_set
    
    # Let's fetch all records/documents from the spider in
    # small groups of constant_set records
    while total_records > 0:
        task_update_progress("Fetching blog records from %s to %s" % (id_start, id_max))
        blogs = []
        posts = []
        comments = []
        final_matches = []
        sr.Query = "Type:(Post OR Comment OR Blog) AND Id:["+str(id_start)+" TO "+str(id_max)+"]"
        for i in range(constant_set):
            try:
#                sys.stdout.write("\r"+str(sr.PageNumber))
#                time.sleep(0.01)
#                sys.stdout.flush()
                result = client.service.SearchEntities(api_key, sr)
                matches = result.Matches.BlogSearchMatch
            except Exception, e: # no more results found on page sr.PageNumber
                error_file = open("/tmp/error_file", "a")
                error_file.write("Page Number %s" % sr.PageNumber + ": " + str(e)+"\n")
                error_file.close()
            # Let's go to the next page
            sr.PageNumber = sr.PageNumber + 1
            final_matches.extend([match for match in matches])
    
        task_update_progress("Start processing blog records from %s to %s" % (id_start, id_max))
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
                process_record(client, api_key, blog)
                total_records -= 1
            task_update_progress("Running bibindex and webcoll for BLOGS")
            task_low_level_submission('bibindex', 'admin')
            task_low_level_submission('webcoll', 'admin')
        task_update_progress("BLOGS done")
    
        if posts:
            for post in posts:
                process_record(client, api_key, post)
                total_records -= 1
            task_update_progress("Running bibindex and webcoll for POSTS")
            task_low_level_submission('bibindex', 'admin')
            task_low_level_submission('webcoll', 'admin')
        task_update_progress("POSTS done")

        if comments:
            for comment in comments:
                process_record(client, api_key, comment)
                total_records -= 1
            task_update_progress("Running bibindex and webcoll for COMMENTS")
            task_low_level_submission('bibindex', 'admin')
            task_low_level_submission('webcoll', 'admin')
        task_update_progress("COMMENTS done")
    
        # Set new limits to get the next group of records
        id_start = id_max + 1
        id_max = id_start + constant_set
        sr.PageNumber = 0 

    task_update_progress("Finish fetching blog records")

