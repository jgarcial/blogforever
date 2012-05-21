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

import time
import datetime
import calendar
import re
import os
import cPickle
import math
import urllib
from MySQLdb import OperationalError
from xml.dom import minidom
from urlparse import urlparse

from invenio.config import \
     CFG_ETCDIR, \
     CFG_SITE_URL, \
     CFG_CACHEDIR, \
     CFG_SITE_LANG, \
     CFG_ACCESS_CONTROL_LEVEL_SITE, \
     CFG_SITE_SUPPORT_EMAIL, \
     CFG_DEVEL_SITE
from invenio.dbquery import run_sql
from invenio.bibformat_engine import BibFormatObject
from invenio.search_engine import search_pattern, \
                                  record_exists, \
                                  perform_request_search
from invenio.search_engine_utils import get_fieldvalues
from invenio.messages import gettext_set_language
from invenio.errorlib import register_exception


############################# POSTS RELATED ##########################

def get_parent_blog(recid):
    if get_fieldvalues(recid,'980__a')[0] == 'BLOG':
        return recid
    parent_blog_recid = get_fieldvalues(recid, '760__w')
    if len(parent_blog_recid)>0:
        parent_blog_recid = parent_blog_recid[0]
    else:
        parent_blog_recid = None
    return parent_blog_recid

def get_posts(blog_recid, newest_first=True):
    return perform_request_search(p='760__w:"%s"' % blog_recid, sf='date', so='d')

def get_comments(post_recid, newest_first=True):
    pass

def get_parent_post(comment_recid):
    pass

def get_sibling_posts(post_recid, newest_first=True, exclude_this_post=True):
    main_blog_recid = get_parent_blog(recid)
    siblings_list = get_posts(main_blog_recid, newest_first)
    if exclude_this_post:
        siblings_list.remove(post_recid)
    return siblings_list

def get_sibling_comments(comment_recid, newest_first=True, exclude_this_comment=True):
    post_recid = get_parent_post(comment_recid)
    siblings_list = get_comments(post_recid, newest_first)
    if exclude_this_comment:
        siblings_list.remove(comment_recid)
    return siblings_list

def get_next_post(post_recid):
    next_post_recid = None
    main_blog_recid = get_parent_blog(post_recid)
    post_date = get_fieldvalues(post_recid, '269__c')
    if len(post_date) > 0:
        post_date = post_date[0]
        recid_list = perform_request_search(p='760__w:"%s" 269__c:%s-->9999-99-99' % (main_blog_recid, post_date), sf='date', so='d')
        if len(recid_list) > 0:
            next_post_recid = recid_list[0]
    return next_post_recid


def get_previous_post(post_recid):
    previous_post_recid = None
    main_blog_recid = get_parent_blog(post_recid)
    post_date = get_fieldvalues(post_recid, '269__c')
    if len(post_date) > 0:
        post_date = post_date[0]
        recid_list = perform_request_search(p='760__w:"%s" 269__c:0000-00-00-->%s' % (main_blog_recid, post_date), sf='date', so='a')
        if len(recid_list) > 1:
            previous_post_recid = recid_list[1]
    return previous_post_recid

def get_next_comment(comment_recid):
    pass

def get_previous_comment(comment_recid):
    pass
