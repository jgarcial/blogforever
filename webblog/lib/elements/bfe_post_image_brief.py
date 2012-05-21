#!/usr/bin/env python
# -*- coding: utf-8 -*-
## This file is part of CDS Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007 CERN.
##
## CDS Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## CDS Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with CDS Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
BibFormat Element -
"""

def format_element(bfo):
    """

    """

#    attached_files = bfo.fields('8564__u')
#    
#    # get only the files .jpg, .png
#    attached_files_names = [file[file.rfind('/') + 1:] for file in attached_files]
#    
#    # exclude "snapshot", include .jpg, .png
#    final_images = []
#    for name in attached_files_names:
#        name_split = name.split('.')
#        ext = ""
#        if len(name_split) > 1:
#            ext = str(name_split[1])
#        if name.find("snapshot") == -1 and (ext == "png" or ext == "jpg"):
#            final_images = name
            
    img = '<img src="http://cdsweb.cern.ch/record/1368911/files/BlogForever_image.png" width="110" height="110" hspace="10" align="left">'
       
    # http://pcuds99.cern.ch/record/1778/files/subID21
    # http://pcuds99.cern.ch/record/1778/files/TL_snapshot.png
    #http://pcuds99.cern.ch/record/1778/files/snapshot.pdf
    
    # VER bfe_photos


    return '<div>' + img + '</div>'

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0


def format_size(size):
    """
    Get human-readable string for the given size in Bytes
    """
    if size < 1024:
        return "%d byte%s" % (size, size != 1 and 's' or '')
    elif size < 1024 * 1024:
        return "%.1f KB" % (size / 1024)
    elif size < 1024 * 1024 * 1024:
        return "%.1f MB" % (size / (1024 * 1024))
    else:
        return "%.1f GB" % (size / (1024 * 1024 * 1024))
