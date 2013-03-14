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

"""BlogForever ingestion pre-processing.
   Extracts the MARC record contained in the given METS and
   enriches it with the required tags.
"""

import os
from xml.dom.minidom import parseString
from invenio.search_engine import search_pattern
from invenio.config import CFG_BATCHUPLOADER_DAEMON_DIR, \
                           CFG_PREFIX
from HTMLParser import HTMLParser, HTMLParseError
from invenio.bibtask import  task_update_progress
from bs4 import BeautifulSoup
import bleach

batchupload_dir = CFG_BATCHUPLOADER_DAEMON_DIR[0] == '/' and CFG_BATCHUPLOADER_DAEMON_DIR \
                          or CFG_PREFIX + '/' + CFG_BATCHUPLOADER_DAEMON_DIR
path_mets_attachedfiles = batchupload_dir + "/files/"
path_metadata = batchupload_dir + "/metadata/replace/"


class HTMLStyleWasher(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
#        super(HTMLStyleWasher, self).__init__()
        self.tag_black_list = ('style',
                               'iframe',
                               'script',)
        self.attribute_black_list = ('color',
                                     'style',
                                     'class',
                                     'id',)
        self.output = ''
        self.black_listed_tag_count = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.tag_black_list:
            self.black_listed_tag_count += 1
        else:
            self.output += '<' + tag
            for (attr, value) in attrs:
                if attr not in self.attribute_black_list:
                    self.output += ' %s="%s"' % (attr, value)
            self.output += '>'

    def handle_endtag(self, tag):
        if tag in self.tag_black_list:
            if self.black_listed_tag_count:
                self.black_listed_tag_count -= 1
        else:
            self.output += '</' + tag + '>'

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_data(self, data):
        if self.black_listed_tag_count == 0:
            self.output += data

    def handle_charref(self, name):
        self.output += '&#' + name + ';'

    def handle_entityref(self, name):
        self.output += '&' + name + ';'

    def clean(self, html):
        self.reset()
        self.output = ''
        self.black_listed_tag_count = 0
        self.feed(html)
        self.close()


class MetsIngestion:

    def __init__(self, file_path):
        self.file_path = file_path
        self.file_name = os.path.basename(self.file_path)
        self.submission_id = self.file_name[:self.file_name.find(".xml")]
        self.attachments_dir = path_mets_attachedfiles + self.submission_id
        self.mets_file_name = os.path.join(self.attachments_dir, self.file_name + '_mets')
        # check if coming record already exists
        self.recid = None
        self.marc_record = None
        self.record_type = None
        f = open(self.file_path, 'r')
        mets = f.read()
        f.close()
        self.dom = parseString(mets)


    def generate_marc_xml(self):
        """
        Generates the final MARC xml.
        """

        marc_output = '<?xml version="1.0" encoding="UTF-8"?>\n'
        marc_output += '<collection xmlns="http://www.loc.gov/MARC21/slim">\n'
        if self.marc_record is not None:
            marc_output += self.marc_record.toxml()
        marc_output += '</collection>\n'
        return marc_output.encode('utf-8')


    def create_fft_tag_node(self, file_name):
        """Creates FFT node inside the MARC record."""

        FFT_node = self.create_new_field('datafield', tag='FFT', ind1='', ind2='')
        sub_node1 = self.create_new_field('subfield', code='a', \
                                          value=os.path.join(self.attachments_dir, file_name))
        sub_node2 = self.create_new_field('subfield', code='t')
        sub_node3 = self.create_new_field('subfield', code='d')

        FFT_node.appendChild(sub_node1)
        FFT_node.appendChild(sub_node2)
        FFT_node.appendChild(sub_node3)

        return FFT_node


    def create_new_field(self, type, tag="", ind1="", ind2="", code="", value=""):
        """Creates a new field (controlfield, datafield, subfield) inside
        the MARC record."""

        new_node = self.dom.createElement(type)
        if tag: # controlfield, datafield
            new_node.setAttribute('tag', tag)
            if tag == "datafield":
                new_node.setAttribute('ind1', ind1)
                new_node.setAttribute('ind2', ind2)
        if code: # subfield
            new_node.setAttribute('code', code)
        if value:
            new_node.appendChild(self.dom.createTextNode(str(value)))

        return new_node


    def get_fieldvalue(self, tag, code):
        """ Gets the value contained in the given tag. """

        for elem in self.marc_record.getElementsByTagName('datafield'):
            if elem.getAttribute('tag') == tag:
                for subfield in elem.getElementsByTagName('subfield'):
                    if subfield.getAttribute('code') == code:
                        return subfield.firstChild.data
                    else:
                        return None


    def insert_parent_blog_recid(self):
        """ Inserts the recid of the parent blog of a post. """

        parent_blog_url = self.get_fieldvalue(tag='760', code='o')
        if parent_blog_url:
            parent_blog_recid = search_pattern(p='520__u:' + parent_blog_url)
            if parent_blog_recid:
                for tag in self.marc_record.getElementsByTagName('datafield'):
                    if tag.getAttribute('tag') == '760':
                        tag.appendChild(self.create_new_field('subfield', code="w", \
                                                              value=parent_blog_recid[0]))


    def insert_parent_post_recid(self):
        """ Inserts the recid of the parent post of a comment. """

        parent_post_url = self.get_fieldvalue(tag='773', code='o')
        if parent_post_url:
            parent_post_recid = search_pattern(p='520__u:' + parent_post_url)
            if parent_post_recid:
                for tag in self.marc_record.getElementsByTagName('datafield'):
                    if tag.getAttribute('tag') == '773':
                        tag.appendChild(self.create_new_field('subfield', code="w", \
                                                              value=parent_post_recid[0]))


    def create_fft_nodes(self):
        """ Creates a FFT node for each of the attached files
        for the corresponding record (the original METS file is also
        included as FFT).
        """

        attached_files_list = os.listdir(self.attachments_dir)
        fft_nodes = [self.create_fft_tag_node(attached_file) \
                     for attached_file in attached_files_list]
        return fft_nodes


    def get_recid(self):
        """ This function returns the recid of the coming record
        in case it is already into the repository.
        """

        record_url = self.get_fieldvalue(tag='520', code='u')
        if record_url:
            recid = search_pattern(p='520__u:' + record_url)
            return recid


    def clean_html(self):
        """ This function cleans the HTML coming in tag 520__a.
        """

        for tag in self.marc_record.getElementsByTagName('datafield'):
            if tag.getAttribute('tag')=='520':
                for subfield in tag.getElementsByTagName('subfield'):
                    if subfield.getAttribute('code')=='a':
                        sw = HTMLStyleWasher()
                        try:
#                        tag_black_list = ['iframe', 'script', 'style', 'select', 'form', 'option']
#                        tag_white_list = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6',
#                                          'span', 'div', 'p', 'object', 'param', 'embed', 'blockquote',
#                                          'ul','li','ol', 'dl', 'dt', 'dd', 'br', 'a', 'pre',
#                                          'table', 'tbody', 'thead', 'tr', 'td', 'img']
#                        attr_white_list = {'*': ['title'],
#                                           'a': ['href'],
#                                           'img': ['src', 'alt'],
#                                           'ul' : ['type', 'start'],
#                                           'li' : ['type'],
#                                           'object' : ['name', 'type', 'value', 'allowfullscreen', 'allowscriptaccess', 'src', 'rel', 'width', 'height'],
#                                           'param' : ['name', 'type', 'value', 'allowfullscreen', 'allowscriptaccess', 'src', 'rel', 'width', 'height'],
#                                           'embed' : ['name', 'type', 'value', 'allowfullscreen', 'allowscriptaccess', 'src', 'rel', 'width', 'height']
#                                           }
#
#                        # Open file as BeautifulSoup object with utf-8 encoding.
#                        text = BeautifulSoup(subfield.firstChild.data)
#                        text.encode("utf-8")
#                        # With BeautifulSoup: Remove tags in tag_black_list, destroy contents.
#                        for s in text(tag_black_list): s.decompose()
#                        # Prettify- a BeautifulSoup operation to correctly indent the mark-up
#                        # With Bleach: Remove tags and attributes not in whitelists, leave tag contents.
#                        cleaned = bleach.clean(text.prettify(), strip="TRUE", \
#                                               attributes=attr_white_list, tags=tag_white_list)
#                        subfield.firstChild.data = cleaned
                            sw.clean(subfield.firstChild.data)
                        except HTMLParseError, e:
                            # TODO: write down this url to fetch this record again
                            wrong_html_file = open("/tmp/wrong_html_file_%s" % self.file_name, "w")
                            wrong_html_file.write(subfield.firstChild.data.encode('utf8'))
                            wrong_html_file.close()
                            wp = ""
                            for tag in self.marc_record.getElementsByTagName('datafield'):
                                if tag.getAttribute('tag')=='99999':
                                    for subfield in tag.getElementsByTagName('subfield'):
                                        if subfield.getAttribute('code')=='watchpointid':
                                            wp = subfield.firstChild.data
                            error_file = open("/tmp/error_file", "a")
                            error_file.write("HTMLParseError in file %s, wp: %s. Error: %s\n" %
                                             (self.file_name, wp, str(e)))
                            error_file.close()
                            # something is wrong with the HTML of the record, so let's stop this bibupload task
                            # and notified this to the spider
                            raise HTMLParseError(str(e))
                        subfield.firstChild.data = sw.output


    def find_marc_node(self):
        """Returns the MARC record which is inside
        the given METS file."""

        for dmdSec in self.dom.firstChild.childNodes:
            if dmdSec.localName == 'dmdSec':
                for mdWrap in dmdSec.childNodes:
                    if mdWrap.localName == 'mdWrap':
                        for xmlData in mdWrap.childNodes:
                            if xmlData.localName == 'xmlData':
                                for record in xmlData.childNodes:
                                    if record.localName == 'record':
                                        return record


    def transform_marc(self, node):
        """This function transforms the given MARC record
        to get it compatible with Invenio."""

        marc_node = self.dom.createElement(node.localName)
        if node.nodeType == 1:
            for attr in node._attrs:
                marc_node.setAttribute(attr, node.getAttribute(attr))

            for sub_node in node.childNodes:
                marc_node.appendChild(self.transform_marc(sub_node))

        elif node.nodeType == 3:
            marc_node = node.cloneNode(True)

        return marc_node


    def transform_mets_to_marc(self):
        """This function extracts the MARC record coming inside
        the given METS file and transforms it to get it compatible
        with Invenio. The record is enriched with the recid, submission_id,
        parent recid and parent visibility.
        The HTML coming in tag 520__a is also cleaned."""

        # transforms MARC to MARC record compatible with Invenio
        self.marc_record = self.transform_marc(self.find_marc_node())
        # let's clean the HTML content of the record
        self.clean_html()
        # before adding the recid, check if the coming
        # record is already in the repository
        recid = self.get_recid()
        if recid:
            self.recid = recid[0]
        else:
            from invenio.bibupload import create_new_record
            self.recid = create_new_record()
        # let's add thr recid
        self.marc_record.appendChild(self.create_new_field('controlfield',
                                                           tag='001', value=self.recid))
        # lets' add the submission id
        self.marc_record.appendChild(self.create_new_field('controlfield',
                                                           tag='002', value=self.submission_id))
        # let's add the FFT tag with the attached files of the record
        for fft_node in self.create_fft_nodes():
            self.marc_record.appendChild(fft_node)
        # let's add the record type
        if self.record_type == None:
            self.record_type = self.get_fieldvalue(tag='980', code='a')
        # let's add the parent recid depending on the record type
        if self.record_type == 'BLOGPOST':
            self.insert_parent_blog_recid()
        if self.record_type == 'COMMENT':
            self.insert_parent_post_recid()


def bp_pre_ingestion(file_path):
    """
    Plugin to extract the MARC record from the given METS file
    and transform it to get it compatible with Invenio
    @param file_path: absolute path of the METS file to pre-process
    @type file_path: string
    """

    m = MetsIngestion(file_path)
    task_update_progress("Started pre-processing record %s" % m.mets_file_name)
    # METS file will be stored as one of the attached files
    # under /mets/file_name, while the extracted MARC will be
    # under /metadata/replace
    os.rename(file_path, m.mets_file_name)
    m.transform_mets_to_marc()
    marc_file = open(m.file_path, 'w')
    marc_file.write(m.generate_marc_xml())
    marc_file.close()
    task_update_progress("Finished pre-processing record %s" % m.mets_file_name)

    return 1
