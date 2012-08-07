# This file is part of Invenio.
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

__revision__ = "$Id$"


import os
import shutil
import time
import tempfile
from invenio.websubmit_config import InvenioWebSubmitFunctionError
from invenio.webblog_utils import get_blog_descendants
from invenio.search_engine_utils import get_fieldvalues
from invenio.bibtask import task_low_level_submission, bibtask_allocate_sequenceid
from invenio.config import CFG_TMPDIR
from invenio.textutils import wash_for_xml

def Make_Delete_Records(parameters, curdir, form, user_info=None):
    """
    Function used to delete a blog and all its descendants.
    The blog URL will be provided and from there all its
    descendants will be found. The field (980, c, DELETED)
    will be added to all of them.
    """

    # let's get the blog's recid
    try:
        f = open("%s/SN" % curdir, "r")
    except IOError:
        ## Unable to read the SN file's content
        msg = """Unable to correctly read the current submission's recid"""
        raise InvenioWebSubmitFunctionError(msg)

    blog_recid = int(f.read().strip())
    f.close()
    # let's build the list of recids (blog + descendants) to delete
    recids = get_blog_descendants(blog_recid)
    recids.append(blog_recid)

    # let's build the final xml
    marcxml_output = '<?xml version="1.0" encoding="UTF-8"?>\n'
    marcxml_output += '<collection xmlns="http://www.loc.gov/MARC21/slim">'

    for recid in recids:
        record_marcxml = """
    <record>
    <controlfield tag="001">%(recid)s</controlfield>
    <datafield tag="980" ind1=" " ind2=" ">
        <subfield code="c">DELETED</subfield>
    </datafield>
    </record>""" % {'recid': recid}
        marcxml_output += record_marcxml

    marcxml_output += '\n</collection>\n'

    # Escape XML-reserved chars and clean the unsupported ones (mainly
    # control characters)
    marcxml_output = wash_for_xml(marcxml_output)

    f = open("%s/recmysql" % curdir,"w")
    f.write(marcxml_output)
    f.close()

    blog_url = get_fieldvalues(blog_recid, '520__u')[0]
    sequence_id = bibtask_allocate_sequenceid(curdir)
    initial_file = os.path.join(curdir, "recmysql")
    tmp_fd, final_file = tempfile.mkstemp(dir=CFG_TMPDIR,
                                          prefix="%s_%s" % \
                                          (blog_url.replace('/', '_'),
                                           time.strftime("%Y-%m-%d_%H:%M:%S")))

    os.close(tmp_fd)
    shutil.copy(initial_file, final_file)
    bibupload_id = task_low_level_submission('bibupload', 'websubmit.Make_Delete_Records', \
                                             '-c', final_file, '-P', '3', '-I', str(sequence_id))
    open(os.path.join(curdir, 'bibupload_id'), 'w').write(str(bibupload_id))

    return ""

