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
Configuration parameters for html to pdf conversion. Most of them are related
with latex representation.
"""
import re
from invenio.config import CFG_WEBDIR
from invenio.config import CFG_ETCDIR

# If a workspace directory for converting html to latex is not specified,
# a temporary directory (tempfile.mkdtemp()) is created.
CFG_BIBFORMAT_EXPORT_DIR = CFG_WEBDIR + "/export"
CFG_BIBFORMAT_LATEX_TEMP_DIR = CFG_BIBFORMAT_EXPORT_DIR + '/tmp'

# Path to xelatex tool. If TeX Live is installed in default install directory,
# then the xelatex is on path
# "/usr/local/texlive/2013/bin/<your binary platform name>-linux/xelatex"
# "uname -i" command can be used to find platform name.
CFG_BIBFORMAT_PATH_PDF_CONVERTER = \
    "/usr/local/texlive/2013/bin/x86_64-linux/xelatex"

# The file extensions which will be kept in CFG_BIBFORMAT_EXPORT_DIR
# after pdflatex ends its job.
CFG_BIBFORMAT_LATEX_KEEP_FILE_EXTENSIONS = ['jpeg']

# Order of files is important. if there are two css rules in different two
# files, the latter's rule is used. This is due to behaviour of "dict(y, **x)".
# For better result, only one css file without duplicate rules should be
# preferred.
CFG_BIBFORMAT_CSS_FILES = []

# Regex to check img src attribute whether it is local path or url.
CFG_BIBFORMAT_IMG_SRC_URL = re.compile("http:")

# First line in latex document
CFG_BIBFORMAT_LATEX_HEADER = \
    """
    \\documentclass[10pt]{article}
    """
# Options for page layout. There is no need if "a4wide" package is used.
CFG_BIBFORMAT_LATEX_PAGE_SETTINGS = ""
#"""
#\\setlength{\\topmargin}{-.5in}
#\\setlength{\\textheight}{9in}
#\\setlength{\\oddsidemargin}{.125in}
#\\setlength{\\textwidth}{6.25in}
#"""

CFG_BIBFORMAT_LATEX_BEGIN_DOC = \
    """
    \\begin{document}
    """
CFG_BIBFORMAT_LATEX_END_DOC = \
    """
    \\end{document}
    """
# Packages to be used.
CFG_BIBFORMAT_LATEX_PACKAGES = \
    """
    \\usepackage{a4wide}
    \\usepackage{ulem}
    \\usepackage[dvipsnames,svgnames]{xcolor}
    \\usepackage{multirow}
    \\usepackage{wasysym}
    \\usepackage{amssymb}
    \\usepackage{hyperref}
    \\usepackage{graphicx}
    \\usepackage{seqsplit}
    \\usepackage{fontspec}
    \\usepackage{tabulary}
    \\usepackage[export]{adjustbox}
    \\setmainfont[Ligatures=TeX]{Linux Libertine O}
    \\usepackage{xeCJK}
    \\setCJKmainfont{WenQuanYi Micro Hei Mono}
    \\makeatletter
    \\renewcommand\\@seccntformat[1]{}
    \\makeatother
    """

# Regex to identify latex special characters in the source.
CFG_BIBFORMAT_LATEX_SPECIAL_CHARS_REGEX = re.compile(r"[&%$#_{}~^\\]")
CFG_BIBFORMAT_LATEX_SPECIAL_CHARS_LIST = ['&', '%', '$', '#', '_', '{',
                                          '}', '~', '^', '\\']

# Regex to find patterns of math formulas which are in already latex format.
# $SL(8,\mathbb{R})/SO(8)$
CFG_BIBFORMAT_LATEX_MATH_FORMULAS = re.compile("[$].*?[$]")
# Regex to split content into pieces according to start and end of math
# formulas. Later compare each piece whether they are in result of
# CFG_BIBFORMAT_LATEX_MATH_FORMULAS. If they are, do not escape special chars
# which will be handled by latex math.
CFG_BIBFORMAT_LATEX_ONLY_TEXT = re.compile("[^$]*[^$]")
# Regex to find words containing symbols more than provided number.
CFG_BIBFORMAT_LATEX_LONG_WORDS = re.compile("\S{20,}")

# Set to 1 to seek latex formulas in text. If it is set to 0, then
# CFG_BIBFORMAT_MATHJAX_DELIMITERS is ignored.
CFG_BIBFORMAT_MATHJAX_ENABLED = 1

# Delimiter characters for formulas. For example "$SL(8,\mathbb{R})/SO(8)$" or
# "$$SL(8,\mathbb{R})/SO(8)$$". The characters should not be in
# CFG_BIBFORMAT_LATEX_SPECIAL_CHARS_EQUIVALANCES. Otherwise, they are not
# escaped.
# CFG_BIBFORMAT_MATHJAX_DELIMITERS will be replaced with latex math
# delimiter "$".
CFG_BIBFORMAT_MATHJAX_DELIMITERS = "$"

