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
"""Configuration for WebHistory module."""

#: Messages used for displaying user history.
#: @type: dict
CFG_WEBHISTORY_MSGS = {
    0: "You sent a message <a href=%(msgurl)s>%(subject)s</a> to user(s): "
    "%(usernames)s.",

    1: "You sent a message <a href=%(msgurl)s>%(subject)s</a> to group(s): "
    "%(groupnames)s.",

    2: "You sent a message <a href=%(msgurl)s>%(subject)s</a> to user(s): "
    "%(usernames)s and group(s): %(groupnames)s.",

    3: "You sent a <a href=%(msgurl)s>message</a> to user(s): %(usernames)s.",

    4: "You sent a <a href=%(msgurl)s>message</a> to group(s): "
    "%(groupnames)s.",

    5: "You sent a <a href=%(msgurl)s>message</a> to user(s): %(usernames)s "
    "and group(s): %(groupnames)s.",

    6: "You displayed <a href=%(recordurl)s>%(title)s</a>.",

    7: "You <a href=%(discussionurl)s>discussed</a> about "
    "<a href=%(recordurl)s>%(title)s</a>.",

    8: "You <a href=%(reviewurl)s>reviewed</a> "
    "<a href=%(recordurl)s>%(title)s</a>. %(stars)s",

    9: "You voted a <a href=%(discussionurl)s>discussion</a> of "
    "<a href=%(recordurl)s>%(title)s</a>.",

    10: "You voted a <a href=%(reviewurl)s>review</a> of "
    "<a href=%(recordurl)s>%(title)s</a>.",

    11: "You reported a <a href=%(discussionurl)s>discussion</a> of "
    "<a href=%(recordurl)s>%(title)s</a> as abuse.",

    12: "You reported a <a href=%(reviewurl)s>review</a> of "
    "<a href=%(recordurl)s>%(title)s</a> as abuse.",

    13: "You subscribed to the <a href=%(discussionurl)s>discussion</a> of "
    "<a href=%(recordurl)s>%(title)s</a>.",

    14: "You created a new <a href=%(groupurl)s>group</a>: %(groupname)s",

    15: "You joined a <a href=%(groupurl)s>group</a>: %(groupname)s",

    16: "You downloaded <a href=%(recordurl)s>%(title)s</a> as %(format)s.",

    17: "You created a new basket: <a href=%(basketurl)s>%(basketname)s</a>",

    18: "You subscribed to a basket: <a href=%(basketurl)s>%(basketname)s</a>",

    19: "You added <a href=%(recordurl)s>%(title)s</a> into basket "
    "<a href=%(basketurl)s>%(basketname)s</a>.",

    20: "You added a <a href=%(noteurl)s>note</a> for "
    "<a href=%(recordurl)s>%(title)s</a> in basket "
    "<a href=%(basketurl)s>%(basketname)s</a>.",

    21: "You set an <a href=%(alerturl)s>alert</a> for %(pattern)s.",

    22: "You <a href=%(searchurl)s>searched</a> for %(pattern)s.",

    23: "You made a <a href=%(searchurl)s>search</a>.",

    24: "You purchased a <a href='%(paymenturl)s'>premium package</a> "
    "for %(price).2f %(currency)s. Your transaction ID was %(token)s."
}


#: Messages used for constructing share message of user history.
#: @type: dict
CFG_SHARE_MSGS = {
    0: "I sent a message '%(subject)s' to user(s): %(usernames)s.",

    1: "I sent a message '%(subject)s' to group(s): %(groupnames)s.",

    2: "I sent a message '%(subject)s' to user(s): %(usernames)s and group(s):"
    " %(groupnames)s.",

    3: "I sent a message to user(s): %(usernames)s.",

    4: "I sent a message to group(s): %(groupnames)s.",

    5: "I sent a message to user(s): %(usernames)s and group(s): "
    "%(groupnames)s.",

    6: "I displayed <a href=%(recordurl)s>%(title)s</a>.",

    7: "I <a href=%(discussionurl)s>discussed</a> about "
    "<a href=%(recordurl)s>%(title)s</a>.",

    8: "I <a href=%(reviewurl)s>reviewed</a> "
    "<a href=%(recordurl)s>%(title)s</a>. %(stars)s",

    9: "I voted a <a href=%(discussionurl)s>discussion</a> of "
    "<a href=%(recordurl)s>%(title)s</a>.",

    10: "I voted a <a href=%(reviewurl)s>review</a> of "
    "<a href=%(recordurl)s>%(title)s</a>.",

    11: "I reported a <a href=%(discussionurl)s>discussion</a> of "
    "<a href=%(recordurl)s>%(title)s</a> as abuse.",

    12: "I reported a <a href=%(reviewurl)s>review</a> of "
    "<a href=%(recordurl)s>%(title)s</a> as abuse.",

    13: "I subscribed to the <a href=%(discussionurl)s>discussion</a> of "
    "<a href=%(recordurl)s>%(title)s</a>.",

    14: "I created a new group: %(groupname)s",

    15: "I joined a group: %(groupname)s",

    16: "I downloaded <a href=%(recordurl)s>%(title)s</a> as %(format)s.",

    17: "I created a new basket: <a href=%(basketurl)s>%(basketname)s</a>",

    18: "I subscribed to a basket: <a href=%(basketurl)s>%(basketname)s</a>",

    19: "I added <a href=%(recordurl)s>%(title)s</a> into basket "
    "<a href=%(basketurl)s>%(basketname)s</a>.",

    20: "I added a <a href=%(noteurl)s>note</a> for "
    "<a href=%(recordurl)s>%(title)s</a> in basket "
    "<a href=%(basketurl)s>%(basketname)s</a>.",

    21: "I set an alert for <a href=%(searchurl)s>%(pattern)s</a>.",

    22: "I <a href=%(searchurl)s>searched</a> for %(pattern)s.",

    23: "I made a <a href=%(searchurl)s>search</a>.",

    24: "I purchased a premium package for %(price).2f %(currency)s."
}

CFG_WEBHISTORY_JSON_DATE_FORMAT = "%d/%m/%Y"
CFG_WEBHISTORY_JSON_TIME_FORMAT = "%H:%M:%S"
CFG_WEBHISTORY_JSON_DATETIME_FORMAT = ("%s %s"
                                       % (CFG_WEBHISTORY_JSON_DATE_FORMAT,
                                          CFG_WEBHISTORY_JSON_TIME_FORMAT))
CFG_WEBHISTORY_DATEPICKER_DATETIME = "dd/mm/yy"
