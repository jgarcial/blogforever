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

from invenio.search_engine import sort_records
from invenio.config import CFG_SITE_LANG

def websearch_instantbrowse_by_field(reclist, \
                                     field="", order="d", \
                                     pattern="", verbose=0, of="hb", \
                                     ln=CFG_SITE_LANG):
    """
    Plugin used to sort and list
    records by a given field.
    @param reclist: HitSet of recIDs
    @type reclist: HitSet
    @param field: field code (E.g.: "author")
    or MARC tag (E.g.: "100__a")
    @type field: string
    @param order: order for listing records
    ("a"=ascending, "d"=descending)
    @type order: string
    @param pattern: pattern to search for
    (E.g.: "ellis")
    @type pattern: string
    @param verbose: verbose level (0=min, 9=max)
    @type verbose: Useful to print some
    internal information on the searching process
    in case something goes wrong.
    @param of: output format (E.g.: "hb")
    @type of: string
    @param ln: language (E.g.: "en")
    @type ln: string
    @return: sorted list of recIDs
    @rtype: list
    """

    recIDs = sort_records(None, reclist, sort_field=field, sort_order=order, \
                          sort_pattern=pattern, verbose=verbose, of=of, ln=ln)
    return recIDs
