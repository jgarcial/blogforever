# -*- coding: utf-8 -*-
##
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
"""Database models for WebHistory module"""

from invenio.sqlalchemyutils import db
from invenio.webmessage_model import MsgMESSAGE


class HstShare(db.Model):
    """
    Represents a HstShare model
    """
    __tablename__ = 'hstSHARE'

    #: ID of the message.
    #: @type: L{Column}
    id_msgMESSAGE = db.Column(db.Integer(11, unsigned=False),
                              db.ForeignKey(MsgMESSAGE.id),
                              nullable=False,
                              primary_key=True)

    #: Type of the history. (i.e. The class name of the history collector)
    #: @type: L{Column}
    type_history = db.Column(db.String(255),
                             nullable=False)

    #: Serialized history element.
    #: @type: L{Column}
    serialized = db.Column(db.PickleType(),
                           nullable=True)

__all__ = ['HstShare']
