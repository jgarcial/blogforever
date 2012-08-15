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
BibFormat Element - displays the description of how to cite the archive's content
"""

from invenio.config import CFG_SITE_URL
from invenio.webblog_utils import get_parent_blog
from invenio.search_engine import get_creation_date
from invenio.bibformat_engine import BibFormatObject

def format_element(bfo):
    """
    Displays the description of how users should cite
    any content of the archive. The citation includes:
    For blogs: "title". (record_creation_date). record_url
    Retrieved from the original "original_url"
    For blog posts: author. "title". Blog: "blog_title".
    (record_creation_date). record_url
    Retrieved from the original "original_url"
    """

    coll = bfo.fields('980__a')[0]
    recid = bfo.control_field('001')

    # let's get the fields we want to show
    if coll in ["BLOGPOST", "COMMENT"]:
        author = bfo.fields('100__a')[0]
        original_creation_date = bfo.fields('269__c')[0]

    try:
        title = bfo.fields('245__a')[0]
    except:
        title = "Untitled"

    try:
        original_url = bfo.fields('520__u')[0]
    except:
        raise Exception("URL not found")

    # creation date of a record
    record_creation_date = get_creation_date(recid)
    # url in the archive
    record_url = CFG_SITE_URL + "/record/" + recid

    if coll in ["BLOGPOST", "COMMENT"]:
        # we will also show the blog's title of 
        # the corresponding comment or blog post
        blog_recid = get_parent_blog(recid)
        blog_bfo = BibFormatObject(blog_recid)
        try:
            blog_title = blog_bfo.fields('245__a')[0]
        except:
            blog_title = 'Untitled'

        description = """<table style="border:1px solid black;"><tr><td>\
        <span><b>%s</b>. '%s'. </br>Blog: '%s'. (%s). <i>'%s'</i> </br> \
        Retrieved from the original <i>'%s'</i><span></td></tr></table>""" \
        % (author, title, blog_title, record_creation_date, record_url, original_url)
    else:
        description = """<table style="border:1px solid black;"><tr><td>\
        <span>'%s'. (%s). <i>'%s'</i> </br> \
        Retrieved from the original <i>'%s'</i><span></td></tr></table>""" \
        % (title, record_creation_date, record_url, original_url)


    out = """
        <script type="text/javascript">
        function displayCitationDescription(){
            var description = document.getElementById('description');
            var citation_link = document.getElementById('citation_link');
            if (description.style.display == 'none'){
                description.style.display = '';
                citation_link.innerHTML = "Hide citation description"
            } else {
                description.style.display = 'none';
                citation_link.innerHTML = "Show citation description"
            }
        }
        </script>
        """

    out += '<span id="description" style="">' + description + '</span>'
    out += '<a class="moreinfo" id="citation_link" \
            href="javascript:void(0)" onclick="displayCitationDescription()""></a>'
    out += '<script type="text/javascript">displayCitationDescription()</script>'

    return out

#    out = """
#    <a class="moreinfo" id="citation_info" href="#">How to cite this</a>
#    <script type="text/javascript">
#        $(document).ready(function(){
#        $("#citation_info").click(function(){
#        alert("%s");
#        });
#        });
#    </script>""" % description

def escape_values(bfo):
    """
    Called by BibFormat in order to check if
    output of this element should be escaped.
    """

    return 0
