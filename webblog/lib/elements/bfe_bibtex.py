# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2006, 2007, 2008, 2009, 2010, 2011, 2013 CERN.
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

"""BibFormat element - Prints BibTeX meta-data
"""
__revision__ = "$Id$"

from invenio.config import CFG_SITE_LANG
from invenio.webblog_utils import transform_format_date

def format_element(bfo, width="50"):
    """
    Prints a full BibTeX record.

    'width' must be bigger than or equal to 30.
    This format element is an example of large element, which does
    all the formatting by itself

    @param width: the width (in number of characters) of the record
    """
    out = "@"
    width = int(width)
    if width < 30:
        width = 30

    name_width = 19
    value_width = width-name_width
    recID = bfo.control_field('001')

#    collections = bfo.fields("980__a")
##    #Print entry type
#    if collections:
#        out += collections[0].lower()

    out += "misc"

    out += "{"
    #Print BibTeX key
    #
    #Try to have: author_name:recID
    #If author_name cannot be found, use primary_report_number
    #If primary_report_number cannot be found, use additional_report_number
    #If additional_report_number cannot be found, use title:recID
    #If title cannot be found, use only recID
    #
    #The construction of this key is inherited from old BibTeX format
    #written in EL, in old BibFormat.
    key = recID
    author = bfo.field("100__a")
    if author != "":
        key = get_name(author)+":"+recID
    else:
        title = bfo.field("245__a")
        if title != "":
            key = get_name(title)+":"+recID
    out += key +","

    #Print authors
    #If author cannot be found, print a field key=recID
    if author == "":
        out += format_bibtex_field("key",
                                   recID,
                                   name_width,
                                   value_width)
    else:
        out += format_bibtex_field("author",
                                   author,
                                   name_width,
                                   value_width)

    #Print title
    import invenio.bibformat_elements.bfe_title as bfe_title
    title = bfe_title.format_element(bfo=bfo, separator = ". ")
    out += format_bibtex_field("title",
                               title,
                               name_width,
                               value_width)

    posted_date = transform_format_date(bfo.fields('269__c')[0])
    # hack
    if posted_date == "Unknown date":
        posted_date = ""

    #Print month
    try:
        month = get_month(posted_date)
        out += format_bibtex_field("month",
                                   month,
                                   name_width,
                                   value_width)
    except:
        pass

    #Print year
    try:
        year = get_year(posted_date)

        out += format_bibtex_field("year",
                                   year,
                                   name_width,
                                   value_width)
    except:
        pass

    out +="\n}"

    return out


def format_bibtex_field(name, value, name_width=20, value_width=40):
    """
    Formats a name and value to display as BibTeX field.

    'name_width' is the width of the name of the field (everything before " = " on first line)
    'value_width' is the width of everything after " = ".

    6 empty chars are printed before the name, then the name and then it is filled with spaces to meet
    the required width. Therefore name_width must be > 6 + len(name)

    Then " = " is printed (notice spaces).

    So the total width will be::
        name_width + value_width + len(" = ")
                                        (3)

    if value is empty string, then return empty string.

    For example format_bibtex_field('author', 'a long value for this record', 13, 15) will
    return :
    >>
    >>      name    = "a long value
    >>                 for this record",
    """
    if name_width < 6 + len(name):
        name_width = 6 + len(name)
    if value_width < 2:
        value_width = 2
    if value is None or value == "":
        return ""

    #format name
    name = "\n      "+name
    name = name.ljust(name_width)

    #format value
    value = '"'+value+'"' #Add quotes to value
    value_lines = []
    last_cut = 0
    cursor = value_width -1 #First line is smaller because of quote
    increase = False
    while cursor < len(value):
        if cursor == last_cut: #Case where word is bigger than the max
                               #number of chars per line
            increase = True
            cursor = last_cut+value_width-1

        if value[cursor] != " " and not increase:
            cursor -= 1
        elif value[cursor] != " " and increase:
            cursor += 1
        else:
            value_lines.append(value[last_cut:cursor])
            last_cut = cursor
            cursor += value_width
            increase = False
    #Take rest of string
    last_line = value[last_cut:]
    if last_line != "":
        value_lines.append(last_line)

    tabs = "".ljust(name_width + 2)
    value = ("\n"+tabs).join(value_lines)

    return name + ' = ' + value + ","

