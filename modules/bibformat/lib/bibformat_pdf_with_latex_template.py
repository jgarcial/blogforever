# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2012, 2013 CERN.
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
"""
Converts html based records to pdf written latex template.
PdfWithLatexTemplateHtmlParser class extracts html tags and data which are
mapped with their possible latex representations within LatexConverter class.
If css style is provided, for each html tag, class, id or possible css
selectors, related latex style is also applied.
"""
from flask import g
import re
import copy
from operator import itemgetter
from HTMLParser import HTMLParser

from invenio.textutils import get_random_string
from flask import session
from invenio.bibformat_pdf_with_latex_template_config import \
    CFG_BIBFORMAT_LATEX_REPRESENTATION_OF_HTML_TAGS, \
    CFG_BIBFORMAT_LATEX_REPRESENTATION_OF_CSS_RULES, \
    CFG_BIBFORMAT_CSS_PARSER_REGULAR_EXPRESSIONS, \
    CFG_BIBFORMAT_LATEX_TEMP_DIR, \
    CFG_BIBFORMAT_LATEX_ALIGNMENTS, \
    CFG_BIBFORMAT_LATEX_COMMANDS, \
    CFG_BIBFORMAT_LATEX_DEFAULT_FONT_SIZE, \
    CFG_BIBFORMAT_LATEX_CSS_SELECTORS, \
    CFG_BIBFORMAT_HTML_SPECIAL_CHARS_BY_NUM, \
    CFG_BIBFORMAT_HTML_SPECIAL_CHARS_BY_NAME, \
    CFG_BIBFORMAT_LATEX_SPECIAL_CHARS_REGEX, \
    CFG_BIBFORMAT_LATEX_SPECIAL_CHARS_EQUIVALANCES, \
    CFG_BIBFORMAT_LATEX_STYLE_FIRST_TAGS, \
    CFG_BIBFORMAT_LATEX_NON_END_TAGS, \
    CFG_BIBFORMAT_MATHJAX_ENABLED, \
    CFG_BIBFORMAT_MATHJAX_DELIMITERS, \
    CFG_BIBFORMAT_LATEX_SPECIAL_CHARS_LIST, \
    CFG_BIBFORMAT_CSS_SELECTOR_COMPONENTS, \
    CFG_BIBFORMAT_LATEX_MATH_FORMULAS, \
    CFG_BIBFORMAT_LATEX_ONLY_TEXT, \
    CFG_BIBFORMAT_LATEX_EXCEPTIONAL_COMMANDS, \
    CFG_BIBFORMAT_LATEX_PX_CM_SCALE, \
    CFG_BIBFORMAT_LATEX_A4_SCALE, \
    CFG_BIBFORMAT_LATEX_DEFAULT_IMG_SCALE, \
    CFG_BIBFORMAT_LATEX_LONG_WORDS, \
    CFG_BIBFORMAT_LATEX_COMMAND_CONSTRAINTS

from invenio.latexutils_image import get_image_path


class PdfWithLatexTemplateHtmlParser(HTMLParser):
    """
    Html parser inherited from HTMLParser. Some methods are overwritten to
    enable conversion.
    """
    __converter = None

    # To keep track of tags without end tag like <hr>, <br>.
    __former_tag = None

    def __init__(self, converter=None):
        """
        @param converter: The object handling
            translation between html based data and latex based data. Maps
            html tags with their latex equivalences and applies css style.
        @type converter: L{LatexConverter}
        """
        HTMLParser.__init__(self)
        self.reset()
        if not converter:
            converter = LatexConverter()
        self.__converter = converter

    def handle_starttag(self, tag, attrs):
        # Check if the former tag is ended or not.
        if (self.__former_tag and
                    self.__former_tag in CFG_BIBFORMAT_LATEX_NON_END_TAGS):
            self.handle_endtag(self.__former_tag)

        # Flush content buffer before activating new html element.
        self.__converter.handle_raw_data()

        # If active latex environment does not allow this html tag, replace
        # this with formerly defined one.
        if (self.__converter.active_environment in
                CFG_BIBFORMAT_LATEX_COMMAND_CONSTRAINTS and
                    tag in CFG_BIBFORMAT_LATEX_COMMAND_CONSTRAINTS
                [self.__converter.active_environment]):
            tag = (CFG_BIBFORMAT_LATEX_COMMAND_CONSTRAINTS
                   [self.__converter.active_environment][tag])

        # If tag has constraints, set this as new environment.
        if tag in CFG_BIBFORMAT_LATEX_COMMAND_CONSTRAINTS:
            (self.__converter.active_environment_stack
             .append(self.__converter.active_environment))
            self.__converter.active_environment = tag

        style_selectors = []
        dattrs = list_to_dict(attrs)

        if 'id' in dattrs:
            style_selectors.append('#' + dattrs['id'])
            style_selectors.append(tag + '#' + dattrs['id'])
        if 'class' in dattrs:
            for char in dattrs['class'].split("  "):
                style_selectors.append('.' + char)
                style_selectors.append(tag + '.' + char)
        style_selectors.append(tag)
        self.__converter.css_selectors.append(style_selectors)

        # Initialize converter object for new coming html tag.
        self.__converter.active_style = {}
        self.__converter.tag_id += 1
        self.__converter.active_tag = tag
        self.__converter.attributes = dattrs
        if tag in CFG_BIBFORMAT_LATEX_STYLE_FIRST_TAGS:
            # Push tag before style addition.
            self.__converter.push_into_end_stack(tag)
            # Add style.
            self.__converter.extract_style()
            self.__converter.add_style()
            self.__converter.trivial_tag_start(tag, push_end_value=False)
        else:
            if 'img' == tag:
                self.__converter.img_start(tag)
            elif 'table' == tag:
                self.__converter.table_start(tag)
            elif 'td' == tag or 'th' == tag:
                self.__converter.table_cell_start(tag)
            elif 'tr' == tag:
                self.__converter.table_row_start(tag)
            elif 'a' == tag:
                self.__converter.anchor_start(tag)
            elif 'font' == tag:
                self.__converter.font_start(tag)
            elif 'br' == tag:
                self.__converter.br_start(tag)
            else:
                self.__converter.trivial_tag_start(tag)

            # Add style.
            self.__converter.extract_style()
            self.__converter.add_style()

            self.__former_tag = tag

    def handle_endtag(self, tag):
        # Set former latex environment for html tags having constraints.
        if (tag != self.__converter.active_environment and
                    self.__converter.active_environment in
                    CFG_BIBFORMAT_LATEX_COMMAND_CONSTRAINTS and
                    tag in CFG_BIBFORMAT_LATEX_COMMAND_CONSTRAINTS
                [self.__converter.active_environment]):
            tag = (CFG_BIBFORMAT_LATEX_COMMAND_CONSTRAINTS
                   [self.__converter.active_environment][tag])

        if tag in CFG_BIBFORMAT_LATEX_COMMAND_CONSTRAINTS:
            self.__converter.active_environment = (self.__converter
                                                   .active_environment_stack
                                                   .pop())

        # Flush content buffer before leaving the html element.
        self.__converter.handle_raw_data()
        # If there are not any unmatched html tags, no problem occurs.
        if self.__converter.css_selectors:
            self.__converter.css_selectors.pop()
        if self.__converter.css_rule_stack:
            self.__converter.css_rule_stack.pop()
        self.__converter.active_style_selectors = {}
        # end tag stack must be traversed, converter will handle this.
        self.__converter.tag_end(tag)
        self.__former_tag = None

    def handle_data(self, data):
        if not self.__converter.active_tag in ['script', 'iframe']:
            left = right = None
            if data:
                left = data[0]
                right = data[-1]

            data = data.strip()
            data = re.sub(r'( |\n|\t)+', ' ', data)
            if left == ' ':
                self.__converter.html_content_buffer += ' '
            self.__converter.html_content_buffer += data
            if right == ' ':
                self.__converter.html_content_buffer += ' '

    def handle_charref(self, name):
        if name.startswith('x'):
            u_char = unichr(int(name[1:], 16))
        else:
            u_char = unichr(int(name))
        self.__converter.handle_raw_data(u_char)

    def handle_entityref(self, name):
        self.__converter.handle_raw_data(name, char_by_name=True)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def feed(self, data):
        if not isinstance(data, unicode):
            data = data.decode("utf-8")
        self.rawdata = data
        self.goahead(0)
        self.__converter.handle_raw_data()
        self.__converter.flush_end_stack()
        out = self.__converter.get_latex_text()
        writ = open('/tmp/latexout2', 'w')
        writ.write(out)
        writ.close()
        return out


