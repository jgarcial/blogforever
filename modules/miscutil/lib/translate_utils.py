## This file is part of Invenio.
## Copyright (C) 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013 CERN.
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
from invenio.config import CFG_SITE_LANG

INVENIO_LANGUAGE_CODES = {
    'af': 'Afrikaans',
    'ar': 'Arabic',
    'bg': 'Bulgarian',
    'ca': 'Catalan',
    'cs': 'Czech',
    'de': 'German',
    'el': 'Greek',
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'hr': 'Crotian',
    'gl': 'Galician',
    'ka': 'Georgian',
    'it': 'Italian',
    'lt': 'Lithuanian',
    'hu': 'Hungarian',
    'ja': 'Japanese',
    'no': 'Norwegian',
    'pl': 'Polish',
    'pt': 'Portuguese',
    'ro': 'Romanian',
    'ru': 'Russian',
    'sk': 'Slovak',
    'sv': 'Swedish',
    'uk': 'Ukrainian',
    'zh_CN': 'Chinese (Simplified)',
    'zh_TW': 'Chinese (Traditional)',
    'rw': 'Kinyarwanda'
}

LANGUAGE_CODES = {
    'Afrikaans': ['af'],
    'Albanian': ['sq'],
    'Arabic': ['ar'],
    'Belarusian': ['be'],
    'Bulgarian': ['bg'],
    'Catalan': ['ca'],
    'Chinese (Simplified)': ['zh-CN'],
    'Chinese (Traditional)': ['zh-TW'],
    'Crotian': ['hr'],
    'Czech': ['cs', 'cze'],
    'Danish': ['da'],
    'Dutch': ['nl'],
    'English': ['en', 'eng'],
    'Esperanto': ['eo', 'epo'],
    'Estonian': ['et'],
    'Filipino': ['tl'],
    'Finnish': ['fi', 'fin'],
    'French': ['fr', 'fre'],
    'Galician': ['gl'],
    'German': ['de', 'ger', 'deu'],
    'Greek': ['el', 'gre'],
    'Haitian Creole': ['ht'],
    'Hebrew': ['iw'],
    'Hindi': ['hi', 'hin'],
    'Hungarian': ['hu', 'hun'],
    'Icelandic': ['is'],
    'Indonesian': ['id'],
    'Irish': ['ga'],
    'Italian': ['it', 'ita'],
    'Japanese': ['ja', 'jpn'],
    'Korean': ['ko'],
    'Latvian': ['lv'],
    'Lithuanian': ['lt'],
    'Macedonian': ['mk'],
    'Malay': ['ms'],
    'Maltese': ['mt'],
    'Norwegian': ['no', 'nor'],
    'Persian': ['fa'],
    'Polish': ['pl'],
    'Portuguese': ['pt', 'por'],
    'Romanian': ['ro'],
    'Russian': ['ru', 'rus'],
    'Serbian': ['sr'],
    'Slovak': ['sk'],
    'Slovenian': ['sl'],
    'Spanish': ['es', 'spa'],
    'Swahili': ['sw'],
    'Swedish': ['sv'],
    'Thai': ['th'],
    'Turkish': ['tr', 'tur'],
    'Ukrainian': ['uk', 'ukr'],
    'Vietnamese': ['vi'],
    'Welsh': ['cy'],
    'Yiddish': ['yi']
}


def get_lang_name_from_code(l_code):
    """
    From given language code, returns the extended language name.
    """

    lang = ""
    if l_code in INVENIO_LANGUAGE_CODES.keys():
        lang = INVENIO_LANGUAGE_CODES[l_code]
    return lang


def is_in_lang_codes(l_name, l_code):
    """
    Checks whether a language code is in the list of given language's language
    codes.

    @param l_name -str- : The name of the language.
    @param l_code -str- : The code of the language that will be checked.
    """

    lang = ""
    if l_name in LANGUAGE_CODES.keys():
        if l_code in LANGUAGE_CODES[l_name]:
            lang = l_name

    return lang


def match_language_code(invenio_lang_code, record_lang_code):
    """
    Returns if the given invenio language code matches with any of the
    language codes

    @param invenio_lang_code: invenio language code from the keys of
                              L{INVENIO_LANGUAGE_CODES}
    @type invenio_lang_code: str

    @param: record_lang_code: value of the 041__a of a record
    @type record_lang_code: str

    @rtype: bool
    """
    return (invenio_lang_code in INVENIO_LANGUAGE_CODES.keys()
            # invenio_lang_code is a valid invenio language code
            and record_lang_code in
            LANGUAGE_CODES[INVENIO_LANGUAGE_CODES[invenio_lang_code]]
            # and given code matches with the other language codes
            )


def construct_translate_section():
    """
    Constructs drop-down language list.
    """
    out = """
<div class="languages">
<select id="language-combo-box">
    <option value="">Select Language</option>"""

    keys = sorted(LANGUAGE_CODES)
    for key in keys:
        out += """<option value="%(value)s">%(name)s</option>\n""" % {
                                    'value': LANGUAGE_CODES[key][0],
                                    'name': key
                                    }

    out += """
</select>
</div>
"""
    return out


def get_translate_script(sectional_node_class_name, ln=CFG_SITE_LANG,
                         load_script=False):
    """
    Returns google translate script
    """
    out = """
    <div id="translate-script">
        <script>
            function googleSectionalElementInit() {
              new google.translate.SectionalElement({
                sectionalNodeClassName: '%(sectional_node)s',
                controlNodeClassName: 'translate-link',
                background: '#ffffff',
                multilanguagePage: true
              }, 'google_sectional_element');
            }
        </script>
    """ % {
        'sectional_node': sectional_node_class_name,
    }
    if load_script:
        out += ("<script src=\"//translate.google.com/translate_a/"
                "element.js?cb=googleSectionalElementInit&ug=secti"
                "on&hl=%s\"></script>" % (ln,))

    out += "</div>"
    return out
