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
from invenio.webblog_utils import get_parent_blog, get_parent_post, transform_format_date
from invenio.search_engine import get_creation_date
from invenio.bibformat_engine import BibFormatObject
import datetime

def format_element(bfo):
    """
    Displays the description of how users should cite
    any content of the archive. The citation includes:
    For blogs: "title".
    Date archived: creation_date. Archived at "record_url"
    Retrieved from the original "original_url"
    For blog posts: author. "title". Blog: "blog_title".
    Date posted: posted_date. Retrieved from the original "original_url
    Date archived: creation_date. Archived at "record_url"
    For comments: author. Blog post: "post_title".
    Retrieved from the original "original_url
    Date archived: creation_date. Archived at "record_url"
    """

    coll = bfo.fields('980__a')[0]
    recid = bfo.control_field('001')

    # let's get the fields we want to show
    if coll in ["BLOGPOST", "COMMENT"]:
        author = bfo.fields('100__a')[0]
        if not author:
            author = "Unknown author"

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
    date = datetime.datetime.strptime(record_creation_date, "%Y-%m-%d")
    record_creation_date = date.strftime("%Y/%m/%d")
    # url in the archive
    record_url = CFG_SITE_URL + "/record/" + recid

    out = """
        <div class="well well-large">
        <h4><i class="icon-pencil"></i>   Cite as</h4>"""

    if coll == "BLOGPOST":
        # we will also show the blog's title of 
        # the corresponding blog post
        blog_recid = get_parent_blog(recid)
        blog_bfo = BibFormatObject(blog_recid)
        try:
            blog_title = blog_bfo.fields('245__a')[0]
        except:
            blog_title = 'Unknown title'

        posted_date = transform_format_date(bfo.fields('269__c')[0])
        out += """
        <span><b>%s</b>. '%s'. Blog: '%s' </br> \
        Date posted: %s. Retrieved from the original post <i>'%s'</i> </br>\
        Date archived: %s. Archived at <i>'%s'</i> </span>""" \
        % (author, title, blog_title, posted_date, original_url, record_creation_date, record_url)

    elif coll == "COMMENT":
        # we will also show the post's title of
        # the corresponding comment
        post_recid = get_parent_post(recid)
        post_bfo = BibFormatObject(post_recid)
        try:
            post_title = post_bfo.fields('245__a')[0]
        except:
            post_title = 'Unknown title'

        out += """
        <span><b>%s. </b>Blog post: '%s'</br> \
         Retrieved from the original comment <i>'%s'</i></br> \
         Date archived: %s. Archived at <i>'%s'</i> </span>""" \
        % (author, post_title, original_url, record_creation_date, record_url)

    else: # coll == "BLOG"
        out += """
        <span>'%s' </br> \
        Retrieved from the original blog <i>'%s'</i></br> \
        Date archived: %s. Archived at <i>'%s'</i> </span>""" \
        % (title, original_url, record_creation_date, record_url)

    out += "</div>"
    return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if
    output of this element should be escaped.
    """

    return 0
