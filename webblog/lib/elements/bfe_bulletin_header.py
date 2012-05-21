#!/usr/bin/env python
# -*- coding: utf-8 -*-
## This file is part of CDS Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007 CERN.
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
BibFormat Element - format the header of an EBulletin article
"""
from invenio.bibformat_engine import BibFormatObject
from invenio.config import CFG_SITE_URL
from invenio.webjournal_utils import get_release_datetime, issue_to_datetime, get_journal_preferred_language
from invenio.dateutils import get_i18n_day_name, get_i18n_month_name
cfg_messages = {}
cfg_messages["published_in"] = {"en" : "Bulletin Issue",
                                "fr" : "Bulletin N<sup>o</sup>"}
cfg_messages["date"] = {"en" : "date",
                        "fr" : "date"}

def format_element(bfo):
    """
    Formats a header used in Bulletin Articles containing: issue nr., date,
    english/french link, report number
    """
    # get variables
    this_recid = bfo.control_field('001')
    available_languages = bfo.fields('041__a')
    current_language = bfo.lang
    report_number = bfo.fields('037__a')
    issue_numbers = bfo.fields('773__n')
    journal_name = bfo.field('773__t')
    if journal_name.lower() == 'cern bulletin':
        journal_name = 'CERNBulletin'
    elif journal_name.lower() == 'cms bulletin':
        journal_name = 'CMSBulletin'

    preferred_ln = get_journal_preferred_language(journal_name, bfo.lang)

    date = ''
    if len(issue_numbers) > 0:
#        date = get_release_datetime(issue_numbers[0], journal_name)
#        if not date:
        date = issue_to_datetime(issue_numbers[0], journal_name)
        weekday = get_i18n_day_name(date.isoweekday() % 7)
        monthname = get_i18n_month_name(date.month)
        date  = weekday + ' ' + date.strftime('%d') + ' ' + monthname + ' ' + date.strftime('%Y')

    # assemble the HTML output
    out = '<div id="top"><div id="topbanner">&nbsp;</div>'
    if len(issue_numbers) > 0:
        out += '<span class="printLogo">%s, %s</span>' % (" & ".join(["%s" % issue.split("/")[0] for issue in issue_numbers]), date)
    out += '<div id="mainmenu"><table width="100%">'
    out += '<tr>'
    if len(issue_numbers) > 0:
        issue_number, issue_year = issue_numbers[-1].split('/')
        out += '<td class="left"><a href="%s/journal/CERNBulletin/%s/%s" target="_blank">%s: %s, %s</a></td>' % \
               (CFG_SITE_URL, issue_year, issue_number,
                cfg_messages["published_in"][preferred_ln],
                " & ".join(["%s" % issue for issue in issue_numbers]),
                date)
    if len(report_number) > 0:
        out += '<td class="right">%s</td>' % report_number[0]
    out += '</tr>'

    out += '<tr>'
    if len(available_languages) > 1:
        if current_language == "en" and "fr" in available_languages:
            #TODO: server name generic
            out += '<td class="left"><a href="%s/record/%s?ln=fr">&gt;&gt; french version</a></td>' % (CFG_SITE_URL, this_recid)
        elif current_language == "fr" and "en" in available_languages:
            out += '<td class="left"><a href="%s/record/%s?ln=en">&gt;&gt; version anglaise</a></td>' % (CFG_SITE_URL, this_recid)

    out += '<td class="right"></td>'
    out += '</tr>'
    out += '</table></div><div id="mainphoto"></div></div>'

    return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0

if __name__ == "__main__":
    myrec = BibFormatObject(619)
    format(myrec)
