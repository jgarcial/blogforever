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
from invenio.search_engine import perform_request_search, get_record
from invenio.bibrecord import record_get_field_value
from invenio.config import CFG_BATCHUPLOADER_DAEMON_DIR, \
                           CFG_PREFIX
from HTMLParser import HTMLParser

class HTMLStyleWasher(HTMLParser):

    def __init__(self, recid):
        HTMLParser.__init__(self)
        self.tag_black_list = ('style',
                               'iframe',
                               'script',)
        self.attribute_black_list = ('color',
                                     'style',
                                     'class',
                                     'id',)
        self.recid = recid
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
	from invenio.bibupload import create_new_record
        self.file_path = file_path
        self.file_name = os.path.basename(self.file_path)
        self.submission_id = self.file_name[:self.file_name.find(".xml")]
        self.daemon_dir = CFG_BATCHUPLOADER_DAEMON_DIR[0] == '/' and CFG_BATCHUPLOADER_DAEMON_DIR \
                          or CFG_PREFIX + '/' + CFG_BATCHUPLOADER_DAEMON_DIR
        self.attachments_dir = self.daemon_dir + "/mets/" + self.submission_id
        self.mets_file_name = os.path.join(self.attachments_dir, self.file_name + '_mets')
        self.recid = create_new_record()
        self.marc_record = None
        self.record_type = None
        f = open(self.file_path, 'r')
        mets = f.read()
        f.close()
        self.dom = parseString(mets)


    def create_fft_tag_node(self, file_name):
        ## JG: The path needs to be absolute!

        new_node = self.dom.createElement('datafield')
        new_node.setAttribute('tag', 'FFT')
        new_node.setAttribute('ind1', '')
        new_node.setAttribute('ind2', '')

        sub_node1 = self.dom.createElement('subfield')
        sub_node1.setAttribute('code', 'a')
        sub_node1.appendChild(self.dom.createTextNode(os.path.join(self.attachments_dir, file_name)))

        sub_node2 = self.dom.createElement('subfield')
        sub_node2.setAttribute('code', 't')
        sub_node2.appendChild(self.dom.createTextNode(""))

        sub_node3 = self.dom.createElement('subfield')
        sub_node3.setAttribute('code', 'd')
        sub_node3.appendChild(self.dom.createTextNode(""))

        new_node.appendChild(sub_node1)
        new_node.appendChild(sub_node2)
        new_node.appendChild(sub_node3)

        return new_node


    def get_attached_files_list(self):
        return os.listdir(self.attachments_dir)


    def produce_fft_nodes(self):
        ## JG: Has to check if the files are different copies of the same item
        ## and produce the tags accordingly
        out = []
        try:
            files_list = self.get_attached_files_list()
            for attached_file in files_list:
                out.append(self.create_fft_tag_node(attached_file))
            return out
        except:
            pass


    def find_marc_node(self):
        for dmdSec in self.dom.firstChild.childNodes:
            if dmdSec.localName == 'dmdSec':
                for mdWrap in dmdSec.childNodes:
                    if mdWrap.localName == 'mdWrap':
                        for xmlData in mdWrap.childNodes:
                            if xmlData.localName == 'xmlData':
                                for record in xmlData.childNodes:
                                    if record.localName == 'record':
                                        return record


    def create_control_tag_node(self, tag, content):
        new_node = self.dom.createElement('controlfield')
        new_node.setAttribute('tag', tag)
        new_node.appendChild(self.dom.createTextNode(str(content)))
        return new_node


    def generate_marc_xml(self):
        marc_output = '<?xml version="1.0" encoding="UTF-8"?>\n'
        marc_output += '<collection xmlns="http://www.loc.gov/MARC21/slim">\n'
        if self.marc_record is not None:
            marc_output += self.marc_record.toxml()
        marc_output += '</collection>\n'
        return marc_output.encode('utf-8')


    def extract_record_type(self):
        if self.record_type == None:
            for tag in self.marc_record.getElementsByTagName('datafield'):
                if tag.getAttribute('tag')=='980':
                    for subfield in tag.getElementsByTagName('subfield'):
                        if subfield.getAttribute('code')=='a':
                            return subfield.firstChild.data


    def insert_parent_blog_recid(self):
        for tag in self.marc_record.getElementsByTagName('datafield'):
            if tag.getAttribute('tag')=='760':
                for subfield in tag.getElementsByTagName('subfield'):
                    if subfield.getAttribute('code')=='o':
                        parent_blog_url =  subfield.firstChild.data
                        try:
                            parent_blog_recid = perform_request_search(p='520__u:' + parent_blog_url)[0]
                        except:
                            parent_blog_recid = ''
                        new_node = self.dom.createElement('subfield')
                        new_node.setAttribute('code', 'w')
                        new_node.appendChild(self.dom.createTextNode(str(parent_blog_recid)))
                        tag.appendChild(new_node)


    def insert_parent_post_recid(self):
        for tag in self.marc_record.getElementsByTagName('datafield'):
            if tag.getAttribute('tag')=='773':
                for subfield in tag.getElementsByTagName('subfield'):
                    if subfield.getAttribute('code')=='w':
                        parent_post_url =  subfield.firstChild.data
                        try:
                            parent_post_recid = perform_request_search(p='520__u:' + parent_post_url)[0]
                        except:
                            parent_post_recid = ''
                        new_node = self.dom.createElement('subfield')
                        new_node.setAttribute('code', 'w')
                        new_node.appendChild(self.dom.createTextNode(str(parent_post_recid)))
                        tag.appendChild(new_node)


    def transform_mets_to_marc(self):
        self.marc_record = self.transform_marc(self.find_marc_node())
        self.marc_record.appendChild(self.create_control_tag_node('001', self.recid))
        self.marc_record.appendChild(self.create_control_tag_node('002', self.submission_id))
        for fft_node in self.produce_fft_nodes():
            self.marc_record.appendChild(fft_node)
        self.record_type = self.extract_record_type()
        if self.record_type == 'BLOGPOST':
            self.insert_parent_blog_recid()
        if self.record_type == 'COMMENT':
            self.insert_parent_post_recid()


    def transform_marc(self, node):
        new_node = self.dom.createElement(node.localName)

        if node.nodeType == 1:
            for attr in node._attrs:
                new_node.setAttribute(attr, node.getAttribute(attr))

            for sub_node in node.childNodes:
                new_node.appendChild(self.transform_marc(sub_node))

        elif node.nodeType == 3:
            new_node = node.cloneNode(True)
            if node.parentNode.getAttribute('code') == 'a' \
                    and node.parentNode.parentNode.getAttribute('tag') == '520':
                sw = HTMLStyleWasher(self.recid)
                sw.clean(node.data)
                new_node.data = sw.output
        return new_node


def bp_pre_ingestion(file_path):
    """
    @param: file_path
    @type: string
    """
    m = MetsIngestion(file_path)
    os.rename(file_path, m.mets_file_name)
    m.transform_mets_to_marc()
    marc_file = open(m.file_path, 'w')
    marc_file.write(m.generate_marc_xml())
    marc_file.close()

    return 1