# Regular expressions used for parsing css.
CFG_BIBFORMAT_CSS_PARSER_REGULAR_EXPRESSIONS = {
    'extract_css_block':
    re.compile("(([\w\s,.><#+\]\[+=~|:^\")(*$])+\s*([{].*?[}])\s*?)",
               re.DOTALL),
    'extract_selectors': re.compile(".*?(?={)", re.DOTALL),
    'parse_selectors': re.compile("([.#\w]+)"),
    'extract_rules':
    re.compile("([\s\w\-]+)[:\s]+([\w,.)(\s#\-%]+)(?=[;\s}]+)"),
}

CFG_BIBFORMAT_CSS_SELECTOR_COMPONENTS = re.compile("[^.#]+|[#.][^.#]+")

# Complex selector types for which css rules will be applied.
# Like div" "p, div">"p, div":"p, div"+"p etc.
CFG_BIBFORMAT_LATEX_CSS_SELECTORS = [" ", ">", "+", "~"]

# Apply css rules before handle of html tags.
CFG_BIBFORMAT_LATEX_STYLE_FIRST_TAGS = ['hr']

# The tags that may not have '/' character indicating end of tag.
# For example, while <hr/> is okay, <hr> causes problems.
CFG_BIBFORMAT_LATEX_NON_END_TAGS = ['hr', 'br']

# List of commands after which an environment can not be initialized. Check if
# these commands are encountered. If one or some of them are encountered, do
# not apply immediately.
# Insert to LatexConverter.__exceptional_active_text_styles list and apply to
# only tag content(pure text).
CFG_BIBFORMAT_LATEX_EXCEPTIONAL_COMMANDS = [r'\underline{',
                                            r'\sout{',
                                            r'$\overline{',
                                            r'\lowercase{',
                                            r'\uppercase{']

# Changing default img format may require extra effort during conversion.
# For "jpeg" case, before save operation, it is needed to convert Image
# object mode to "RGB" for example.
CFG_BIBFORMAT_LATEX_DEFAULT_IMG_FORMAT = 'png'
CFG_BIBFORMAT_LATEX_SUPPORTED_IMG_EXTS = ['png', 'jpg', 'jpeg', 'jbig2', 'jb2']
# Treated as 1 px is equal to provided number in units of cm.
CFG_BIBFORMAT_LATEX_PX_CM_SCALE = 0.021
# Amount of scale for a4 paper dimensions.
CFG_BIBFORMAT_LATEX_A4_SCALE = 0.5
# If an img element has neither width nor height values, then scale the image
# with the provided value.(Otherwise, the image may be too wide for the page.)
CFG_BIBFORMAT_LATEX_DEFAULT_IMG_SCALE = 0.75

# If font size is not specified in css, the default size to be used.
CFG_BIBFORMAT_LATEX_DEFAULT_FONT_SIZE = 10

CFG_BIBFORMAT_LATEX_KB_FILE = "%s/bibconvert/KB/latex-to-unicode.kb" \
                              % (CFG_ETCDIR, )
CFG_BIBFORMAT_LATEX_TO_UNICODE_KB_FILE_DICT = {}

# Representations of special latex chars.
CFG_BIBFORMAT_LATEX_SPECIAL_CHARS_EQUIVALANCES = {
    '&': r'\&',
    '%': r'\%',
    '$': r'\$',
    '#': r'\#',
    '_': r'\_',
    '{': r'\{',
    '}': r'\}',
    '~': r'\textasciitilde ',
    '^': r'\textasciicircum ',
    '\\': r'\textbackslash ',
}

CFG_BIBFORMAT_LATEX_COMMAND_CONSTRAINTS = {
    'li': {
        'h1': 'strong',
        'h2': 'strogn',
        'h3': 'strong',
        'h4': 'p',
        'h5': 'p',
        'h6': 'p'
    }
}

# Latex representatios of html alignment options.
CFG_BIBFORMAT_LATEX_ALIGNMENTS = {
    'default': 'c',
    'center': 'c',
    'right': 'r',
    'left': 'l',
    'td': 'l',  # Default alignment for td html tag.
    'th': 'c',  # Default alignment for th html tag.
}

# Latex commands used for rather than tag and css mappings.
CFG_BIBFORMAT_LATEX_COMMANDS = {
    'table_multicolumn': {
        'start': r'\multicolumn{%(col_num)s}{%(lb)s%(pos)s%(rb)s}{',
        'end': '}'
    },
    'table_multirow': {
        'start': r'\multirow{%(row_num)s}{%(width)s}{',
        'end': '}'
    },
    'table_cline': {
        'start': r'\cline{%s-%s}',
        'end': ''
    },
    'definecolor': {
        'start': '\\definecolor{%(color_name)s}{%(type)s}{%(val)s}',
        'end': ''
    },
    'fbox': {
        'start': r'\fbox{',
        'end': '}'
    },
    'hyperlink': {
        'start': '\n\\hyperlink{%s}{',
        'end': '}'
    },
    'hypertarget': {
        'start': '\n\\hypertarget{%s}{',
        'end': '}'
    },
    'href': {
        'start': '\n\\href{%s}{',
        'end': '}'
    }
}