class LatexConverter:
    """
    Converts html to latex. Possible latex commands are mapped from
    dictionaries in bibformat_pdf_with_latex_config module. Only a few html
    tags are needed extra effort. The methods defined to handle them are
    called from HtmlParser class.
    """
    # The css tree ,self.css_selectors, in parsed html element's order,
    # contains simple selector identifiers and already found selectors to
    # prevent repetition (e.g., .class_name, #id, tag_name#id, tag_name,
    # tag_name.class_name, ['img', '>', '#id']).
    css_selectors = []

    # Keeps css rules for each html element until its end tag is encountered so
    # that style can be inherited from parents.
    css_rule_stack = []

    # Predefined dictionaries for code mapping.
    __html_latex_mappings = CFG_BIBFORMAT_LATEX_REPRESENTATION_OF_HTML_TAGS
    __css_latex_mappings = CFG_BIBFORMAT_LATEX_REPRESENTATION_OF_CSS_RULES
    __latex_alignments = CFG_BIBFORMAT_LATEX_ALIGNMENTS
    __latex_commands = CFG_BIBFORMAT_LATEX_COMMANDS
    __special_chars_by_number = CFG_BIBFORMAT_HTML_SPECIAL_CHARS_BY_NUM
    __special_chars_by_name = CFG_BIBFORMAT_HTML_SPECIAL_CHARS_BY_NAME

    # Holds latex code.
    __tex_buffer = ""
    # Holds definitions like color.
    __tex_define_section = ""

    # Accumulates content of the active html tag.
    html_content_buffer = ""

    # Holds end tags of latex commands. There are two types of end tags. One
    # for html tags and the other is for css rules. When an end html tag is
    # encountered, stack is popped until that tag.
    __end_stack = []

    # If css selectors of an html element are already found, there is no need
    # to search for those again. Once found , save them and use later.
    active_style_selectors = {}
    # Css rules for active tag.
    active_style = {}
    # In latex some commands cause errors if they are used after some specific
    # commands.
    # To prevent this, "active_environment" stack holds the active tags.
    active_environment_stack = []
    # Current environment (Last element of the active_environment_stack)
    active_environment = None
    # The tag name that is handled currently.
    active_tag = ""
    # Attributes of the active html element.
    attributes = None

    # Keeps active latex commands as dictionaries. Each dictionary holds
    # trouble maker latex command's start and end values.
    __troublesome_commands = {}

    # To keep track of last applied latex end value. Since new line after an
    # environment's end tag causes latex errors, we need to check former
    # command's end. If the last applied latex end value is in the form  of
    # \end{.+}, then set value True.
    __is_former_new_environment = False

    # List of defined colors. To prevent redefine of a color in latex file.
    __defined_colors = []

    # For table related "table", "td", "th", "tr" tags. In case there is
    # another table inside the table stacks are used. Necessary parameters are
    # pushed into and popped from stack in table_start and table_end methods.
    # There is also a separate buffer for table tag.
    __tex_table_buffer = ""
    __number_of_tables = 0
    __tabular_definition = []
    __is_first_line = True
    __is_first_cell = True
    __has_border = False
    __table_column_size = 0
    __numb_of_cols = 0
    __is_rowspan = False
    __header_line = ""
    __rowspan_params = []
    # Keeps rowspan and colspan attributes related data.
    __multicolumn_params = {
        'col_num': 1,
        'lb': '',
        'rb': '',
        'pos': __latex_alignments['default']
    }
    # For nested tables. Whenever a new table is encountered push current
    # parameters.
    __table_stack = []

    def __init__(self, css_parser=None):
        """
        Both css_rules and css_rules_index are return of CssParser.parse. They
        are used for mapping style rules. They are described in details in
        CssParser.parse method's docstring.

        @param css_parser: The css parser object that
            extracts css style rules from file or string.
        @type css_parser: L{CssParser}
        """
        if not css_parser:
            css_parser = CssParser()

        self.__css_parser = css_parser
        (self.__css_rules, self.__css_rules_index) = self.__css_parser.parse()

        # Check for dependencies and construct regex for latex special chars.
        if CFG_BIBFORMAT_MATHJAX_ENABLED:
            if (CFG_BIBFORMAT_MATHJAX_DELIMITERS in
                    CFG_BIBFORMAT_LATEX_SPECIAL_CHARS_LIST):
                (CFG_BIBFORMAT_LATEX_SPECIAL_CHARS_LIST
                 .remove(CFG_BIBFORMAT_MATHJAX_DELIMITERS))
            regex_str = (re
                         .escape(''
            .join(CFG_BIBFORMAT_LATEX_SPECIAL_CHARS_LIST))
            )
            regex_str = '[' + regex_str + ']'
            global CFG_BIBFORMAT_LATEX_SPECIAL_CHARS_REGEX
            CFG_BIBFORMAT_LATEX_SPECIAL_CHARS_REGEX = re.compile(regex_str)

        # tag_id keeps # of html tags to provide a unique identifier for each
        # html tag.
        self.tag_id = 0
        self.__defined_colors = []
        self.__tabular_definition = []
        self.__rowspan_params = []
        self.__end_stack = []
        self.css_selectors = []
        self.css_rule_stack = []
        self.__number_of_images = 0
        self.session_id = session.sid

    def get_latex_text(self):
        """
        Returns concatenation of definitions and latex codes.
        """
        out = self.__tex_define_section + "\n" + self.__tex_buffer
        if isinstance(out, unicode):
            out = out.encode("utf-8")
        return out

    def __handle_latex_commands(self, start_data, end_data=None):
        """
        Adds given data to one of the buffers holding latex template according
        to state of html tags.

        @param start_data: Content to be added latex code buffers.
        @type start_data: str
        @param end_data: Dictionary holding type (style or related html
            tag's name) and closing latex command which is appended to latex
            code buffers when the closing html tag is encountered.
        @type end_data: dict
        """
        if start_data:
            # If the start tag is a troubled latex command, it is not inserted
            # into latex code buffers.
            if not start_data in CFG_BIBFORMAT_LATEX_EXCEPTIONAL_COMMANDS:
                if self.__number_of_tables:
                    self.__tex_table_buffer += start_data
                else:
                    self.__tex_buffer += start_data
            elif end_data:
                except_command = {
                    'start': start_data,
                    'end': end_data['end']
                }
                identifier = end_data['type'] + "_" + str(self.tag_id)
                end_data['end'] = ''
                end_data['type'] = identifier
                self.__troublesome_commands[identifier] = except_command

        if end_data:
            self.__end_stack.append(end_data)

    def handle_raw_data(self, data=None, char_by_name=False):
        """
        Main controller for inserting html elements' content. To flush
        html_content_buffer, simply call without parameters.

        @param data: html content(text only)
        @param data: str
        @param char_by_name: If the content is like "&hellip" an html
            special character then it is mapped from dictionary with its name.
        @type char_by_name: bool
        """
        if self.html_content_buffer:
            self.__insert_raw_data(self.html_content_buffer)
            self.html_content_buffer = ""
        if data:
            self.__insert_raw_data(data, char_by_name)

    def __insert_raw_data(self, content, char_by_name=False):
        """
        Handles latex special characters, maps special html characters
        (e.g. &hellip) with their latex equivalances and adds the content to
        latex code buffer.

        @param content: html content
        @type content: str
        @param char_by_name: If the content is like "&hellip" an html
            special character then it is mapped from dictionary with its name.
        @type char_by_name: bool
        """

        def remove_escape_chars(match_object):
            """
            Returns latex representation of special latex chars.
            """
            return (CFG_BIBFORMAT_LATEX_SPECIAL_CHARS_EQUIVALANCES
                    [match_object.group(0)])

        def split_long_words(match_object):
            """
            Surrounds matched text with seqsplit latex command which
            automatically adds line breaks at the end of line.
            """
            return "\\seqsplit{" + match_object.group(0) + "}"

        # If the tag is <pre>, then leave its content.
        # Otherwise, find latex special characters and escape them if they are
        # not in a latex math formula.
        if self.active_tag != "pre":
            math = CFG_BIBFORMAT_LATEX_MATH_FORMULAS.findall(content)
            only_text = CFG_BIBFORMAT_LATEX_ONLY_TEXT.findall(content)
            index = 0
            for elem in math:
                math[index] = elem.rstrip('$').lstrip('$')
                index += 1
            content = ""
            for elem in only_text:
                if not elem in math:
                    elem = (CFG_BIBFORMAT_LATEX_SPECIAL_CHARS_REGEX
                            .sub(remove_escape_chars, elem))
                    elem = (CFG_BIBFORMAT_LATEX_LONG_WORDS
                            .sub(split_long_words, elem))
                else:
                    elem = '$' + elem + '$'
                content += elem

        raw_data_buffer = ""
        if not char_by_name:
            raw_data_buffer += content
        else:
            try:
                raw_data_buffer += self.__special_chars_by_name[content]
            except KeyError:
                raw_data_buffer += "<<" + content + ">>"

        # If any active latex command, apply them on text.
        if raw_data_buffer.rstrip().lstrip():
            for elem in self.__troublesome_commands:
                values = self.__troublesome_commands[elem]
                raw_data_buffer = (values['start'] +
                                   raw_data_buffer +
                                   values['end'])

        self.__handle_latex_commands(raw_data_buffer)

    def trivial_tag_start(self, tag, push_end_value=True):
        """
        Handles start tags mapping of which from dictionary is enough.

        @param tag: tag name
        @type tag: str
        @param push_end_value: If style rules are applied before tag is
            handled, there is no need to push that tag's end values.
        @type push_end_value: bool
        """
        try:
            end_value = None
            if push_end_value:
                end_value = {
                    'type': tag,
                    'end': self.__html_latex_mappings[tag]['end']
                }
            (self
             .__handle_latex_commands(self
                                      .__html_latex_mappings[tag]['start'],
                                      end_value))
        except:
            # TODO
            # If there are missing tags, insert them to dictionaries.
            pass

    def tag_end(self, tag):
        """
        Pops end values from self.__end_stack until popped element's type is
        tag. Until an html tag is found, css related values are added to
        buffer. For table related elements extra effort is needed.

        @param tag: tag name
        @type tag: str
        """
        while self.__end_stack:
            stack_elem = self.__end_stack.pop()

            # To prevent new line errors in latex, check whether former latex
            # command is in the form of end{.+}.
            if tag == 'br':
                pass
            if re.search("end{.+}", stack_elem['end']):
                self.__is_former_new_environment = True
            else:
                self.__is_former_new_environment = False

            if tag == 'table':
                self.__handle_latex_commands(stack_elem['end'])
                self.table_end()
            elif tag == 'tr':
                stack_elem = self.table_row_end(tag)
                self.__handle_latex_commands(stack_elem['end'])
            else:
                self.__handle_latex_commands(stack_elem['end'])

            if stack_elem['type'] in self.__troublesome_commands:
                del self.__troublesome_commands[stack_elem['type']]

            if stack_elem['type'].startswith(tag):
                break

    def br_start(self, tag):
        """
        Applies new line only after text. Because latex causes errors if new
        line is not after text.
        """
        if not self.__is_former_new_environment:
            self.trivial_tag_start(tag)

    # Start of html <font> handler methods.
    def font_start(self, tag):
        """
        Handles font tag's attributes rather than font tag.

        @param tag: tag name
        @type tag: str
        """
        self.trivial_tag_start(tag)
        if 'size' in self.attributes:
            end_value = {
                'type': tag,
                'end': (self.__css_latex_mappings
                        ['font_tag_size']['default']['end'])
            }
            try:
                (self
                 .__handle_latex_commands(self
                                          .__css_latex_mappings
                                          ['font_tag_size']
                                          [self.attributes['size']]['start'],
                                          end_value))
            except:
                (self
                 .__handle_latex_commands(self
                                          .__css_latex_mappings
                                          ['font_tag_size']
                                          ['default']
                                          ['start'],
                                          end_value))

    # End of html <font> handler methods.

    # Start of html <a> handler methods.
    def anchor_start(self, tag):
        """
        Handles anchor tag's attributes rather than anchor tag.,

        @param tag : tag name
        @type tag: str
        """
        self.trivial_tag_start(tag)
        if 'href' in self.attributes:
            href = self.attributes['href']
            end_value = {
                'type': tag,
                'end': self.__latex_commands['href']['end']
            }
            if href.startswith('#'):
                (self
                 .__handle_latex_commands(self
                                          .__latex_commands['hyperlink']
                                          ['start'] %
                                          (href[1:]),
                                          end_value))
            else:
                (self
                 .__handle_latex_commands(self
                                          .__latex_commands['href']['start'] %
                                          (href),
                                          end_value))

        if 'name' in self.attributes:
            name = self.attributes['name']
            if name:
                end_value = {
                    'type': tag,
                    'end': self.__latex_commands['hypertarget']['end']
                }
                (self.__handle_latex_commands(self
                                              .__latex_commands['hypertarget']
                                              ['start'] % (name, ),
                                              end_value))

                # End of html <a> handler methods.

    # Start of html <img> handler methods.
    def img_start(self, tag):
        """
        Handles img tag based on parameters in config module. If
        CFG_BIBFORMAT_LATEX_USE_LOCAL_IMAGES is not set, then the image is
        downloaded from src attribute value.
        If the image extension is not supported by latex, converts image into
        specified format.

        @param tag: tag name
        @type tag: str

        """

        def scale_units(unit):
            """
            Scales html measurements for a4 paper size.
            @param unit: Measurement to be scaled.
            @type unit: str
            @return: Scaled length.
            @rtype: str
            """
            if unit[-1] == "%":
                unit = float(unit[0:-1])
                unit = str(unit / 100) + "\\textwidth"
            elif unit[-2:] == "px" or unit.isdigit():
                try:
                    unit = float(unit)
                except ValueError:
                    unit = float(unit[0:-2])
                unit = str(unit * CFG_BIBFORMAT_LATEX_PX_CM_SCALE) + "cm"
            else:
                ext = unit[-2:0]
                unit = (str(CFG_BIBFORMAT_LATEX_A4_SCALE * float(unit[0:-2])) +
                        ext)
            return unit

        self.attributes['src'] = self.attributes['src'].replace("\\", "")

        path = get_image_path(self.attributes['src'])

        if path:
            self.attributes['src'] = path

            if 'height' in self.attributes:
                height = self.attributes['height']
            else:
                height = self.__search_style_in_external_css('height')
            if 'width' in self.attributes:
                width = self.attributes['width']
            else:
                width = self.__search_style_in_external_css('width')

            include_graphics_options = ""
            if width:
                include_graphics_options += ('width=' +
                                             scale_units(width) +
                                             ', ')
            if height:
                include_graphics_options += ('height=' +
                                             scale_units(height) +
                                             ', ')
            elif not width:
                include_graphics_options += \
                    'max height=\\textheight, max width=\\textwidth, '

            include_graphics_options += 'keepaspectratio=true'
            self.__number_of_images += 1
            end_value = {
                'type': tag,
                'end': self.__html_latex_mappings[tag]['end']
            }
            format_dict = {
                'path': self.attributes['src'],
                'caption': '',
                'size_config': include_graphics_options
            }
            self.__handle_latex_commands(self.__html_latex_mappings
                                         [tag]['start'] % format_dict,
                                         end_value)
        else:
            # Skip the image.
            pass

            # End of html <img> handler methods.

    # Start of html <table> handler methods.
    def table_start(self, tag):
        """
        Handles html table start tag. Since there may be nested tables, table
        related parameters are pushed into a stack by initialize_new_table
        function at each table start.

        Since attributes of table also affects tr, td or th elements stores
        that attribute values.

        @param tag: tag name
        @type tag: str
        """

        def initialize_new_table():
            """
            Simply appends table specific parameters to self.__table_stack and
            initializes this parameters for new table.
            """
            self.__number_of_tables += 1
            # In case a table has already been encountered, push table related
            # parameters.
            self.__table_stack.append([self.__is_first_line,
                                       self.__is_first_cell,
                                       self.__has_border,
                                       self.__table_column_size,
                                       self.__numb_of_cols,
                                       self.__is_rowspan,
                                       self.__header_line,
                                       self.__rowspan_params,
                                       self.__multicolumn_params])
            self.__is_first_line = True
            self.__is_first_cell = True
            self.__has_border = False
            self.__table_column_size = 0
            self.__numb_of_cols = 0
            self.__is_rowspan = False
            self.__header_line = ""
            self.__rowspan_params = []
            self.__multicolumn_params = {
                'col_num': 1,
                'lb': '',
                'rb': '',
                'pos': self.__latex_alignments['default']
            }

        initialize_new_table()
        if 'align' in self.attributes:
            self.__handle_latex_commands(self.__html_latex_mappings['center']
                                         ['start'],
                                         {'type': 'style',
                                          'end': self.__html_latex_mappings
                                          ['center']['end']})

        if 'border' in self.attributes and self.attributes['border'] != '0':
            self.__has_border = True
            self.__multicolumn_params['lb'] = '|'
            self.__multicolumn_params['rb'] = '|'

        self.__handle_latex_commands(self.__html_latex_mappings[tag]['start'],
                                     {'type': tag,
                                      'end': self.__html_latex_mappings[tag]
                                      ['end']})

    def table_end(self):
        """
        Handles html table end tag. Loads former table's parameters before
        return.
        """
        if self.__has_border:
            tabular_cols = '{*{' + str(self.__table_column_size) + '}{|J}|}'
        else:
            tabular_cols = '{*{' + str(self.__table_column_size) + '}{J}}'

        self.__tabular_definition = ([tabular_cols, self.__header_line] +
                                     self.__tabular_definition)

        self.__number_of_tables -= 1
        if not self.__number_of_tables:
            self.__handle_latex_commands(self.__tex_table_buffer %
                                         tuple(self.__tabular_definition))
            self.__tex_table_buffer = ""
            self.__tabular_definition = []

        # Set back table parameters.
        table_params = self.__table_stack.pop()
        self.__is_first_line = table_params[0]
        self.__is_first_cell = table_params[1]
        self.__has_border = table_params[2]
        self.__table_column_size = table_params[3]
        self.__numb_of_cols = table_params[4]
        self.__is_rowspan = table_params[5]
        self.__header_line = table_params[6]
        self.__rowspan_params = table_params[7]
        self.__multicolumn_params = table_params[8]

    def table_row_start(self, tag):
        """
        Handles html tr start tag. Key value to be mapped differs according to
        border value of table. If table has border "tr_True" key, otherwise
        "tr_False" key is used.

        @param tag: tag name.
        @type tag: str
        """
        end_value = {
            'type': tag,
            'end': self.__html_latex_mappings[tag +
                                              '_' +
                                              str(self.__has_border)]['end']
        }
        self.__handle_latex_commands(None, end_value)

    def table_row_end(self, tag):
        """
        Handles html tr end tag based on attributes of table element.

        @param tag: tag name
        @type tag: str
        @return: returns own self.__end_stack element.
        @rtype: dict
        """
        if self.__table_column_size < self.__numb_of_cols:
            self.__table_column_size = self.__numb_of_cols
        if self.__is_first_line and self.__has_border:
            self.__is_first_line = False
            if self.__has_border:
                self.__header_line = (self.__latex_commands
                                      ['table_cline']['start'] %
                                      (1, str(self.__table_column_size)))

        if self.__numb_of_cols < self.__table_column_size:
            self.__multicolumn_params['col_num'] = (self.__table_column_size -
                                                    self.__numb_of_cols)
            self.__handle_latex_commands(" & " +
                                         self.__latex_commands
                                         ['table_multicolumn']['start'] %
                                         self.__multicolumn_params)
            self.__handle_latex_commands(self.__latex_commands
            ['table_multicolumn']['end'])
            self.__multicolumn_params['col_num'] = 1

        self.__numb_of_cols = 0
        self.__is_first_cell = True

        if self.__is_rowspan:
            rowspan_data = self.__rowspan_params
            rowspan_data[0] -= 1
            out = "\\\\"
            if not rowspan_data[0]:
                self.__is_rowspan = False
                out = self.__html_latex_mappings[tag +
                                                 '_' +
                                                 str(self.__has_border)]['end']
            elif self.__has_border:
                if rowspan_data[1] - 1:
                    out += (self.__latex_commands['table_cline']['start'] %
                            (1, str(rowspan_data[1] - 1)))
                if (rowspan_data[1] + rowspan_data[2] <
                        self.__table_column_size):
                    out += (self.__latex_commands['table_cline']['start'] %
                            (str(rowspan_data[1] + rowspan_data[2]),
                             str(self.__table_column_size)))
        else:
            out = self.__html_latex_mappings[tag +
                                             '_' +
                                             str(self.__has_border)]['end']

        return {
            'type': tag,
            'end': out
        }

    def table_cell_start(self, tag):
        """
        Handles html td or th start tag.

        @param tag: tag name
        @type tag: str
        """
        self.__numb_of_cols += 1
        self.__handle_latex_commands(None, {
            'type': tag,
            'end': self.__html_latex_mappings[tag]['end']
        })

        if not self.__is_first_cell:
            self.__handle_latex_commands(" & ")
        else:
            self.__is_first_cell = False

        if 'align' in self.attributes:
            self.__multicolumn_params['pos'] = (self.__latex_alignments
                                                [self.attributes['align']])

        colspan_number = 1
        start_of_colspan = self.__numb_of_cols

        if self.__is_rowspan:
            rowspan_data = self.__rowspan_params
            if rowspan_data[1] == self.__numb_of_cols:
                self.__multicolumn_params['col_num'] = rowspan_data[2]
                self.__handle_latex_commands(self
                                             .__latex_commands
                                             ['table_multicolumn']['start'] %
                                             self.__multicolumn_params)
                self.__handle_latex_commands(self
                                             .__latex_commands
                                             ['table_multicolumn']['end'] +
                                             " & ")
                self.__numb_of_cols += rowspan_data[2]

        if 'colspan' in self.attributes:
            self.__multicolumn_params['col_num'] = \
                colspan_number = self.attributes['colspan']
            self.__handle_latex_commands(self.__latex_commands
                                         ['table_multicolumn']['start'] %
                                         self.__multicolumn_params,
                                         {
                                             'type': 'table_multicolumn',
                                             'end': self.__latex_commands
                                             ['table_multicolumn']['end']
                                         })
            self.__numb_of_cols += int(self.attributes['colspan']) - 1

        elif 'align' in self.attributes:
            self.__handle_latex_commands(self.__latex_commands
                                         ['table_multicolumn']['start'] %
                                         self.__multicolumn_params,
                                         {
                                             'type': 'table_multicolumn',
                                             'end': self.__latex_commands
                                             ['table_multicolumn']['end']})

        if 'rowspan' in self.attributes:
            self.__is_rowspan = True
            self.__rowspan_params = [int(self.attributes['rowspan']),
                                     start_of_colspan,
                                     int(colspan_number)]
            params = {
                'row_num': self.attributes['rowspan'],
                'width': '*'
            }
            self.__handle_latex_commands(self.__latex_commands
                                         ['table_multirow']['start'] % params,
                                         {
                                             'type': 'table_multirow',
                                             'end': self.__latex_commands
                                             ['table_multirow']['end']
                                         })

        self.__handle_latex_commands(self.__html_latex_mappings[tag]['start'])
        # Set back to default values
        self.__multicolumn_params['col_num'] = 1
        self.__multicolumn_params['pos'] = self.__latex_alignments['default']

        # End of html <table> handler methods.

    def flush_end_stack(self):
        """
        If there is not any problem with the html content, all html tags is
        successfully ended. If there are any element for style rules, pops them
        and adds 'end' values to latex text.
        """
        while self.__end_stack:
            stack_elem = self.__end_stack.pop()
            self.__handle_latex_commands(stack_elem['end'])

    ## Style related methods.
    def add_style(self):
        """
        Adds style related latex codes based on current tag's css rules. Most
        of the css declarations are mapped from dictionary. However, some needs
        extra effort (e.g., font-size, color, border, etc.)
        """

        def interpret_rule(rule):
            """
            Modifies rule name based on options since some tags and style rules
            cause trouble.

            @param rule: rule name to be checked.
            @type rule: str
            """
            # Default values
            rule_name = rule
            status = self.active_style[rule]['status']
            rule_value = self.active_style[rule]['value']

            if self.active_tag == "hr":
                if rule == "background-color":
                    rule_name = "color"
                if rule == "color":
                    status = False   # Only background-color is enough.
            # TODO
            # The \colorbox command causes problems.
            elif rule == "background-color":
                status = False

            return rule_name, status, rule_value

        for rule in self.active_style:
            (rule, status, rule_val) = interpret_rule(rule)
            if status:
                if rule == 'font-size':
                    if rule_val.endswith('%'):
                        size = (CFG_BIBFORMAT_LATEX_DEFAULT_FONT_SIZE *
                                int(float(rule_val[0:-1])) / 100)
                        params = (size, size * 1.2)
                    elif rule_val.endswith(('px', 'pt')):
                        size = int(float(rule_val[0:-2]))
                        params = (size, size * 1.2)
                    else:
                        try:
                            size = int(float(rule_val))
                            params = (size, size * 1.2)
                        except:
                            size = CFG_BIBFORMAT_LATEX_DEFAULT_FONT_SIZE
                            params = (size, size * 1.2)
                    latex_commands = copy.deepcopy(self.__css_latex_mappings
                    [rule]['variable'])
                    latex_commands['start'] = (latex_commands['start'] %
                                               params)

                elif rule == 'color' or rule == 'background-color':
                    color_name = rule_val[1:]
                    if not color_name in self.__defined_colors:
                        # if color name is not specified clearly e.g. red,
                        # yellow, then define new color.
                        if rule_val.startswith("#"):
                            color_type = "HTML"
                            color_value = rule_val[1:]
                            if len(rule_val) == 4:          # 3-digit hex
                                color_value = (rule_val[1] +
                                               rule_val[1] +
                                               rule_val[2] +
                                               rule_val[2] +
                                               rule_val[3] +
                                               rule_val[3])
                        elif rule_val.startswith('rgb'):
                            color_type = 'RGB'
                            color_values = re.findall("[\d.%]+", rule_val)
                            color_value = ""
                            for val in color_values:
                                if val.endswith('%'):
                                    color_value += (str(float(val[:-1]) / 100)
                                                    + ", ")
                                else:
                                    color_value += val + ", "
                            color_value = color_value[:-2]
                            color_name = 'gb(' + color_value + ')'

                        if (rule_val.startswith("#") or
                                rule_val.startswith('rgb')):
                            if not color_name in self.__defined_colors:
                                # Define new color.
                                color_params = {
                                    'color_name': color_name,
                                    'type': color_type,
                                    'val': color_value
                                }
                                self.__tex_define_section += (self.
                                                              __latex_commands
                                                              ['definecolor']
                                                              ['start'] %
                                                              color_params)
                                self.__defined_colors.append(color_name)
                        else:
                            color_name = rule_val.capitalize()

                    latex_commands = copy.deepcopy(self.__css_latex_mappings
                    [rule]['defined'])
                    latex_commands['start'] = (latex_commands['start'] %
                                               {'val': color_name})

                elif rule == 'border' and self.active_tag == 'img':
                # TODO
                # (width, t, color) can be used with a package.
                # (width, t, color) = re.findall("[\w#]+", rule_val)
                    latex_commands = None
                else:
                    try:
                        latex_commands = (self.__css_latex_mappings[rule]
                                          [rule_val])
                    except KeyError:
                        latex_commands = None
                        # TODO
                        # If there are missing declarations in dictionary,
                        # handle!

                if latex_commands:
                    self.__handle_latex_commands(latex_commands['start'],
                                                 {
                                                     'type': 'style',
                                                     'end': latex_commands
                                                     ['end']
                                                 })

                    self.active_style[rule]['status'] = 0

    def __search_style_in_external_css(self, key):
        """
        In all possible selectors' css rules, searches given property.

        @param key: Property to be looked for e.g. "width", "font-size".
        @type key: str
        @return: If a css rule is matched returns its value. Otherwise
            returns None.
        """
        if not self.active_style:
            self.extract_style()
        if key in self.active_style:
            return self.active_style[key]['value']
        else:
            return None

    def extract_style(self):
        """
        Finds all possible css declarations and adds to self.active_style.
        Parents' css rules can also be accessible. If the html element owns
        inline style rules, they have top priority and may override inherited
        rules.
        If a css rule is already applied, there is no need to use it again. In
        that case, set "status" value to False.
        self.active_style[rule]['status'] has 3 kind of values.
            * 0 or False stands for already used or not applicable.
            * 1 stands for active and applicable.
            * 2 stands for inline style rule which can not be overridden.
        """
        if not self.active_style:
            # By default directly inherit parent's style rules and as new rules
            # are defined, simply add or override them.
            try:
                self.active_style = copy.deepcopy(self.css_rule_stack[-1])
            except IndexError:
                self.active_style = {}

            # If there are inline style rules for the active html tag, parse
            # and give them top priority.
            if 'style' in self.attributes:
                inline_rules = (self.__css_parser
                                .parse_inline_style(self.attributes['style']))
                for elem in inline_rules:
                    self.active_style[elem] = {}
                    self.active_style[elem]['value'] = inline_rules[elem]
                    self.active_style[elem]['status'] = 2

            # If the selectors are already defined for the current tag, simply
            # use them. Otherwise, it is need to look for selectors.
            if not self.active_tag in self.active_style_selectors:
                selectors = self.find_style_selectors()
            else:
                selectors = self.active_style_selectors[self.active_tag]

            for elem in selectors:
                if elem in self.__css_rules:
                    rules = self.__css_rules[elem]
                    for rule in rules.keys():
                        if not rule in self.active_style:
                            self.active_style[rule] = {}
                            self.active_style[rule]['value'] = rules[rule]
                            self.active_style[rule]['status'] = 1
                        elif (self.active_style[rule]['status'] != 2 and
                                      self.active_style[rule]['value'] !=
                                      rules[rule]):
                            self.active_style[rule]['value'] = rules[rule]
                            self.active_style[rule]['status'] = 1
                    break

            # Add a dummy entry to disable style check for unsupported
            # declarations.
            self.active_style["dummy"] = {}
            self.active_style["dummy"]['status'] = 0
            self.active_style["dummy"]['value'] = None

            # Add current element's style rules to stack for its children.
            self.css_rule_stack.append(self.active_style)

    def find_style_selectors(self):
        """
        Checks current html element's parents and their ids, class names to
        construct css selectors possibly containing more than one identifier
        (e.g., ".class_name > #id", "div div img", "div.class_name > p", etc.)

        Uses self.__css_rules_index which is constructed by CssParser.parse
        method.

        @return: list of css selector names.
        @rtype: list
        """

        def calculate_precedence(selector, score):
            """
            Extracts a css selector piece into its components. For example,
            "tag.class_name" -> [tag, .class_name]. And then based on browsers'
            selector precedence rules, scores each selector.
                (a,b,c,d)
                * Element, Pseudo Element: d = 1 – (0,0,0,1)
                * Class, Pseudo class, Attribute: c = 1 – (0,0,1,0)
                * Id: b = 1 – (0,1,0,0)
                * Inline Style: a = 1 – (1,0,0,0)
            @param selector : Css selector to be extracted into.
            @type selector: str
            @param score: Score accumulator for a css selector in the
                form of (a,b,c,d).
            @type score: list
            """
            components = (CFG_BIBFORMAT_CSS_SELECTOR_COMPONENTS
                          .findall(selector))
            for elem in components:
                if elem.startswith('#'):
                    score[1] += 1
                elif elem.startswith('.'):
                    score[2] += 1
                elif elem[0].isalpha():
                    score[3] += 1

        def prepare_selector_string(selector_components):
            """
            Simply concatenates list elements in reverse order.

            @param selector_components: List containing identifiers and
            operators connecting them in reverse order (e.g., ['>', '#id']).
            @type selector_components: list

            @return: Returns a tuple containing string of css selector
            (e.g., "#id > ") and precedence score of the selector.
            @rtype: (str, list)
            """
            out = ""
            score = [0, 0, 0, 0]
            length = len(selector_components) - 1
            while length >= 0:
                out += selector_components[length]
                if not length % 2:
                    calculate_precedence(selector_components[length], score)
                length -= 1
            return score, out

        def walk_on_css_tree(index_css_selectors, selector):
            """
            A recursive method for parsing the list containing identifiers.
            The css tree ,self.css_selectors, in parsed html element's order,
            contains simple selector identifiers and already found selectors to
            prevent repetition (e.g., .class_name, #id, tag_name#id, tag_name,
            tag_name.class_name, ['img', '>', '#id']).

            @param index_css_selectors: Current position in the css tree.
            @type index_css_selectors: int

            @param selector: The list containing identifiers.
            @type selector: list

            @return: If selector can be constructed from css tree,
                returns True. Otherwise, returns False.
            @rtype: bool
            """

            if not selector:
                return True
            elif index_css_selectors < 0:
                return False

            # If the selector is already in css tree, there is no need to look
            # forward.
            if selector[1:] in self.css_selectors[index_css_selectors - 1]:
                return True

            operator = selector[0]
            if operator == " ":
                # Search through list to find container
                while True:
                    try:
                        if (selector[1] in
                                self.css_selectors[index_css_selectors - 1]):
                            # Keep looking next for selector element.
                            return walk_on_css_tree(index_css_selectors - 1,
                                                    selector[2:])
                    except:
                        return False
                    index_css_selectors -= 1

            elif operator.rstrip().lstrip() == ">":
                # Just Look one level up
                try:
                    parents_selectors = (self.css_selectors
                                         [index_css_selectors - 1])
                    if selector[1] in parents_selectors:
                        # Keep looking next for selector element.
                        return walk_on_css_tree(index_css_selectors - 1,
                                                selector[2:])
                    else:
                        return False
                except:
                    return False
            elif operator.rstrip().lstrip() == "+":
                # TODO
                # !Out of case, need siblings!
                pass
            elif operator.rstrip().lstrip() == "~":
                # TODO
                # !Out of case, need siblings!
                pass
            else:
                # TODO
                # Add to CFG_BIBFORMAT_LATEX_CSS_SELECTORS
                pass

        possible_selectors = []
        active_css_selectors = self.css_selectors[-1]
        for elem in active_css_selectors:
            if isinstance(elem, type([])) and elem in self.__css_rules_index:
                indexed_selectors = self.__css_rules_index[elem]
                for selector in indexed_selectors:
                    if walk_on_css_tree(len(self.css_selectors) - 1, selector):
                        tmp_selector = [elem] + selector
                        (possible_selectors
                         .append(prepare_selector_string(tmp_selector)))
                        # Add selector to css tree.
                        if len(tmp_selector) > 1:
                            active_css_selectors.append(tmp_selector)

        possible_selectors.sort(key=itemgetter(0), reverse=True)
        sorted_selectors = [elem[1] for elem in possible_selectors]
        self.active_style_selectors[self.active_tag] = sorted_selectors
        return sorted_selectors

    def push_into_end_stack(self, tag):
        """
        Push data to self.__end_stack.

        @param tag: Tag name.
        @type tag: str
        """
        end_value = {
            'type': tag,
            'end': self.__html_latex_mappings[tag]['end']
        }
        self.__handle_latex_commands(None, end_value)

    def pop_from_end_stack(self):
        """
        Pop data from self.__end_stack.
        """
        return self.__end_stack.pop()


