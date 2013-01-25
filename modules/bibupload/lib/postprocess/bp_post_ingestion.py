 # -*- coding: utf-8 -*-
 ##
 ## This file is part of Invenio.
 ## Copyright (C) 2009, 2010, 2011 CERN.
 ##
 ## Invenio is free software; you can redistribute it and/or
 ## modify it under the terms of the GNU General Public License as
 ## along with Invenio; if not, write to the Free Software Foundation, Inc.,
 ## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
 
"""BlogForever ingestion post-processing.
   Inserts METS file in mongoDB.
"""

import sys
import time


def bp_post_ingestion(filename):
    """

    @param: submissionID
    @type: string
    """
 
    ## JG: insert mets in mongodb
 
    return 1