def get_name(string):
    """
    Tries to return the last name contained in a string.

    In fact returns the text before any comma in 'string', whith
    spaces removed. If comma not found, get longest word in 'string'

    Behaviour inherited from old GET_NAME function defined as UFD in
    old BibFormat. We need to return the same value, to keep back
    compatibility with already generated BibTeX records.

    Eg: get_name("سtlund, عvind B") returns "سtlund".
    """
    names = string.split(',')

    if len(names) == 1:
        #Comma not found.
        #Split around any space
        longest_name = ""
        words = string.split()
        for word in words:
            if len(word) > len(longest_name):
                longest_name = word
        return longest_name
    else:
        return names[0].replace(" ", "")


def get_year(date, default=""):
    """
    Returns the year from a textual date retrieved from a record

    The returned value is a 4 digits string.
    If year cannot be found, returns 'default'
    Returns first value found.

    @param date: the textual date to retrieve the year from
    @param default: a default value to return if year not fount
    """
    import re
    year_pattern = re.compile(r'\d\d\d\d')
    result = year_pattern.search(date)
    if result is not None:
        return result.group()

    return default

def get_month(date, ln=CFG_SITE_LANG, default=""):
    """
    Returns the month from a textual date retrieved from a record

    The returned value is the 3 letters short month name in language 'ln'
    If year cannot be found, returns 'default'

    @param date: the textual date to retrieve the month from
    @param default: a default value to return if month not found
    """
    import re
    from invenio.dateutils import get_i18n_month_name
    from invenio.messages import language_list_long

    #Look for textual month like "Jan" or "sep" or "November" or "novem"
    #Limit to CFG_SITE_LANG as language first (most probable date)
    #Look for short months. Also matches for long months
    short_months = [get_i18n_month_name(month).lower()
                    for month in range(1, 13)] # ["jan","feb","mar",...]
    short_months_pattern = re.compile(r'('+r'|'.join(short_months)+r')',
                                      re.IGNORECASE) # (jan|feb|mar|...)
    result = short_months_pattern.search(date)
    if result is not None:
        try:
            month_nb = short_months.index(result.group().lower()) + 1
            return get_i18n_month_name(month_nb, "short", ln)
        except:
            pass

    #Look for month specified as number in the form 2004/03/08 or 17 02 2004
    #(always take second group of 2 or 1 digits separated by spaces or - etc.)
    month_pattern = re.compile(r'\d([\s]|[-/.,])+(?P<month>(\d){1,2})')
    result = month_pattern.search(date)
    if result is not None:
        try:
            month_nb = int(result.group("month"))
            return get_i18n_month_name(month_nb, "short", ln)
        except:
            pass

    #Look for textual month like "Jan" or "sep" or "November" or "novem"
    #Look for the month in each language

    #Retrieve ['en', 'fr', 'de', ...]
    language_list_short = [x[0]
                           for x in language_list_long()]
    for lang in language_list_short: #For each language
        #Look for short months. Also matches for long months
        short_months = [get_i18n_month_name(month, "short", lang).lower()
                        for month in range(1, 13)] # ["jan","feb","mar",...]
        short_months_pattern = re.compile(r'('+r'|'.join(short_months)+r')',
                                          re.IGNORECASE) # (jan|feb|mar|...)
        result = short_months_pattern.search(date)
        if result is not None:
            try:
                month_nb = short_months.index(result.group().lower()) + 1
                return get_i18n_month_name(month_nb, "short", ln)
            except:
                pass

    return default


