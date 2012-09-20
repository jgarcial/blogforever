# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2005, 2006, 2007, 2008, 2010, 2011 CERN.
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

__revision__ = \
   "$Id$"

from invenio.config import \
     CFG_ACCESS_CONTROL_LEVEL_SITE, \
     CFG_CERN_SITE
from invenio.dbquery import run_sql
from invenio.bibrank_downloads_indexer import database_tuples_to_single_list
from invenio.search_engine_utils import get_fieldvalues
from invenio.webblog_utils import get_parent_blog, get_blog_descendants


def record_exists(recID):
    """Return 1 if record RECID exists.
       Return 0 if it doesn't exist.
       Return -1 if it exists but is marked as deleted.
       Copy from search_engine"""
    out = 0
    query = "SELECT id FROM bibrec WHERE id='%s'" % recID
    res = run_sql(query, None, 1)
    if res:
        # record exists; now check whether it isn't marked as deleted:
        dbcollids = get_fieldvalues(recID, "980__%")
        if ("DELETED" in dbcollids) or (CFG_CERN_SITE and "DUMMY" in dbcollids):
            out = -1 # exists, but marked as deleted
        else:
            out = 1 # exists fine
    return out

### INTERFACE

def register_page_view_event(recid, uid, client_ip_address):
    """Register Detailed record page view event for record RECID
       consulted by user UID from machine CLIENT_HOST_IP.
       To be called by the search engine.
    """
    if CFG_ACCESS_CONTROL_LEVEL_SITE >= 1:
        # do not register access if we are in read-only access control
        # site mode:
        return []
    return run_sql("INSERT INTO rnkPAGEVIEWS " \
                   " (id_bibrec,id_user,client_host,view_time) " \
                   " VALUES (%s,%s,INET_ATON(%s),NOW())", \
                   (recid, uid, client_ip_address))

def calculate_reading_similarity_list(recid, type="pageviews"):
    """Calculate reading similarity data to use in reading similarity
       boxes (``people who downloaded/viewed this file/page have also
       downloaded/viewed'').  Return list of (recid1, score1),
       (recid2,score2), ... for all recidN that were consulted by the
       same people who have also consulted RECID.  The reading
       similarity TYPE can be either `pageviews' or `downloads',
       depending whether we want to obtain page view similarity or
       download similarity.
    """
    if CFG_CERN_SITE:
        return [] # CERN hack 2009-11-23 to ease the load
    if type == "downloads":
        tablename = "rnkDOWNLOADS"
    else: # default
        tablename = "rnkPAGEVIEWS"

    # firstly compute the set of client hosts who consulted recid:
    client_host_list = run_sql("SELECT DISTINCT(client_host)" + \
                               " FROM " + tablename + \
                               " WHERE id_bibrec=%s " + \
                               " AND client_host IS NOT NULL",
                               (recid,))

    # BF: let's display blogs that were read by people who
    # also read the current recid parent blog
    from invenio.webblog_utils import get_parent_blog
    parent_blog = get_parent_blog(recid)
    res = []
    if parent_blog:
        if client_host_list != ():
            client_host_list = str(database_tuples_to_single_list(client_host_list))
            client_host_list = client_host_list.replace("L", "")
            client_host_list = client_host_list.replace("[", "")
            client_host_list = client_host_list.replace("]", "")
    
            res = run_sql("SELECT CAST(b.value AS UNSIGNED), COUNT(DISTINCT(client_host)) AS c" \
                      "  FROM rnkPAGEVIEWS v, bibrec_bib76x bb, bib76x b WHERE client_host IN (" + client_host_list + ")" + \
                      "   AND v.id_bibrec != %s" \
                      "   AND v.id_bibrec = bb.id_bibrec" \
                      "   AND bb.id_bibxxx = b.id" \
                      "   AND b.tag = '760__w'" \
                      "   AND b.value != %s" \
                      " GROUP BY b.value ORDER BY c",
                      (recid, parent_blog))

        # secondly look up all recids that were consulted by these client hosts,
        # and order them by the number of different client hosts reading them:
#        res = run_sql("SELECT id_bibrec,COUNT(DISTINCT(client_host)) AS c" \
#                      "  FROM " + tablename + \
#                      " WHERE client_host IN (" + client_host_list + ")" + \
#                      "   AND id_bibrec != %s" \
#                      " GROUP BY id_bibrec ORDER BY c DESC LIMIT 10",
#                      (recid,))

    #BF: let's group the records by blog collection
#    results = {}
#    res = list(res)
#    if get_fieldvalues(recid, '980__a')[0] == 'BLOG':
#        blog_descendants = get_blog_descendants(recid)
#        for row in res:
#            recid = row[0]
#            # recid is a post, comment or page from a different BLOG
#            if recid not in blog_descendants:
#                # let's get the blog to which belongs each record
#                parent_blog = get_parent_blog(recid)
#                if parent_blog not in results:
#                    results.update([(parent_blog, row[1])])
#                else:
#                    results.update([(parent_blog, results[parent_blog] + 1)])
#
#        res = results.items()

    return res
