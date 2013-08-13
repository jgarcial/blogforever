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

"""
Various utilities for WebBlog, e.g. config parser, etc.
"""

from invenio.search_engine_utils import get_fieldvalues
from invenio.websearch_instantbrowse import instantbrowse_manager
from invenio.pluginutils import PluginContainer
import os
import json
import datetime
from invenio.search_engine import perform_request_search,search_pattern, get_fieldvalues
from invenio.websearch_external_collections_utils import get_collection_id
from invenio.config import CFG_PYLIBDIR, CFG_SPIDER_WEBSERVICE_URL, \
                            CFG_SPIDER_API_KEY, CFG_TMPDIR
from invenio.bibtask import task_low_level_submission
from suds.client import Client
import time


# Container of latest additions plugins
instantbrowse_plugins_container = PluginContainer\
    (os.path.join(CFG_PYLIBDIR, 'invenio', 'websearch_instantbrowse_plugins', 'websearch_*.py'))


#####  BLOGS #####

def get_parent_blog(recid):
    """ This function returns the parent blog of any 
    post or comment given its recid
    @param recid: comment or post recid
    @type recid: int
    @return: parent blog recid
    @rtype: int
    """

    coll = get_fieldvalues(recid, '980__a')[0]
    if coll == 'BLOG':
        return recid

    parent_blog = get_fieldvalues(recid, '760__w')

    if parent_blog:
        if parent_blog[0]:
            return int(parent_blog[0])
        else:
            return None
    else:
        return None

def get_blog_descendants(recid):
    """ This function returns all the descendants of the given blog """

    posts = get_posts(recid)
    descendants = posts
    for post_recid in posts:
        comments = get_comments(post_recid)
        descendants += comments

    return descendants

##### POSTS #####

def get_posts(blog_recid):
    """ This function returns the list of posts 
    written on the given blog
    @param blog_recid: blog recid
    @type blog_recid: int
    @return: list of posts recids
    @rtype: list
    """

    collection_id = get_collection_id('Posts')
    argd = {}
    # check which plugins have been set for each collection
    instantbrowse_plugin = instantbrowse_manager.get_instantbrowse_plugin(collection_id)
    if instantbrowse_plugin:
        plugin = instantbrowse_plugins_container.get_plugin(instantbrowse_plugin[0])
        params = instantbrowse_plugin[1]
        # run the corresponding plugin
        if params:
            argd.update(json.loads(params))
    argd['p'] = '760__w:"%s"' % blog_recid
    argd['cc'] = 'Posts'
    return perform_request_search(None, **argd)

def get_parent_post(comment_recid):
    """ This function returns the parent post of any 
    comment given its recid
    @param comment_recid: comment recid
    @type comment_recid: int
    @return: parent post recid
    @rtype: int
    """

    parent_post = get_fieldvalues(comment_recid, '773__w')
    if parent_post:
       if parent_post[0]:
           return int(parent_post[0])
       else:
           return None
    else:
        return None

def get_post_tags(post_recid):
    return get_fieldvalues(post_recid, '653__1')

##### COMMENTS #####

def get_comments(post_recid):
    """ This function returns the list of comments 
    written on the given post
    @param post_recid: post recid
    @type post_recid: int
    @return: list of sibling comments recids
    @rtype: list
    """

    collection_id = get_collection_id('Comments')
    argd = {}
    # check which plugins have been set for each collection
    instantbrowse_plugin = instantbrowse_manager.get_instantbrowse_plugin(collection_id)
    if instantbrowse_plugin:
        plugin = instantbrowse_plugins_container.get_plugin(instantbrowse_plugin[0])
        params = instantbrowse_plugin[1]
        # run the corresponding plugin
        if params:
            argd.update(json.loads(params))
    argd['p'] = '773__w:"%s"' % post_recid
    return perform_request_search(None, **argd)

##### GENERAL FUNCTIONS #####

def transform_format_date(date, format="%Y/%m/%d"):
    """Transforms the given date into the given format"""

    try:
        date_datetime = datetime.datetime.strptime(date, "%m/%d/%Y %I:%M:%S %p")
        formated_date = date_datetime.strftime(format)
    except:
        formated_date = "Unknown date"
    return formated_date

def calculate_path(base_dir, file_name):
    """Given a file name it returns the complete path that should host its files."""
    h = hash(file_name)
    group1 = str(h % 100)
    group2 = str(h % 99)
    return os.path.join(base_dir, group1, group2)

