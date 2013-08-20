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
from invenio.bibformat_pdf_with_latex_template import CssParser, \
    LatexConverter, PdfWithLatexTemplateHtmlParser

from invenio.bibformat_pdf_with_latex_template_config import \
    CFG_BIBFORMAT_LATEX_HEADER, CFG_BIBFORMAT_LATEX_PACKAGES, \
    CFG_BIBFORMAT_LATEX_BEGIN_DOC, CFG_BIBFORMAT_LATEX_PAGE_SETTINGS, \
    CFG_BIBFORMAT_LATEX_END_DOC, CFG_BIBFORMAT_LATEX_MATH_FORMULAS, \
    CFG_BIBFORMAT_LATEX_ONLY_TEXT, \
    CFG_BIBFORMAT_LATEX_SPECIAL_CHARS_EQUIVALANCES, \
    CFG_BIBFORMAT_LATEX_SPECIAL_CHARS_REGEX, CFG_BIBFORMAT_CSS_FILES


def begin_document():
    """
    @return: Initialization of a latex document
    @rtype: string
    """
    return (CFG_BIBFORMAT_LATEX_HEADER +
            CFG_BIBFORMAT_LATEX_PAGE_SETTINGS +
            CFG_BIBFORMAT_LATEX_PACKAGES +
            CFG_BIBFORMAT_LATEX_BEGIN_DOC)


def end_document():
    """
    Finalization of a latex document

    @return: latex document end tag
    @rtype: str
    """
    return CFG_BIBFORMAT_LATEX_END_DOC


def remove_escape_chars(match_object):
    """
    Returns latex representation of special latex chars.
    """
    return CFG_BIBFORMAT_LATEX_SPECIAL_CHARS_EQUIVALANCES[
        match_object.group(0)]


def format_raw_text(content, apply_escape=True):
    """
    Formats given content as latex.

    @param content: The content to be formatted.
    @type content: str

    @param apply_escape:
    @type apply_escape: bool

    @return: Latex formatted content
    @type: str
    """
    math = CFG_BIBFORMAT_LATEX_MATH_FORMULAS.findall(content)
    only_text = CFG_BIBFORMAT_LATEX_ONLY_TEXT.findall(content)
    index = 0
    for elem in math:
        math[index] = elem.rstrip('$').lstrip('$')
        index += 1
    content = ""
    for elem in only_text:
        if not elem in math:
            if apply_escape:
                elem = CFG_BIBFORMAT_LATEX_SPECIAL_CHARS_REGEX.sub(
                    remove_escape_chars, elem)
        else:
            elem = '$' + elem + '$'
        content += elem
    return content


def format_latex_field(tag, value, apply_escape=True):
    """
    Formats a name and value to display as BibTeX field.

    @param tag: latex command
    @type tag: str

    @param value: text to be displayed in latex code.
    @type value: str

    @param apply_escape:
    @type apply_escape: bool

    @rtype: str
    """

    value = format_raw_text(value, apply_escape=apply_escape)
    #format name
    tag = "\n\\" + tag
    if not value:
        return tag + '{}'
    else:
        return tag + '{' + value + '}'


def html_to_latex(html):
    """
    Converts html to latex text.

    @param html:
    @type: str

    @return: latex text of the given html.
    @rtype: str
    """
    css_parser = CssParser(css_file_list=CFG_BIBFORMAT_CSS_FILES, data='')
    converter = LatexConverter(css_parser)
    html_parser = PdfWithLatexTemplateHtmlParser(converter)
    out = html_parser.feed(html)
    return out
