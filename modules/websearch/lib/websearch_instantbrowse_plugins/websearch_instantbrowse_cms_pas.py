# -*- coding: utf-8 -*-

## This file is part of Invenio.
## Copyright (C) 2011 CERN.
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

import string

def websearch_instantbrowse_cms_pas(reclist, recIDs_to_remove=""):
    """
    Plugin used to display the records of one collection
    except given records.
    This plugin is used for "CMS Physics Analysis Summaries"
    collection like a temporary hack.
    @param reclist: HitSet of recIDs
    @type reclist: HitSet
    @param recIDs_to_remove: list of recIDs
    belongs to reclist that will not be displayed
    (E.g.: "1281585")
    (E.g.: "56,89,22")
    @type recIDs_to_remove: string
    @return: list of recIDs and output format
    @rtype: tuple(list, string)
    """

    recIDs = list(reclist)
    if recIDs_to_remove:
        recIDs_to_remove = string.split(recIDs_to_remove, ",")
        for recID_to_remove in recIDs_to_remove:
            if int(recID_to_remove) in recIDs:
                recIDs.remove(int(recID_to_remove))

    return (recIDs, 'hb')