# Html tags and their start, end latex representations.
CFG_BIBFORMAT_LATEX_REPRESENTATION_OF_HTML_TAGS = {
    '': {
        'end': '',
        'start': ''
    },
    '!doctype': {
        'end': '',
        'start': ''
    },
    'a': {
        'end': '',
        'start': ''
    },
    'abbr': {
        'end': '}',
        'start': '{\\ttfamily '
    },
    'acronym': {
        'end': '}',
        'start': '{\\ttfamily '
    },
    'address': {
        'end': '',
        'start': ''
    },
    'applet': {
        'end': '',
        'start': ''
    },
    'area': {
        'end': '',
        'start': ''
    },
    'b': {
        'end': '}',
        'start': '{\\bfseries '
    },
    'base': {
        'end': '',
        'start': ''
    },
    'basefont': {
        'end': '',
        'start': ''
    },
    'bdo': {
        'end': '',
        'start': ''
    },
    'big': {
        'end': '\\normalsize',
        'start': '\\LARGE'
    },
    'blockquote': {
        'end': '\\end{quotation}',
        'start': '\\begin{quotation}'
    },
    'br': {
        'end': '',
        'start': '~\\\\'
    },
    'button': {
        'end': '',
        'start': ''
    },
    'caption': {
        'end': '}',
        'start': '\n\\caption{\n'
    },
    'center': {
        'end': '\\end{center}',
        'start': '\\begin{center}'
    },
    'cite': {
        'end': '}',
        'start': '{\\itshape '
    },
    'code': {
        'end': '}',
        'start': '{\\ttfamily '
    },
    'col': {
        'end': '',
        'start': ''
    },
    'colgroup': {
        'end': '',
        'start': ''
    },
    'dd': {
        'end': '',
        'start': ''
    },
    'del': {
        'end': '}',
        'start': '\\sout{'
    },
    'dfn': {
        'end': '}',
        'start': '{\\itshape '
    },
    'dir': {
        'end': '\\end{itemize}',
        'start': '\\begin{itemize}'
    },
    'div': {
        'end': '',
        'start': ''
    },
    'dl': {
        'end': '\\end{description}',
        'start': '\\begin{description}'
    },
    'dt': {
        'end': ']',
        'start': '\t\\item['
    },
    'em': {
        'end': '}',
        'start': '{\\em '
    },
    'fieldset': {
        'end': '',
        'start': ''
    },
    'font': {
        'end': '',
        'start': ''
    },
    'form': {
        'end': '',
        'start': ''
    },
    'frame': {
        'end': '',
        'start': ''
    },
    'frameset': {
        'end': '',
        'start': ''
    },
    'h1': {
        'end': '}\n',
        'start': '\n\\section{'
    },
    'h2': {
        'end': '}\n',
        'start': '\n\\subsection{'
    },
    'h3': {
        'end': '}\n',
        'start': '\n\\subsubsection{'
    },
    'h4': {
        'end': '}\n',
        'start': '\n\\paragraph{'
    },
    'h5': {
        'end': '}\n',
        'start': '\n\\subparagraph{'
    },
    'h6': {
        'end': '}\n',
        'start': '\n\\subparagraph{'
    },
    'head': {
        'end': '',
        'start': ''
    },
    'hr': {
        'end': '',
        'start': '\\line(1,0){300}'
    },
    'i': {
        'end': '}',
        'start': '{\\itshape '
    },
    'iframe': {
        'end': '',
        'start': ''
    },
    'img': {
        'end': '',
        'start': """\\begin{figure}[h]
            \\begin{center}
            \\includegraphics[%(size_config)s]{%(path)s}
            %(caption)s \\end{center}
            \\end{figure} \\\\"""
    },
    'input': {
        'end': '',
        'start': ''
    },
    'ins': {
        'end': '}',
        'start': '{\\bfseries '
    },
    'isindex': {
        'end': '',
        'start': ''
    },
    'kbd': {
        'end': '}',
        'start': '{\\ttfamily '
    },
    'label': {
        'end': '',
        'start': ''
    },
    'legend': {
        'end': '',
        'start': ''
    },
    'li': {
        'end': '\n\t}',
        'start': '\n\t\\item{ '
    },
    'link': {
        'end': '',
        'start': ''
    },
    'map': {
        'end': '',
        'start': ''
    },
    'menu': {
        'end': '\\end{itemize}',
        'start': '\n\\begin{itemize}'
    },
    'meta': {
        'end': '',
        'start': ''
    },
    'noframes': {
        'end': '',
        'start': ''
    },
    'noscript': {
        'end': '',
        'start': ''
    },
    'object': {
        'end': '',
        'start': ''
    },
    'ol': {
        'end': '\n\\end{enumerate}\n',
        'start': '\\begin{enumerate}\n'
    },
    'optgroup': {
        'end': '',
        'start': ''
    },
    'option': {
        'end': '',
        'start': ''
    },
    'p': {
        'end': '\n}',
        'start': '\n\\par{\n'
    },
    'param': {
        'end': '',
        'start': ''
    },
    'pre': {
        'end': '\\end{verbatim}\n',
        'start': '\n\\begin{verbatim}\n'
    },
    'q': {
        'end': '\\end{quote}',
        'start': '\\begin{quote}'
    },
    's': {
        'end': '}',
        'start': '\\sout{'
    },
    'samp': {
        'end': '}',
        'start': '{\\ttfamily '
    },
    'script': {
        'end': '',
        'start': ''
    },
    'select': {
        'end': '',
        'start': ''
    },
    'small': {
        'end': '\\normalsize ',
        'start': '\\scriptsize '
    },
    'span': {
        'end': '',
        'start': ''
    },
    'strike': {
        'end': '}',
        'start': '\\sout{'
    },
    'strong': {
        'end': '}',
        'start': '{\\bfseries '
    },
    'sub': {
        'end': '$',
        'start': '$_'
    },
    'sup': {
        'end': '}$',
        'start': '$^{'
    },
    'table': {
        'end': '\\end{tabulary} \\\\ \n',
        'start': '\\begin{tabulary}{\\textwidth}%s %s\n'
    },
    'tbody': {
        'end': '',
        'start': ''
    },
    'td': {
        'end': '',
        'start': ''
    },
    'textarea': {
        'end': '',
        'start': ''
    },
    'tfoot': {
        'end': '',
        'start': ''
    },
    'th': {
        'end': '}',
        'start': '{\\bfseries '
    },
    'thead': {
        'end': '',
        'start': ''
    },
    'title': {
        'end': '}',
        'start': '\\title{'
    },
    'tr_True': {
        'end': '\\\\ \\hline\n',
        'start': ''
    },
    #With border lines.
    'tr_False': {
        'end': '\\\\\n',
        'start': ''
    },
    #No border lines.
    'tt': {
        'end': '}',
        'start': '{\\ttfamily '
    },
    'u': {
        'end': '}',
        'start': '\\underline{'
    },
    'ul': {
        'end': '\\end{itemize}\n',
        'start': '\\begin{itemize}\n'
    },
    'var': {
        'end': '}',
        'start': '{\\ttfamily '
    },
}
# Css declarations and their start, end representations for possible values.
CFG_BIBFORMAT_LATEX_REPRESENTATION_OF_CSS_RULES = {
    'text-decoration': {
        'underline': {
            'start': r'\underline{',
            'end': '}'
        },
        'overline': {
            'start': r'$\overline{',
            'end': '}$'
        },
        'line-through': {
            'start': r'\sout{',
            'end': '}'
        },
    },
    'text-transform': {
        'uppercase': {
            'start': r'\uppercase{',
            'end': '}'
        },
        'lowercase': {
            'start': r'\lowercase{',
            'end': '}'
        },
    },
    'font-style': {
        'normal': {
            'start': r'{\normalfont ',
            'end': '}'
        },
        'initial': {
            'start': r'{\normalfont ',
            'end': '}'
        },
        'italic': {
            'start': r'{\itshape ',
            'end': '}'
        },
        'oblique': {
            'start': r'{\slshape ',
            'end': '}'
        },
    },
    'font-variant': {
        'normal': {
            'start': r'{\normalfont ',
            'end': '}'
        },
        'small-caps': {
            'start': r'{\scshape ',
            'end': '}'
        },
    },
    'font-weight': {
        'normal': {
            'start': r'{\normalfont ',
            'end': '}'
        },
        'bold': {
            'start': r'{\bfseries ',
            'end': '}'
        },
        'bolder': {
            'start': r'{\bfseries ',
            'end': '}'
        },
        'lighter': {
            'start': r'{\normalfont ',
            'end': '}'
        },
        '100': {
            'start': r'{\normalfont ',
            'end': '}'
        },
        '200': {
            'start': r'{\normalfont ',
            'end': '}'
        },
        '300': {
            'start': r'{\normalfont ',
            'end': '}'
        },
        '400': {
            'start': r'{\normalfont ',
            'end': '}'
        },
        '500': {
            'start': r'{\normalfont ',
            'end': '}'
        },
        '600': {
            'start': r'{\normalfont ',
            'end': '}'
        },
        '700': {
            'start': r'{\bfseries ',
            'end': '}'
        },
        '800': {
            'start': r'{\bfseries ',
            'end': '}'
        },
        '900': {
            'start': r'{\bfseries ',
            'end': '}'
        },
    },
    'background-color': {
        'defined': {
            'start': '\n\\colorbox{%(val)s}{',
            'end': '}\n'
        },
    },
    'color': {
        'defined': {
            'start': r'{\color{%(val)s}',
            'end': '}'
        },
    },
    'font-size': {
        'xx-small': {
            'start': r'{\tiny ',
            'end': '}'
        },
        'x-small': {
            'start': r'{\scriptsize ',
            'end': '}'
        },
        'small': {
            'start': r'{\small ',
            'end': '}'
        },
        'medium': {
            'start': r'{\normalsize ',
            'end': '}'
        },
        'large': {
            'start': r'{\large ',
            'end': '}'
        },
        'x-large': {
            'start': r'{\LARGE ',
            'end': '}'
        },
        'xx-large': {
            'start': r'{\Huge ',
            'end': '}'
        },
        'variable': {
            'start': r'{\fontsize{%s}{%s} \selectfont ',
            'end': '}'
        }
    },
    'text-align': {
        'center': {
            'start': r'\begin{center}',
            'end': r'\end{center}'
        },
        'left': {
            'start': r'\begin{flushleft}',
            'end': r'\end{flushleft}'
        },
        'right': {
            'start': r'\begin{flushright}',
            'end': r'\end{flushright}'
        },
        'justify': {
            'start': '',
            'end': ''
        },
    },
    'font-family': {
        'serif': {
            'start': r'{\rmfamily ',
            'end': '}'
        },
        'sans-serif': {
            'start': r'{\sffamily ',
            'end': '}'
        },
        'cursive': {
            'start': r'{\itshape ',
            'end': '}'
        },
        'monospace': {
            'start': r'{\ttfamily ',
            'end': '}'
        },
        'fantasy': {
            'start': '',
            'end': ''
        },
    },
    'margin': {
        'auto': {
            'start': r'\begin{center}',
            'end': r'\end{center}'
        },
    },
    'float': {
        'left': {
            'start': r'\begin{center}',
            'end': r'\end{center}'
        },
        'right': {
            'start': r'\begin{center}',
            'end': r'\end{center}'
        },
    },
    'font_tag_size': {
        '1': {
            'start': r'{\tiny ',
            'end': '}'
        },
        '2': {
            'start': r'{\footnotesize ',
            'end': '}'
        },
        '3': {
            'start': r'{\normalsize ',
            'end': '}'
        },
        '4': {
            'start': r'{\large ',
            'end': '}'
        },
        '5': {
            'start': r'{\Large ',
            'end': '}'
        },
        '6': {
            'start': r'{\LARGE ',
            'end': '}'
        },
        '7': {
            'start': r'{\Huge ',
            'end': '}'
        },
        'default': {
            'start': r'{\normalsize ',
            'end': '}'
        }
    }
}
# Special html characters' representations can be mapped in two ways: By
# unicode number and by character command.


