# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2007, 2008, 2009, 2010, 2011 CERN.
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
from invenio.config import CFG_PYLIBDIR
from invenio.search_engine import perform_request_search
from invenio.websearch_external_collections_utils import get_collection_id

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

