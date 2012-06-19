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
    elif coll == 'COMMENT':
        parent_post = get_parent_post(recid)
        recid = parent_post

    parent_blog = get_fieldvalues(recid, '760__w')

    if parent_blog:
        return int(parent_blog[0])
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

def get_posts(blog_recid, newest_first=True):
    """ This function returns the list of posts 
    written on the given blog
    @param blog_recid: blog recid
    @type blog_recid: int
    @param newest_first: order in which the posts will be displayed. If
    it is True the newest published posts will be displayed first
    @type newest_first: boolean
    @return: list of posts recids
    @rtype: list
    """

    from invenio.search_engine import perform_request_search
    return perform_request_search(p='760__w:"%s"' % blog_recid, sf='date', so='d')

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
        return int(parent_post[0])
    else:
        return None

def get_sibling_posts(post_recid, newest_first=True, exclude_this_post=True):
    """ This function returns the list of the sibling posts of any 
    post given its recid
    @param post_recid: post recid
    @type post_recid: int
    @param newest_first: order in wich the sibling posts will be displayed. If
    it is True the newest sibling posts will be displayed first
    @type newest_first: boolean
    @param exclude_this_post: if it is True the given post will not be returned
    as a sibling post
    @type exclude_this_post: boolean
    @return: list of sibling posts recids
    @rtype: list
    """

    main_blog_recid = get_parent_blog(post_recid)
    siblings_list = get_posts(main_blog_recid, newest_first)
    if exclude_this_post:
        siblings_list.remove(post_recid)

    return siblings_list

def get_next_post(post_recid):
    """ This function returns the next post of the
    given one that was published
    @param post_recid: post recid
    @type post_recid: int
    @return: the next post recid of the
    given one that was published
    @rtype: recid
    """

    next_post_recid = None
    main_blog_recid = get_parent_blog(post_recid)
    post_date = get_fieldvalues(post_recid, '269__c')
    if post_date:
        post_date = post_date[0]
        from invenio.search_engine import perform_request_search
        recid_list = perform_request_search(p='760__w:"%s" 269__c:%s-->9999-99-99' % \
                                            (main_blog_recid, post_date), sf='date', so='d')
        if len(recid_list) > 1:
            next_post_recid = recid_list[0]

    return next_post_recid


def get_previous_post(post_recid):
    """ This function returns the previous post of the
    given one that was published
    @param post_recid: post recid
    @type post_recid: int
    @return: the previous post recid of the
    given one that was published
    @rtype: recid
    """

    previous_post_recid = None
    main_blog_recid = get_parent_blog(post_recid)
    post_date = get_fieldvalues(post_recid, '269__c')
    if post_date:
        post_date = post_date[0]
        from invenio.search_engine import perform_request_search
        recid_list = perform_request_search(p='760__w:"%s" 269__c:0000-00-00-->%s' % \
                                            (main_blog_recid, post_date), sf='date', so='a')
        if len(recid_list) > 1:
            previous_post_recid = recid_list[1]

    return previous_post_recid

##### COMMENTS #####

def get_comments(post_recid, newest_first=True):
    """ This function returns the list of comments 
    written on the given post
    @param post_recid: post recid
    @type post_recid: int
    @param newest_first: order in wich the comments will be displayed. If
    it is True the newest comments will be displayed first
    @type newest_first: boolean
    @return: list of sibling comments recids
    @rtype: list
    """
    from invenio.search_engine import perform_request_search
    return perform_request_search(p='773__w:"%s"' % post_recid, sf='date', so='d')

def get_sibling_comments(comment_recid, newest_first=True, exclude_this_comment=True):
    """ This function returns the list of the sibling comments of any 
    comment given its recid
    @param comment_recid: comment recid
    @type comment_recid: int
    @param newest_first: order in wich the sibling comments will be displayed. If
    it is True the newest sibling comments will be displayed first
    @type newest_first: boolean
    @param exclude_this_comment: if it is True the given post will not be returned
    as a sibling post
    @type exclude_this_comment: boolean
    @return: list of sibling comments recids
    @rtype: list
    """

    post_recid = get_parent_post(comment_recid)
    siblings_list = get_comments(post_recid, newest_first)
    if exclude_this_comment:
        siblings_list.remove(comment_recid)

    return siblings_list

def get_next_comment(comment_recid):
    pass

def get_previous_comment(comment_recid):
    pass
