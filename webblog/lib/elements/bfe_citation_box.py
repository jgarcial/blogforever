# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2012 CERN.
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
BibFormat Element - displays the description of how to cite a record
"""

from invenio.config import CFG_SITE_URL
from invenio.webblog_utils import get_parent_blog, get_parent_post
from invenio.search_engine import get_creation_date
from invenio.bibformat_engine import BibFormatObject

def format_element(bfo):
    """
    Displays the description of how users should cite
    any content of the archive. The citation includes:
    For blogs: "title".
    Date created: creation_date. record_url
    Retrieved from the original "original_url"
    For blog posts: author. "title". Blog: "blog_title".
    Date created: creation_date. record_url
    Date posted: posted_date. Retrieved from the original "original_url"
    For comments: author. Blog post: "post_title".
    Date created: creation_date. record_url
    Retrieved from the original "original_url"
    """

    coll = bfo.fields('980__a')[0]
    recid = bfo.control_field('001')

    # let's get the fields we want to show
    if coll in ["BLOGPOST", "COMMENT"]:
        author = bfo.fields('100__a')[0]
        if not author:
            author = "Unknown author"
        try:
            posted_date = bfo.fields('269__c')[0]
            # hack
            if posted_date.find("ERROR") > -1:
                posted_date = "Unknown date"
            else:
                date = datetime.datetime.strptime(posted_date, "%m/%d/%Y %I:%M:%S %p")
                posted_date = date.strftime("%Y/%m/%d %H:%M:%S")
        except:
            posted_date = "Unknown date"

    try:
        title = bfo.fields('245__a')[0]
    except:
        title = "Unknown title"

    try:
        original_url = bfo.fields('520__u')[0]
    except:
        raise Exception("URL not found")

    # creation date of a record
    record_creation_date = get_creation_date(recid)
    # url in the archive
    record_url = CFG_SITE_URL + "/record/" + recid

    if coll == "BLOGPOST":
        # we will also show the blog's title of 
        # the corresponding blog post
        blog_recid = get_parent_blog(recid)
        blog_bfo = BibFormatObject(blog_recid)
        try:
            blog_title = blog_bfo.fields('245__a')[0]
        except:
            blog_title = 'Unknown title'

        out = """<h4>Citation:</h4> 
        <div class="well well-large">
        <span><b>%s </b>: '%s'. Blog: '%s'. </br> \
        Date created: %s. <i>'%s'</i> </br>\
        Date posted: %s. Retrieved from the original post <i>'%s'</i>. </span> </div>""" \
        % (author, title, blog_title, record_creation_date, record_url, posted_date, original_url)

    elif coll == "COMMENT":
        # we will also show the post's title of
        # the corresponding comment
        post_recid = get_parent_post(recid)
        post_bfo = BibFormatObject(post_recid)
        try:
            post_title = post_bfo.fields('245__a')[0]
        except:
            post_title = 'Unknown title'

        out = """<h4>Citation:</h4>
        <div class="well well-large">\
        <span><b>%s. </b>Blog post: '%s'.</br> \
        Date created: %s. <i>'%s'</i> </br> \
        Retrieved from the original comment <i>'%s'</i></span> </div>""" \
        % (author, post_title, record_creation_date, record_url, original_url)

    else: # coll == "BLOG"
        out = """<h4>Citation:</h4>
        <div class="well well-large">\
        <span>'%s' </br> \
        Date created: %s. <i>'%s'</i> </br> \
        Retrieved from the original blog <i>'%s'</i></span> </div>""" \
        % (title, record_creation_date, record_url, original_url)

    return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if
    output of this element should be escaped.
    """

    return 0
