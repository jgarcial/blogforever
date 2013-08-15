# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2006, 2007, 2008, 2009, 2010, 2011 CERN.
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
"""BibFormat element - Converts html based records to latex template.
"""

from invenio.config import \
    CFG_SITE_LANG
from invenio.bibformat_pdf_with_latex_template_config import \
    CFG_BIBFORMAT_CSS_FILES, \
    CFG_BIBFORMAT_LATEX_HEADER, \
    CFG_BIBFORMAT_LATEX_PAGE_SETTINGS, \
    CFG_BIBFORMAT_LATEX_BEGIN_DOC, \
    CFG_BIBFORMAT_LATEX_END_DOC, \
    CFG_BIBFORMAT_LATEX_PACKAGES, \
    CFG_BIBFORMAT_LATEX_SPECIAL_CHARS_EQUIVALANCES, \
    CFG_BIBFORMAT_LATEX_SPECIAL_CHARS_REGEX, \
    CFG_BIBFORMAT_LATEX_MATH_FORMULAS, \
    CFG_BIBFORMAT_LATEX_ONLY_TEXT

from invenio.bibformat_pdf_with_latex_template import \
    CssParser, \
    LatexConverter, \
    PdfWithLatexTemplateHtmlParser
    
from invenio.search_engine import get_creation_date
import datetime

def format_element(bfo, max_authors_len="60"):
    """
    Returns a latex template code inluding bibtex related fields of the record and
    record body in field 520.

    @param max_authors_len: the maximum number of chars of the author name line.
        Warning: If it is more than 60, new line is used after each author name.
    """
    try:
        max_authors_len = int(max_authors_len)
    except:
        max_authors_len = 60
        
    rec_id = bfo.control_field('001')
    
    out =   CFG_BIBFORMAT_LATEX_HEADER + \
            CFG_BIBFORMAT_LATEX_PAGE_SETTINGS + \
            CFG_BIBFORMAT_LATEX_PACKAGES + \
            CFG_BIBFORMAT_LATEX_BEGIN_DOC

    #Print title
    import invenio.bibformat_elements.bfe_title as bfe_title
    title = bfe_title.format_element(bfo=bfo, separator = ". ")
    out += format_latex_field("title", title)

    #Print authors
    #If author cannot be found, print a field key=rec_id
    author_list = bfo.fields('100__a')
    authors = ""
    if len(author_list) == 1:
        authors = str(author_list[0])
    elif len(author_list) > 1:
        last_author = author_list.pop()
        for author in author_list:
            authors += str(author) + ", "
        authors += str(last_author)
    if authors:
        title_authors = format_latex_field("author", authors)
        if len(authors) > int(max_authors_len):
            title_authors = title_authors.replace(",", "\\\\")
        out += title_authors
    
    
    # Extract post and record creation date
    # Copied from bfe_record_date (Only date is required, not html wrappers)
    recid = bfo.control_field('001')
    try:
        posted_date = bfo.fields('269__c')[0]
        # hack
        if posted_date.find("ERROR") > -1:
            posted_date = ""
        else:
            date = datetime.datetime.strptime(posted_date, "%m/%d/%Y %I:%M:%S %p")
            posted_date = date.strftime("%Y/%m/%d")
    except:
        posted_date = ""
    
    record_creation_date = get_creation_date(recid)
    date = datetime.datetime.strptime(record_creation_date, "%Y-%m-%d")
    record_creation_date = date.strftime("%Y/%m/%d")
    
    title_date = ""
    if posted_date:
        title_date += "Posted Date: " + posted_date
    if record_creation_date:
        title_date += " \\\\ " + "Record Creation Date: " + record_creation_date
        
    out += format_latex_field("date", title_date, False)

    #add \maketitle
    out += "\n\\maketitle\n"
    record_body = bfo.fields('520__a')
#    record_body.extend(bfo.fields('520__b'))
    out += convert_record_body(record_body)
    out += CFG_BIBFORMAT_LATEX_END_DOC

    return out


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0


def format_latex_field(tag, value, apply_escape=True):
    """
    Formats a name and value to display as BibTeX field.

    @param tag -str- : latex command
    @param value -str- : text to be displayed in latex code.
    """
    
    def remove_escape_chars(match_object):
        """
        Returns latex representation of special latex chars.
        """
        return CFG_BIBFORMAT_LATEX_SPECIAL_CHARS_EQUIVALANCES[match_object.group(0)]
    
    
    def format_raw_text(content):
        math = CFG_BIBFORMAT_LATEX_MATH_FORMULAS.findall(content)
        only_text = CFG_BIBFORMAT_LATEX_ONLY_TEXT.findall(content)
        index = 0
        for elem in math:
            math[index] = elem.rstrip('$').lstrip('$')
            index += 1
        index = 0
        content = ""
        for elem in only_text:
            if not elem in math:
                if apply_escape:
                    elem = CFG_BIBFORMAT_LATEX_SPECIAL_CHARS_REGEX.sub(remove_escape_chars, elem)
            else:
                elem = '$' + elem + '$'
            content += elem
        return content
    
#    value = CFG_BIBFORMAT_LATEX_SPECIAL_CHARS_REGEX.sub(remove_escape_chars, value)
    value = format_raw_text(value)
    #format name
    tag = "\n\\" + tag
    if not value:
        return tag + '{}'
    else:
        return tag + '{' + value + '}'


def convert_record_body(body_list):
    """
    Converts html like records to latex text.

    @param body -str- : html structure of the record in string form.

    @return -str- : latex text of the given record.
    """
    body = ""
    for elem in body_list:
        body += elem
    css_parser = CssParser(css_file_list = CFG_BIBFORMAT_CSS_FILES, data = '')
    converter = LatexConverter(css_parser)
    html_parser = PdfWithLatexTemplateHtmlParser(converter)
    out = html_parser.feed(body)
    return out
