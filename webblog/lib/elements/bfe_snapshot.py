#!/usr/bin/env python
# -*- coding: utf-8 -*-
## This file is part of CDS Invenio.
## Copyright (C) 2013 CERN.
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
BibFormat Element - displays snapshot
"""
from invenio.bibformat_engine import BibFormatObject
from invenio.config import CFG_SITE_URL


def format_element(bfo, only_image=False):
    """
    Displays the snapshot
    """

    # get variables
    this_recid = bfo.control_field('001')
    files = bfo.fields('8564_')

    snapshot_url = ''

    for f in files:
        if f['u'].find('SnapShot_') > -1:
            snapshot_url = f['u']

    img = """<img src="%s"> """ % snapshot_url
    if only_image:
        return img

    out = """<div class="well well-small modal-margin"> 
            <a href="#SnapshotModal" data-toggle="modal"><div class="snapshot-thumb">%s</div> <small>
            <p>This is a snapshot of this blog as it appeared when it was archived. Click to enlarge</p></small></a></div> """ % (img)
    out += """<!-- Snapshot Modal -->
            <div id="SnapshotModal" class="modal fade" tabindex="-1" role="dialog">
                  <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
                    <h3 id="myModalLabel">Blog snapshot</h3>
                  </div>
                  <div class="modal-body">
                        <img src="%s" />
                  </div>
                  <div class="modal-footer">
                    <button class="btn" data-dismiss="modal" aria-hidden="true">Close</button>
                  </div>
            </div>""" % snapshot_url
    return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
