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

from invenio.search_engine import search_pattern_parenthesised
from invenio.intbitset import intbitset
import time

def websearch_instantbrowse_by_number_of_years(reclist, \
                                               num_years=""):
    """
    Plugin used to list records of
    the last 'num_years' years.
    If 'num_years' is not provided only records
    of the current year will be displayed.
    @param reclist: HitSet of recIDs
    @type reclist: HitSet
    @param num_years: number of years ago (E.g.: "5")
    @type num_years: string
    @return: list of recIDs and output format
    @rtype: tuple(list, string)
    """

    this_year = time.strftime("%Y", time.localtime())
    final_reclist = intbitset()
    # detect recIDs only from this year:
    if not num_years:
        recIDs = list(reclist & \
                        search_pattern_parenthesised(p='year:%s' % this_year))
    else:
        # detect recIDs from last num_years':
        for nb in range(int(num_years)):
            year = str(int(this_year) - nb)
            final_reclist = final_reclist.union(reclist & \
                                search_pattern_parenthesised(p='year:%s' % year))
        recIDs = list(final_reclist)

    return (recIDs, 'hb')

