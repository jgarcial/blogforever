# -*- coding: utf-8 -*-

## This file is part of Invenio.
## Copyright (C) 2011, 2012, 2013 CERN.
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

from invenio.search_engine import sort_records
from invenio.config import CFG_SITE_LANG

def websearch_instantbrowse_by_field(reclist, \
                                     sf="", so="d"):
    """
    Plugin used to sort and list
    records by a given field.
    @param reclist: HitSet of recIDs
    @type reclist: HitSet
    @param sf: field code (E.g.: "author")
    or MARC tag (E.g.: "100__a")
    More examples:
    field code: "title" or MARC tag: "245__a"
    field code: "posted date" or MARC tag: "269__c" (used to display Posts collection)
    @type sf: string
    @param so: order for listing records
    ("a"=ascending, "d"=descending)
    @type so: string
    @return: sorted list of recIDs according to the selected plugin
    @rtype: list
    """

    recIDs = sort_records(None, reclist, sort_field=sf, sort_order=so)
    return recIDs