# Deprecated after use of XeTeX which supports utf-8 characters
# Unicode numbers of special html chars and their latex representations.
CFG_BIBFORMAT_HTML_SPECIAL_CHARS_BY_NUM = {
    '160': '',
    '161': '\\textexclamdown ',
    '162': '\\cent ',
    '163': '\\pounds ',
    '164': '\\currency ',
    '165': '\\textyen ',
    '166': '\\brokenvert ',
    '167': '\\S ',
    '169': '\\copyright ',
    '170': '\\textordfeminine ',
    '171': '\\guillemotleft ',
    '172': '$\\neg$',
    '174': '\\textregistered ',
    '176': '$\\degree$',
    '177': '$\\pm$',
    '178': '$^2$',
    '179': '$^3$',
    '180': '\'',
    '181': '$\\mu$',
    '182': '\\P ',
    '183': '$\\cdot$',
    '184': '\\c\\ ',
    '185': '$^1$',
    '186': '\\textordmasculine ',
    '187': '\\guillemotright ',
    '188': '$\\frac{1}{4}$',
    '189': '$\\frac{1}{2}$',
    '190': '$\\frac{3}{4}$',
    '191': '{?`}',
    '192': '\\`A ',
    '193': '\\\'A ',
    '194': '\\^A ',
    '195': '\\~A ',
    '196': '\\"A ',
    '197': '\\AA ',
    '198': '\\AE ',
    '199': '\\cC ',
    '200': '\\`E ',
    '201': '\\\'E ',
    '202': '\\^E ',
    '203': '\\"E ',
    '204': '\\`I ',
    '205': '\\\'I ',
    '206': '\\^I ',
    '207': '\\"I ',
    '208': '$\\eth$',
    '209': '\\~N ',
    '210': '\\`O ',
    '211': '\\\'O ',
    '212': '\\^O ',
    '213': '\\~O ',
    '214': '\\"O ',
    '215': '$\\times$',
    '216': '\\O ',
    '217': '\\`U ',
    '218': '\\\'U ',
    '219': '\\^U ',
    '220': '\\"U ',
    '221': '\\\'Y ',
    '222': '\\Thorn ',
    '223': '\\ss ',
    '224': '\\`a ',
    '225': '\\\'a ',
    '226': '\\^a ',
    '227': '\\~a ',
    '228': '\\"a ',
    '229': '\\aa ',
    '230': '\\ae ',
    '231': '\\c c ',
    '232': '\\`e ',
    '233': '\\\'e ',
    '234': '\\^e ',
    '235': '\\"e ',
    '236': '\\`i ',
    '237': '\\\'i ',
    '238': '\\^i ',
    '239': '\\"i ',
    '240': '$\\eth$',
    '241': '\\~n ',
    '242': '\\`o ',
    '243': '\\\'o ',
    '244': '\\^o ',
    '245': '\\~o ',
    '246': '\\"o ',
    '247': '$\\divide$',
    '248': '\\o ',
    '249': '\\`u ',
    '250': '\\\'u ',
    '251': '\\^u ',
    '252': '\\"u ',
    '253': '\\\'y ',
    '254': '\\thorn ',
    '255': '\\"y ',
    '338': '\\OE ',
    '339': '\\oe ',
    '34': '"',
    '352': '\\v{S} ',
    '353': '\\v{s} ',
    '376': '\\"Y ',
    '38': '\\& ',
    '60': '$<$',
    '62': '$>$',
    '710': '\\textasciicircum ',
    '732': '\\textasciitilde ',
    '8211': '--',
    '8212': '---',
    '8216': '`',
    '8217': '\'',
    '8220': '``',
    '8221': '\'\' ',
    '8224': '\\dag ',
    '8225': '\\ddag ',
    '8226': '$\\bullet$',
    '8230': '\\ldots ',
    '8240': '\\permil ',
    '8242': '$\\prime$',
    '8249': '\\guilsinglleft ',
    '8250': '\\guilsinglright ',
    '8254': '-',
    '8260': '/',
    '8364': '\\euro ',
    '8465': '$\\Im$',
    '8472': '$\\wp$',
    '8476': '$\\Re$',
    '8482': '$^{\\rm TM}$',
    '8501': '$\\aleph$',
    '8592': '$\\leftarrow$',
    '8593': '$\\uparrow$',
    '8594': '$\\rightarrow$',
    '8595': '$\\downarrow$',
    '8596': '$\\leftrightarrow$',
    '8629': '$\\hookleftarrow$',
    '8656': '$\\Leftarrow$',
    '8657': '$\\Uparrow$',
    '8658': '$\\Rightarrow$',
    '8659': '$\\Downarrow$',
    '8660': '$\\Leftrightarrow$',
    '8704': '$\\forall$',
    '8706': '$\\partial$',
    '8707': '$\\exists$',
    '8709': '$\\emptyset$',
    '8711': '$\\nabla$',
    '8712': '$\\in$',
    '8713': '$\\notin$',
    '8715': '$\\ni$',
    '8719': '$\\prod$',
    '8721': '$\\sum$',
    '8722': '$-$',
    '8727': '$\\ast$',
    '8730': '$\\surd$',
    '8733': '$\\propto$',
    '8734': '$\\infty$',
    '8736': '$\\angle$',
    '8743': '$\\wedge$',
    '8744': '$\\vee$',
    '8745': '$\\cup$',
    '8746': '$\\cap$',
    '8747': '$\\int$',
    '8756': '$\\therefore$',
    '8764': '$\\sim$',
    '8773': '$\\cong$',
    '8776': '$\\approx$',
    '8800': '$\\neq$',
    '8801': '$\\equiv$',
    '8804': '$\\leq$',
    '8805': '$\\geq$',
    '8834': '$\\subset$',
    '8835': '$\\supset$',
    '8836': '$\\nsubset$',
    '8838': '$\\subseteq$',
    '8839': '$\\supseteq$',
    '8853': '$\\oplus$',
    '8855': '$\\otimes$',
    '8869': '$\\perp$',
    '8901': '$\\cdot$',
    '8968': '$\\rceil$',
    '8969': '$\\lceil$',
    '8970': '$\\lfloor$',
    '8971': '$\\rfloor$',
    '9001': '$\\rangle$',
    '9002': '$\\langle$',
    '913': '$A$',
    '914': '$B$',
    '915': '$\\Gamma$',
    '916': '$\\Delta$',
    '917': '$E$',
    '918': '$Z$',
    '919': '$H$',
    '920': '$\\Theta$',
    '921': '$I$',
    '922': '$K$',
    '923': '$\\Lambda$',
    '924': '$M$',
    '925': '$N$',
    '926': '$\\Xi$',
    '927': '$O$',
    '928': '$\\Pi$',
    '929': '$P$',
    '931': '$\\Sigma$',
    '932': '$T$',
    '933': '$Y$',
    '934': '$\\Phi$',
    '935': '$X$',
    '936': '$\\Psi$',
    '937': '$\\Omega$',
    '940': "\\'{a}",
    '945': '$\\alpha$',
    '946': '$\\beta$',
    '947': '$\\gamma$',
    '948': '$\\delta$',
    '949': '$\\epsilon$',
    '950': '$\\zeta$',
    '951': '$\\eta$',
    '952': '$\\theta$',
    '953': '$\\iota$',
    '954': '$\\kappa$',
    '955': '$\\lambda$',
    '956': '$\\mu$',
    '957': '$\\nu$',
    '958': '$\\xi$',
    '959': '$o$',
    '960': '$\\pi$',
    '961': '$\\rho$',
    '962': '$\\varsigma$',
    '963': '$\\sigma$',
    '964': '$\\tau$',
    '965': '$\\upsilon$',
    '966': '$\\phi$',
    '967': '$\\chi$',
    '9674': '$\\lozenge$',
    '968': '$\\psi$',
    '969': '$\\omega$',
    '977': '$\\vartheta$',
    '982': '$\\varpi$',
    '9824': '$\\spadesuit$',
    '9827': '$\\clubsuit$',
    '9829': '$\\heartsuit$',
    '9830': '$\\diamondsuit$',
    '972': "\\'{o}",
    '973': '$\\acute{\\upsilon}$'
}
# Special html chars and their latex representations.
CFG_BIBFORMAT_HTML_SPECIAL_CHARS_BY_NAME = {
    'AElig': '\\AE ',
    'Aacute': '\\\'A ',
    'Acirc': '\\^A ',
    'Agrave': '\\`A ',
    'Alpha': '$A$',
    'Aring': '\\AA ',
    'Atilde': '\\~A ',
    'Auml': '\\"A ',
    'Beta': '$B$',
    'Ccedil': '\\cC ',
    'cedil': '\\c\\ ',
    'Chi': '$X$',
    'Dagger': '\\ddag ',
    'Delta': '$\\Delta$',
    'ETH': '$\\eth$',
    'Eacute': '\\\'E ',
    'Ecirc': '\\^E ',
    'Egrave': '\\`E ',
    'Epsilon': '$E$',
    'Eta': '$H$',
    'Euml': '\\"E ',
    'Gamma': '$\\Gamma$',
    'Iacute': '\\\'I ',
    'Icirc': '\\^I ',
    'Igrave': '\\`I ',
    'Iota': '$I$',
    'Iuml': '\\"I ',
    'Kappa': '$K$',
    'Lambda': '$\\Lambda$',
    'Mu': '$M$',
    'Ntilde': '\\~N ',
    'Nu': '$N$',
    'OElig': '\\OE ',
    'Oacute': '\\\'O ',
    'Ocirc': '\\^O ',
    'Ograve': '\\`O ',
    'Omega': '$\\Omega$',
    'Omicron': '$O$',
    'Oslash': '\\O ',
    'Otilde': '\\~O ',
    'Ouml': '\\"O ',
    'Phi': '$\\Phi$',
    'Pi': '$\\Pi$',
    'Psi': '$\\Psi$',
    'Rho': '$P$',
    'Scaron': '\\v{S} ',
    'Sigma': '$\\Sigma$',
    'THORN': '\\Thorn ',
    'Tau': '$T$',
    'Theta': '$\\Theta$',
    'Uacute': '\\\'U ',
    'Ucirc': '\\^U ',
    'Ugrave': '\\`U ',
    'Upsilon': '$Y$',
    'Uuml': '\\"U ',
    'Xi': '$\\Xi$',
    'Yacute': '\\\'Y ',
    'Yuml': '\\"Y ',
    'Zeta': '$Z$',
    'aacute': '\\\'a ',
    'acirc': '\\^a ',
    'acute': '\'',
    'aelig': '\\ae ',
    'agrave': '\\`a ',
    'alefsym': '$\\aleph$',
    'alpha': '$\\alpha$',
    'amp': '\\& ',
    'and': '$\\wedge$',
    'ang': '$\\angle$',
    'aring': '\\aa ',
    'asymp': '$\\approx$',
    'atilde': '\\~a ',
    'auml': '\\"a ',
    'beta': '$\\beta$',
    'brvbar': '\\brokenvert ',
    'bull': '$\\bullet$',
    'cap': '$\\cap$',
    'ccedil': '\\c c ',
    'cent': '\\cent ',
    'chi': '$\\chi$',
    'circ': '\\textasciicircum ',
    'clubs': '$\\clubsuit$',
    'cong': '$\\cong$',
    'copy': '\\copyright ',
    'crarr': '$\\hookleftarrow$',
    'cup': '$\\cup$',
    'curren': '\\currency ',
    'dArr': '$\\Downarrow$',
    'dagger': '\\dag ',
    'darr': '$\\downarrow$',
    'deg': '$\\degree$',
    'delta': '$\\delta$',
    'diams': '$\\diamondsuit$',
    'divide': '$\\divide$',
    'eacute': '\\\'e ',
    'ecirc': '\\^e ',
    'egrave': '\\`e ',
    'empty': '$\\emptyset$',
    'epsilon': '$\\epsilon$',
    'equiv': '$\\equiv$',
    'eta': '$\\eta$',
    'eth': '$\\eth$',
    'euml': '\\"e ',
    'euro': '\\euro ',
    'exist': '$\\exists$',
    'forall': '$\\forall$',
    'frac12': '$\\frac{1}{2}$',
    'frac14': '$\\frac{1}{4}$',
    'frac34': '$\\frac{3}{4}',
    'frasl': '/',
    'gamma': '$\\gamma$',
    'ge': '$\\geq$',
    'gt': '$>$',
    'hArr': '$\\Leftrightarrow$',
    'harr': '$\\leftrightarrow$',
    'hearts': '$\\heartsuit$',
    'hellip': '\\ldots ',
    'iacute': '\\\'i ',
    'icirc': '\\^i ',
    'iexcl': '\\textexclamdown ',
    'igrave': '\\`i ',
    'image': '$\\Im$',
    'infin': '$\\infty$',
    'int': '$\\int$',
    'iota': '$\\iota$',
    'isin': '$\\in$',
    'iquest': '{?`}',
    'iuml': '\\"i ',
    'kappa': '$\\kappa$',
    'lArr': '$\\Leftarrow$',
    'lambda': '$\\lambda$',
    'lang': '$\\langle$',
    'laquo': '\\guillemotleft ',
    'larr': '$\\leftarrow$',
    'lceil': '$\\lceil$',
    'ldquo': '``',
    'le': '$\\leq$',
    'lfloor': '$\\lfloor$',
    'lowast': '$\\ast$',
    'loz': '$\\lozenge$',
    'lsaquo': '\\guilsinglleft ',
    'lsquo': '`',
    'lt': '$<$',
    'mdash': '---',
    'micro': '$\\mu$',
    'middot': '$\\cdot$',
    'minus': '$-$',
    'mu': '$\\mu$',
    'nabla': '$\\nabla$',
    'nbsp': '',
    'ndash': '--',
    'ne': '$\\neq$',
    'ni': '$\\ni$',
    'not': '$\\neg$',
    'notin': '$\\notin$',
    'nsub': '$\\nsubset$',
    'ntilde': '\\~n ',
    'nu': '$\\nu$',
    'oacute': '\\\'o ',
    'ocirc': '\\^o ',
    'oelig': '\\oe ',
    'ograve': '\\`o ',
    'oline': '-',
    'omega': '$\\omega$',
    'omicron': '$o$',
    'oplus': '$\\oplus$',
    'or': '$\\vee$',
    'ordf': '\\textordfeminine ',
    'ordm': '\\textordmasculine ',
    'oslash': '\\o ',
    'otilde': '\\~o ',
    'otimes': '$\\otimes$',
    'ouml': '\\"o ',
    'para': '\\P ',
    'part': '$\\partial$',
    'permil': '\\permil ',
    'perp': '$\\perp$',
    'phi': '$\\phi$',
    'pi': '$\\pi$',
    'piv': '$\\varpi$',
    'plusmn': '$\\pm$',
    'pound': '\\pounds ',
    'prime': '$\\prime$',
    'prod': '$\\prod$',
    'prop': '$\\propto$',
    'psi': '$\\psi$',
    'quot': '"',
    'rArr': '$\\Rightarrow$',
    'radic': '$\\surd$',
    'rang': '$\\rangle$',
    'raquo': '\\guillemotright ',
    'rarr': '$\\rightarrow$',
    'rceil': '$\\rceil$',
    'rdquo': '\'\'',
    'real': '$\\Re$',
    'reg': '\\textregistered ',
    'rfloor': '$\\rfloor$',
    'rho': '$\\rho$',
    'rsaquo': '\\guilsinglright ',
    'rsquo': '\'',
    'scaron': '\\v{s}',
    'sdot': '$\\cdot$',
    'sect': '\\S ',
    'sigma': '$\\sigma$',
    'sigmaf': '$\\varsigma$',
    'sim': '$\\sim$',
    'spades': '$\\spadesuit$',
    'sub': '$\\subset$',
    'sube': '$\\subseteq$',
    'sum': '$\\sum$',
    'sup': '$\\supset$',
    'sup1': '$^1$',
    'sup2': '$^2$',
    'sup3': '$^3$',
    'supe': '$\\supseteq$',
    'szlig': '\\ss ',
    'tau': '$\\tau$',
    'there4': '$\\therefore$',
    'theta': '$\\theta$',
    'thetasym': '$\\vartheta$',
    'thorn': '\\thorn ',
    'tilde': '\\textasciitilde ',
    'times': '$\\times$',
    'trade': '$^{\\rm TM}$',
    'uArr': '$\\Uparrow$',
    'uacute': '\\\'u ',
    'uarr': '$\\uparrow$',
    'ucirc': '\\^u ',
    'ugrave': '\\`u ',
    'upsilon': '$\\upsilon$',
    'uuml': '\\"u ',
    'weierp': '$\\wp$',
    'xi': '$\\xi$',
    'yacute': '\\\'y ',
    'yen': '\\textyen ',
    'yuml': '\\"y ',
    'zeta': '$\\zeta$'
}