def prepare_path(base_dir, file_name):
    """Prepares the directory serving as root"""
    path = calculate_path(base_dir, file_name)
    # we create the corresponding storage directory
    if not os.path.exists(path):
        old_umask = os.umask(022)
        os.makedirs(path)
        os.umask(old_umask)
    return path


######## FUNCTIONS USED IN REPOSITORY-SPIDER COMMUNICATION ########


def _update_provisional_blog_url(recid, tourl):
    """
    Modify the url of a blog since the one that was submitted
    has been forward by the spider to another one.
    """

    template = """<?xml version="1.0" encoding="UTF-8"?>\n
                    <record>
                        <controlfield tag="001">%(recid)s</controlfield>
                        <datafield tag="520" ind1=" " ind2=" ">
                            <subfield code="u">%(tourl)s</subfield>
                        </datafield>
                    </record>""" % {'recid': recid, 'tourl': tourl}

    file_path = CFG_TMPDIR + '/blog_to_modify_%s.xml' % time.strftime("%Y%m%d_%H%M%S")
    xml_file = open(file_path, 'w')
    xml_file.write(template.encode('utf-8'))
    xml_file.close()
    task_low_level_submission('bibupload', 'webblog', '-c', file_path)


def _delete_provisional_blog(recid):
    """
    Removes a blog from the Provisional Blogs collection.
    """

    template = """<?xml version="1.0" encoding="UTF-8"?>\n
                    <record>
                        <controlfield tag="001">%(recid)s</controlfield>
                        <datafield tag="980" ind1=" " ind2=" ">
                            <subfield code="c">DELETED</subfield>
                        </datafield>
                    </record>""" % {'recid': recid}

    file_path = CFG_TMPDIR + '/blog_to_delete_%s.xml' % time.strftime("%Y%m%d_%H%M%S")
    xml_file = open(file_path, 'w')
    xml_file.write(template.encode('utf-8'))
    xml_file.close()
    task_low_level_submission('bibupload', 'webblog', '-c', file_path)


def send_submitted_blog_urls(urls):
    """
    Let's send a blog URL to the spider to start crawling it.
    """

    try:
        client = Client(CFG_SPIDER_WEBSERVICE_URL)
    except:
        raise Exception("Imposible to connect to the webservice")

    watch_point = client.factory.create('ns7:ArrayOfstring')
    tags = client.factory.create('ns7:ArrayOfstring')
    if isinstance(urls, list):
        watch_point.string.extend(urls)
    else:
        watch_point.string.append(urls)

    try:
        result = client.service.AddWatchPoints(CFG_SPIDER_API_KEY, watch_point, tags)
    except:
        raise Exception("Imposible to add watch point %s" % url)


def check_submitted_blog_urls_status(client):
    """
    Checks which is the status of the submitted blog
    urls in the spider. If the status is "Unknown", "Invalid",
    or "Failed", the corresponding blog will be delelet from the
    Provisional Blogs collections. if the status is "Forward",
    the URL of the corresponding blog will be updated.
    """

    prov_blogs_recids = search_pattern(p="980__a:PROVBLOG")
    if prov_blogs_recids:
        prov_blogs_urls = [get_fieldvalues(prov_blog_recid, "520__u")[0] \
                                for prov_blog_recid in prov_blogs_recids]
        d = dict(zip(prov_blogs_recids, prov_blogs_urls))

        for (recid, url) in d.items():
            # Let's check the status of the submitted urls on the
            # spider side
            result = client.service.GetUriState(CFG_SPIDER_API_KEY, url)
            if result:
                if result.Value in ["Unknown", "Invalid", "Failed"]:
                    _delete_provisional_blog(recid)
                elif result.Value in ["Entity", "Forward"]:
                    if url == result.FromUri and result.FromUri is not result.ToUri:
                        _update_provisional_blog_url(recid, result.ToUri)
                        log_file = open(CFG_TMPDIR + "/log_file", "a")
                        log_file.write("Submitted URL %s forward to %s \n" % (url, result.ToUri))
                        log_file.close()
                    else:
                        raise Exception("The submitted URL and and 'from URI' parameter do not match ")
            else: # the blog is in the PROVISIONAL BLOGS collection but it was never crawled by the spider
                 _delete_provisional_blog(recid)