class CssParser:
    """
    Parses the css rules and converts into dictionary.
    """
    # Extracts css rules seperately from css file content. Returns
    # "#c1 .c2 {...}" for example.
    __css_block = (CFG_BIBFORMAT_CSS_PARSER_REGULAR_EXPRESSIONS
                   ['extract_css_block'])

    # Gets class and tag names from whole rule. (i.e. #c1 .c2{..} will return
    # "#c1 .c2"
    __extract_selectors = (CFG_BIBFORMAT_CSS_PARSER_REGULAR_EXPRESSIONS
                           ['extract_selectors'])

    # Extracts each css rule from block. i.e. {color:red; font-style: arial}
    # will be extracted as "color:red" and "font-style:arial".
    __extract_rules = (CFG_BIBFORMAT_CSS_PARSER_REGULAR_EXPRESSIONS
                       ['extract_rules'])

    def __init__(self, css_file_list=None, data=""):
        """
        If a file list is given, the data to be parsed is read from that files.
        Feeding the data in string form is another alternative.

        @param css_file_list: Contains paths of the css files.
        @type css_file_list: list
        @param data: Whole css file or basic css rules to be parsed.
        @type data: str
        """
        self.__file_list = css_file_list
        self.data = data
        self.css_file_output = {}
        self.css_index = {}
        self.__css_file_content = ""

        if css_file_list:
            self.__read_css_files()

        self.__tags_reg_exp = "[^"
        self.__marks_reg_exp = "["
        for elem in CFG_BIBFORMAT_LATEX_CSS_SELECTORS:
            self.__tags_reg_exp += elem
            self.__marks_reg_exp += elem
        self.__tags_reg_exp += "]+"
        self.__marks_reg_exp += "]+"

    def parse(self):
        """
        Finds each css declaration and selectors of css rules.
        @return: First element is the css rules in dict format. The
            second element is another dict that defines selectors. If there
            are css rules like:
            .class_name img {
                width:200px;
                border:1px solid #999999;
            }
            #id > img{
                margin: 2px;
            }

            return tuple will look like this:
            (
                {
                    '#id img': {'margin': '2px'},
                    '.class_name img':  {
                                        'width': '200px',
                                        'border': '1px solid #999999'
                                        }
                },
                {
                    'img': [[' ', '.class_name'], ['>', '#id']]
                }
            )
            The second element is used for finding css selectors. If an "img"
            element is inside an element with class name "class_name" or its
            parent has id "id" then we can apply the rule with selector
            ".class_name img" or "#id > img".
        @rtype: tuple
        """
        ind = 0
        length = len(self.data)
        while ind < length:
            rule_match = self.__css_block.search(self.data, ind)
            if rule_match:
                ind = rule_match.end()
                rule_block = rule_match.group()
                owners_match = self.__extract_selectors.match(rule_block)

                rule_start_ind = owners_match.end()
                rule_block = rule_block[rule_start_ind + 1:]

                # TODO
                # Not work for all cases. Only basic connectors are handled.
                # For more option, edit walk_on_css_tree function under
                # LatexConverter.find_style_selectors and
                # CFG_BIBFORMAT_CSS_PARSER_REGULAR_EXPRESSIONS
                # ['parse_selectors']

                # Remove unnecessary whitespaces.
                owners = re.sub(r'[\s] +'
                                r'', ' ', owners_match.group()).split(", ")
                for owner in owners:
                    owner = owner.rstrip().lstrip()

                    marks = re.findall(self.__marks_reg_exp, owner)
                    names = re.findall(self.__tags_reg_exp, owner)
                    marks.reverse()
                    names.reverse()
                    merged_list = [None] * (len(names) + len(marks))
                    merged_list[::2] = names
                    merged_list[1::2] = marks
                    if not merged_list[0] in self.css_index:
                        self.css_index[merged_list[0]] = []
                    self.css_index[merged_list[0]].append(merged_list[1:])

                    if owner in self.css_file_output:
                        css_owner = dict(self.css_file_output[owner],
                                         **self.__extract_css_declarations
                                             (rule_block))
                        self.css_file_output[owner] = css_owner
                    else:
                        css_owner = self.__extract_css_declarations(rule_block)
                        self.css_file_output[owner] = css_owner
            else:
                break
        return self.css_file_output, self.css_index

    def parse_inline_style(self, inline_style_data):
        """
        Rather than whole css file data, runs on only inline css.

        @param inline_style_data: Inline css rules of an html tag.
            For example: "color:red;font-style:arial"
        @type inline_style_data: str
        @return: For example: {color:red; font-style: arial}
        @rtype: dict
        """
        return self.__extract_css_declarations('{' + inline_style_data + '}')

    def __extract_css_declarations(self, rule_block):
        """
        Converts style rule declarations in str form to dictionary.

        @param rule_block: For example: "{color:red; font-style: arial}"
        @param rule_block: str
        @return: For example: {color:red; font-style: arial}
        @rtype: dict
        """
        out = {}
        ind = 0
        length = len(rule_block)
        while ind < length:
            match = self.__extract_rules.search(rule_block, ind)
            if match:
                ind = match.end()
                (key, value) = match.groups()
                key = key.rstrip().lstrip()
                value = value.rstrip().lstrip()

                out[key] = value
            else:
                break
        return out

    def __read_css_files(self):
        """
        Reads css file. This method is called when the data is supplied as file
        names.
        """
        for path in self.__file_list:
            try:
                tmpf = open(path)
                self.data += tmpf.read()
                tmpf.close()
            except:
                pass


def list_to_dict(p_list):
    """
    Converts list to dictionary. Even numbered elements are key, whereas odd
    numbered elements are values.

    @param p_list: list to be converted.
    @type p_list: list

    @return : Dictionary produced from list.
    @rtype: dict
    """
    tmp_dict = {}
    for elem in p_list:
        tmp_dict[elem[0]] = elem[1]
    return tmp_dict
