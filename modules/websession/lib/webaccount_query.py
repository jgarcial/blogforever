# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012 CERN.
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

"""Query definitions for module webaccount"""

from invenio.sqlalchemyutils import db
from invenio.websession_model import UserBibrecHighlights, UserBibrecAnnotations
from flask import jsonify

def set_user_bibrec_highlights(uid, recid, highlights):
    """
    Saves current indexes of highlighted area.

    @param uid -int- : user ID

    @param recid -int- : record ID

    @param highlights -str- : indexes of highlights
    """
    uid = int(uid)
    recid = int(recid)

    if highlights:
        user_highlight_entry = UserBibrecHighlights(uid, recid, highlights)
        db.session.merge(user_highlight_entry)
    else:
        UserBibrecHighlights.query.filter(UserBibrecHighlights.id_user == uid).\
            filter(UserBibrecHighlights.id_bibrec == recid).delete(synchronize_session=False)


def get_user_bibrec_highlights(uid, recid):
    """
    Returns the highlight indexes of the highlighted area.

    @param uid -int- : user ID

    @param recid -int- : record ID
    """
    try:
        table_entry = UserBibrecHighlights.query.filter(UserBibrecHighlights.id_user == uid).\
            filter(UserBibrecHighlights.id_bibrec == recid).first()
        return (table_entry.highlights, table_entry.last_updated)
    except:
        return ("","")


def get_all_annotations(uid, recid):
    """
    Gets all of the user annotations on the record provided with recid.

    @param uid -int- : user ID

    @param recid -int- : record ID

    @return -str- : Dictionary in json string. "{"annotation_id":"annotation"}"
    """

    table_entries = UserBibrecAnnotations.query.filter(UserBibrecAnnotations.id_bibrec == recid).\
        filter(UserBibrecAnnotations.id_user == uid).all()

    json_form = "{"
    for elem in table_entries:
        json_form += "\"%s\":\"%s\", " % (str(int(elem.id_annotation)), elem.annotation)

    if len(json_form) > 2:
        json_form = json_form[:-2]
    json_form += "}"
    return json_form
#    except:
#        return {}


def set_user_bibrec_annotation(uid, recid, annotation, annotation_id=0, last_updated=""):
    """
    Inserts or updates an annotation and returns that record.

    @param uid -int- : user ID

    @param recid -int- : record ID

    @param annotation -str- : annotation text

    @param annotation_id -int- : Id of the annotation corresponding to a
        highlight.

    @param last_updated -int- : The last updated time of an annotation (used in
        undo operations)
    """
    # Get last annotation before update it. (For undo)
    return_dict = get_user_bibrec_annotation(uid, recid, annotation_id)
    return_dict["last_updated"] = str(return_dict["last_updated"])

    if isinstance(annotation, unicode):
        annotation = annotation.encode("utf8", errors="replace")

    user_annotation_entry = UserBibrecAnnotations(int(recid), int(annotation_id), int(uid),\
                                                  annotation, last_updated)
    db.session.merge(user_annotation_entry)

    return return_dict


def get_user_bibrec_annotation(uid, recid, annotation_id):
    """
    Gets the annotation record.

    @param uid -int- : user ID

    @param recid -int- : record ID

    @param annotation_id -int- : annotation_id

    @return -dict- : annotatation record
        keys: ["annotation", "last_updated"]
    """
    try:
        table_entry = UserBibrecAnnotations.query.filter(UserBibrecAnnotations.id_annotation == annotation_id).\
            filter(UserBibrecAnnotations.id_bibrec == recid).\
            filter(UserBibrecAnnotations.id_user == uid).first()
        return {"annotation": table_entry.annotation, "last_updated": table_entry.last_updated}
    except:
        return {"annotation":"", "last_updated":""}


def delete_user_bibrec_annotation(uid, recid, annotation_id=""):
    """
    Deletes the annotation with given user id, record id and
        annotation id and returns deleted annotation.

    If annotation_id isn't given, it removes all the annotations.

    @param uid -int- : user ID

    @param recid -int- : record ID

    @param annotation_id -int- : annotation ID

    @return -dict- : deleted annotation for undo operation
        keys: ["annotation", "last_updated"]
    """
    # Delete corresponding annotation entry.
    if annotation_id:
        return_dict = get_user_bibrec_annotation(uid, recid, annotation_id)
        return_dict["last_updated"] = str(return_dict["last_updated"])

        UserBibrecAnnotations.query.filter(UserBibrecAnnotations.id_annotation == annotation_id).\
            filter(UserBibrecAnnotations.id_bibrec == recid).\
            filter(UserBibrecAnnotations.id_user == uid).delete(synchronize_session=False)

        return return_dict

    # Delete all annotations of the corresponding user and record.
    else:
        UserBibrecAnnotations.query.filter(UserBibrecAnnotations.id_bibrec == recid).\
            filter(UserBibrecAnnotations.id_user == uid).delete(synchronize_session=False)

        return {"annotation": "", "last_updated": ""}
