# -*- coding: utf-8 -*-

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

__revision__ = "$Id$"

import PythonMagick

def convert_image(img_path, img_dest_dir, img_name, format_from):
    """
    Plugin used to tranform JPEG images into PNG.
    @param img_path: string with the path of the image to be transformed
    @param img_dest_dir: string with the path where the output image should be stored
    @param img_name: string with the name that the output file should have
    @param format_from: string with the MIME type of the original file
    @return: string with the path of the output file
    """
    img = PythonMagick.Image(img_path)
    if format_from == "image/jpeg":
	img.magick('PNG')
	output_path = img_dest_dir + '/' + img_name + '.png'
	img.write(output_path)
    return output_path
