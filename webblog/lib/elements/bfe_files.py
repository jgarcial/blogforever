# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013 CERN.
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

"""BibFormat element - Prints the attached files of a record
"""
__revision__ = "$Id$"

from invenio.bibformat_elements.bfe_fulltext import get_files, sort_alphanumerically
from invenio.messages import gettext_set_language
from cgi import escape

def format_element(bfo, separator='; '):
    """
    This is the format for formatting the names and links
    of the files attached to a record.
    @param separator: the separator between urls.
    """

    _ = gettext_set_language(bfo.lang)
    out = '<h4><i class="icon-file"></i>&nbsp;&nbsp;'
    out += _("Files attached to this record")
    out += "</h4><div class=span4>"

    # Retrieve files
    (parsed_urls, old_versions, additionals) = get_files(bfo)

    main_urls = parsed_urls['main_urls']
    others_urls = parsed_urls['others_urls']
    if parsed_urls.has_key('cern_urls'):
        cern_urls = parsed_urls['cern_urls']

    # Build urls list.
    # Escape special chars for <a> tag value.
    if main_urls:
        main_urls_keys = sort_alphanumerically(main_urls.keys())
        for descr in main_urls_keys:
            urls = main_urls[descr]
            urls_dict = {}
            for url, name, url_format in urls:
                if name not in urls_dict:
                    urls_dict[name] = [(url, url_format)]
                else:
                    urls_dict[name].append((url, url_format))
            for name, urls_and_format in urls_dict.items():
                if len(urls_dict) > 1:
                    print_name = "%s - " % name
                    url_list = [print_name]
                else:
                    url_list = []
                for url, url_format in urls_and_format:
                    url_list.append('<a class=moreinfo href="%(url)s">%(url_format)s</a>' % {
                        'url': escape(url, True),
                        'url_format': escape(url_format.upper())
                    })
                out += separator + " ".join(url_list)
            out +=  separator + "</div>"

    if out.endswith('<br />'):
        out = out[:-len('<br />')]

    out += "</div>"

    return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
