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
"""
Functions to place images in a latex document.
"""
import Image
from shutil import copyfile
import os
import urllib2

from invenio.config import CFG_WEBDIR
from invenio.bibformat_pdf_with_latex_template_config import \
    CFG_BIBFORMAT_IMG_SRC_URL, CFG_BIBFORMAT_LATEX_DEFAULT_IMG_FORMAT, \
    CFG_BIBFORMAT_LATEX_SUPPORTED_IMG_EXTS
from invenio.textutils import get_random_string
from flask import g


def get_unique_file_path(file_extension):
    """
    Returns a unique path to save the image temporarily.

    @param file_extension:
    @type file_extension: str

    @return: A path for the image
    @type: str
    """
    while True:
        filename = get_random_string(60, is_alphanumeric=True)
        path = os.path.join(g.tex_dir, filename)
        try:
            with open(path + "." + file_extension):
                pass
        except IOError:
            return path


def get_image_path(img_src):
    """
    Returns the path of the image. If the image does not exist in filesystem,
    downloads it to an available location.

    @param img_src: Source of the image
    @type img_src: str

    @return: The path of the image.
    @rtype: str
    """
    (source, file_name) = os.path.split(img_src)
    is_error_occurred = False
    is_local_source = False

    # Check whether src is relative/absolute path or url.
    if source:
        url_match_obj = CFG_BIBFORMAT_IMG_SRC_URL.match(source)

        if url_match_obj:
            is_local_source = False
        elif not url_match_obj:
            is_local_source = True
    else:
        is_local_source = True

    try:
        query_args_start_index = file_name.index("?")
        if query_args_start_index > -1:
            file_name = file_name[:query_args_start_index]

        extension = file_name.split(".")[-1]
        path_extension = '.' + extension
    except:
        path_extension = extension = ""
    path_without_extension = get_unique_file_path(path_extension)

    path = path_without_extension + path_extension

    if not is_local_source:
        # Download image.
        try:
            response = urllib2.urlopen(img_src)
            tmpf = open(path, 'wb')
            tmpf.write(response.read())
            tmpf.close()
        except:
            is_error_occurred = True

    elif is_local_source:
        local_path = os.path.join(CFG_WEBDIR, img_src)
        if os.path.exists(local_path):
            copyfile(local_path, path)
        else:
            is_error_occurred = True

    if not is_error_occurred:
        if not extension in CFG_BIBFORMAT_LATEX_SUPPORTED_IMG_EXTS:
            # Convert img to a supported format
            img = Image.open(path)
            path = (path_without_extension + "." +
                    CFG_BIBFORMAT_LATEX_DEFAULT_IMG_FORMAT)
            img.save(path)

        return path

    return False