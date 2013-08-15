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
from invenio.search_engine import \
    search_pattern, get_fieldvalues, \
    get_creation_date
from invenio.bibrecord import create_record, record_xml_output
from invenio.webblog_utils import get_parent_blog, calculate_path
from invenio.config import CFG_BATCHUPLOADER_DAEMON_DIR, \
                           CFG_PREFIX, CFG_TMPDIR
from invenio.bibtask import  task_update_progress
from bs4 import BeautifulSoup
import bleach
import datetime
from invenio.langid import classify
from invenio.htmlutils import remove_html_markup


batchupload_dir = CFG_BATCHUPLOADER_DAEMON_DIR[0] == '/' and CFG_BATCHUPLOADER_DAEMON_DIR \
                          or CFG_PREFIX + '/' + CFG_BATCHUPLOADER_DAEMON_DIR
path_mets_attachedfiles = batchupload_dir + "/files/"
path_metadata = batchupload_dir + "/metadata/replace/"

tag_black_list = ['iframe', 'script', 'style', 'select', 'form', 'option']
tag_white_list = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                  'span', 'div', 'p', 'object', 'param', 'embed', 'blockquote',
                  'ul','li','ol', 'dl', 'dt', 'dd', 'br', 'a', 'pre',
                  'table', 'tbody', 'thead', 'tr', 'td', 'img']
attr_white_list = {'*': ['title'],
                   'a': ['href'],
                   'img': ['src', 'alt'],
                   'ul' : ['type', 'start'],
                   'li' : ['type'],
                   'object' : ['name', 'type', 'value', 'codebase', 'data', 'wmode', 'allowfullscreen', 'allowscriptaccess', 'src', 'rel', 'width', 'height'],
                   'param' : ['name', 'type', 'value', 'allowfullscreen', 'allowscriptaccess', 'src', 'rel', 'width', 'height'],
                   'embed' : ['name', 'type', 'value', 'allowfullscreen', 'allowscriptaccess', 'src', 'rel', 'width', 'height']
                   }


class MetsIngestion:

    def __init__(self, file_path):

        self.file_path = file_path
        self.file_name = os.path.basename(self.file_path)
        self.submission_id = self.file_name[:self.file_name.find(".xml")]
        ### self.attachments_dir = path_mets_attachedfiles + self.submission_id
        self.attachments_dir = os.path.join(calculate_path(path_mets_attachedfiles, self.submission_id[:-6]), self.submission_id) 
        self.mets_file_name = os.path.join(self.attachments_dir, self.file_name + '_mets')
        self.recid = None
        self.marc_record = None
        self.marc_record_xml = None
        self.marc_in_mets_record = None
        self.record_type = None

        f = open(self.file_path, 'r')
        mets = f.read()
        f.close()
        self.dom = parseString(mets)


    def create_fft_tag_node(self, file_name):
        """
        Creates FFT node inside the MARC record.
        """

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
        """
        Creates a new field (controlfield, datafield, subfield) inside
        the MARC record.
        """

        new_node = self.dom.createElement(type)
        if tag: # controlfield, datafield
            new_node.setAttribute('tag', tag)
            if type == "datafield":
                new_node.setAttribute('ind1', ind1)
                new_node.setAttribute('ind2', ind2)
        if code: # subfield
            new_node.setAttribute('code', code)
        if value:
            new_node.appendChild(self.dom.createTextNode(str(value)))

        return new_node


    def find_marc_node(self):
        """
        Returns the MARC record which is inside
        the given METS file.
        """

        for dmdSec in self.dom.firstChild.childNodes:
            if dmdSec.localName == 'dmdSec':
                for mdWrap in dmdSec.childNodes:
                    if mdWrap.localName == 'mdWrap':
                        for xmlData in mdWrap.childNodes:
                            if xmlData.localName == 'xmlData':
                                for record in xmlData.childNodes:
                                    if record.localName == 'record':
                                        return record


    def get_fieldvalue(self, tag, code):
        """
        Gets the value contained in the given tag.
        """

        for elem in self.marc_record.getElementsByTagName('datafield'):
            if elem.getAttribute('tag') == tag:
                for subfield in elem.getElementsByTagName('subfield'):
                    if subfield.getAttribute('code') == code:
                        return subfield.firstChild.data
                    else:
                        return None


    def get_record_type(self):
        """
        Gets the record type.
        """

        if self.record_type == None:
            self.record_type = self.get_fieldvalue(tag='980', code='a')


    def get_recid(self):
        """
        This function returns the recid of the coming record
        in case it is already into the repository.
        """

        record_url = self.get_fieldvalue(tag='520', code='u')
        if record_url:
            recid = search_pattern(p='520__u:' + record_url)
            return recid


    def create_fft_nodes(self):
        """
        Creates a FFT node for each of the attached files
        for the corresponding record (the original METS file is also
        included as FFT).
        """

        attached_files_list = os.listdir(self.attachments_dir)
        fft_nodes = [self.create_fft_tag_node(attached_file) \
                     for attached_file in attached_files_list]
        return fft_nodes


    def detect_language(self):
        """
        Detects the language in which the post or comment is written
        and adds it into the MARC tag '041__a'.
        """

        for tag in self.marc_record.getElementsByTagName('datafield'):
            if tag.getAttribute('tag')=='520':
                for subfield in tag.getElementsByTagName('subfield'):
                    if subfield.getAttribute('code')=='a':
                        try:
                            content_a = subfield.firstChild.data
                        except:
                            content_a = ""
                    elif subfield.getAttribute('code')=='b':
                        try:
                            content_b = subfield.firstChild.data
                        except:
                            content_b = ""

        if content_a:
            content = content_a
        elif content_b:
            content = content_b
        else:
            content = ""

        cleaned_content = remove_html_markup(content)
        ln = classify(cleaned_content)[0]
        new_node = self.create_new_field('datafield', tag='041', ind1='', ind2='')
        sub_node1 = self.create_new_field('subfield', code='a', \
                                          value=str(ln))
        new_node.appendChild(sub_node1)
        self.marc_record.appendChild(new_node)


    def replace_empty_author(self):
        """
        Replaces the empty author value with (unknown). If the
        author MARC tag is not provided, then creates it with value
        (unknown)
        """

        empty_author= "(unknown)"
        try:
            author = self.get_fieldvalue(tag='100', code='a')
        except:
            for tag in self.marc_record.getElementsByTagName('datafield'):
                if tag.getAttribute('tag')=='100':
                    self.marc_record.removeChild(tag)

            new_node = self.create_new_field('datafield', tag='100', ind1='', ind2='')
            sub_node1 = self.create_new_field('subfield', code='a', \
                                              value=empty_author)
            new_node.appendChild(sub_node1)
            self.marc_record.appendChild(new_node)


    def add_fft_nodes(self):
        """
        Adds the FFT tags for attached files.
        """

        for fft_node in self.create_fft_nodes():
            self.marc_record.appendChild(fft_node)


    def add_controlfield_tags(self):
        """
         Adds the controlfield tags for record and submission id's.
        """

        # before adding the recid, check if the coming
        # record is already into the repository
        from invenio.bibupload import create_new_record
        recid = self.get_recid()
        if recid:
            self.recid = recid[0]
        else:
            self.recid = create_new_record()
        self.marc_record.appendChild(self.create_new_field('controlfield',
                                                            tag='001', value=self.recid))
        self.marc_record.appendChild(self.create_new_field('controlfield',
                                                            tag='002', value=self.submission_id))


    def add_posted_year(self):
        """
        Adds the year in which the post or comment was posted.
        """

        try:
            posted_date = self.get_fieldvalue(tag='269', code='c')
        except:
            posted_date = ""

        if posted_date:
            if posted_date.find("ERROR") > -1:
                creation_date = get_creation_date(self.recid)
                date_datetime = datetime.datetime.strptime(creation_date, "%Y-%m-%d")
            else:
                date_datetime = datetime.datetime.strptime(posted_date, "%m/%d/%Y %I:%M:%S %p")

            posted_year = date_datetime.year

            new_node = self.create_new_field('datafield', tag='909', ind1='C', ind2='0')
            sub_node1 = self.create_new_field('subfield', code='y', \
                                              value=str(posted_year))
            new_node.appendChild(sub_node1)
            self.marc_record.appendChild(new_node)


    def add_parent_blog_topics(self):
        """
        Adds the topics of the parent blog.
        """

        if self.record_type == 'BLOGPOST':
            try:
                parent_blog_url = self.get_fieldvalue(tag='760', code='o')
            except Exception, e: # post coming without parent blog url
                wp = self.get_fieldvalue(tag='99999', code='watchpointid')
                log_file = open(CFG_TMPDIR + "/log_file", "a")
                log_file.write("Not parent blog url present in file %s, wp: %s. Error: %s\n" %
                                (self.file_name, wp, str(e)))
                log_file.close()
                raise Exception(str(e))

            if parent_blog_url:
                parent_blog_recid = search_pattern(p='520__u:' + parent_blog_url)

        elif self.record_type == 'COMMENT':
            try:
                parent_post_url = self.get_fieldvalue(tag='773', code='o')
            except Exception, e: # comment coming without parent post url
                wp = self.get_fieldvalue(tag='99999', code='watchpointid')
                log_file = open(CFG_TMPDIR + "/log_file", "a")
                log_file.write("Not parent post url present in file %s, wp: %s. Error: %s\n" %
                                (self.file_name, wp, str(e)))
                log_file.close()
                raise Exception(str(e))

            if parent_post_url:
                parent_post_recid = search_pattern(p='520__u:' + parent_post_url)
                parent_blog_recid = get_parent_blog(parent_post_recid)

        try:
            topics = get_fieldvalues(parent_blog_recid, "654__a")
            for topic in topics:
                new_node = self.create_new_field('datafield', tag='654', ind1='', ind2='')
                sub_node1 = self.create_new_field('subfield', code='a', \
                                                  value=topic)
                new_node.appendChild(sub_node1)
                self.marc_record.appendChild(new_node)
        except:
            pass


    def add_parent_blog_visibility(self):
        """
        Adds the visibility of the parent blog.
        """

        if self.record_type == 'BLOGPOST':
            try:
                parent_blog_url = self.get_fieldvalue(tag='760', code='o')
            except Exception, e: # post coming without parent blog url
                wp = self.get_fieldvalue(tag='99999', code='watchpointid')
                log_file = open(CFG_TMPDIR + "/log_file", "a")
                log_file.write("Not parent blog url present in file %s, wp: %s. Error: %s\n" %
                                (self.file_name, wp, str(e)))
                log_file.close()
                raise Exception(str(e))

            if parent_blog_url:
                parent_blog_recid = search_pattern(p='520__u:' + parent_blog_url)

        elif self.record_type == 'COMMENT':
            try:
                parent_post_url = self.get_fieldvalue(tag='773', code='o')
            except Exception, e: # comment coming without parent post url
                wp = self.get_fieldvalue(tag='99999', code='watchpointid')
                log_file = open(CFG_TMPDIR + "/log_file", "a")
                log_file.write("Not parent post url present in file %s, wp: %s. Error: %s\n" %
                                (self.file_name, wp, str(e)))
                log_file.close()
                raise Exception(str(e))

            if parent_post_url:
                parent_post_recid = search_pattern(p='520__u:' + parent_post_url)
                parent_blog_recid = get_parent_blog(parent_post_recid)

        try:
            visibility = get_fieldvalues(parent_blog_recid, "542__f")
            new_node = self.create_new_field('datafield', tag='542', ind1='', ind2='')
            sub_node1 = self.create_new_field('subfield', code='f', \
                                              value=visibility)
            new_node.appendChild(sub_node1)
            self.marc_record.appendChild(new_node)
        except:
            pass


    def add_parent_blog_recid(self):
        """
        Adds the recid of the parent blog of a post.
        """

        try:
            parent_blog_url = self.get_fieldvalue(tag='760', code='o')
        except Exception, e: # post coming without parent blog url
            wp = self.get_fieldvalue(tag='99999', code='watchpointid')
            log_file = open(CFG_TMPDIR + "/log_file", "a")
            log_file.write("Not parent blog url present in file %s, wp: %s. Error: %s\n" %
                            (self.file_name, wp, str(e)))
            log_file.close()
            raise Exception(str(e))

        if parent_blog_url:
            parent_blog_recid = search_pattern(p='520__u:' + parent_blog_url)
            if parent_blog_recid:
                for tag in self.marc_record.getElementsByTagName('datafield'):
                    if tag.getAttribute('tag') == '760':
                        tag.appendChild(self.create_new_field('subfield', code="w", \
                                                              value=parent_blog_recid[0]))


    def add_parent_blog_info(self):
        """
        Adds the recid and url of the parent blog of a comment.
        """

        try:
            parent_post_url = self.get_fieldvalue(tag='773', code='o')
        except Exception, e: # comment coming without parent post url
            wp = self.get_fieldvalue(tag='99999', code='watchpointid')
            log_file = open(CFG_TMPDIR + "/log_file", "a")
            log_file.write("Not parent post url present in file %s, wp: %s. Error: %s\n" %
                            (self.file_name, wp, str(e)))
            log_file.close()
            raise Exception(str(e))

        if parent_post_url:
            parent_post_recid = search_pattern(p='520__u:' + parent_post_url)
            if parent_post_recid:
                parent_blog_recid = get_parent_blog(parent_post_recid)
                if parent_blog_recid:
                    parent_blog_url = get_fieldvalues(parent_blog_recid, "520__u")
                    new_node = self.create_new_field('datafield', tag='760', ind1='', ind2='')
                    if parent_blog_url:
                        sub_node1 = self.create_new_field('subfield', code='o', \
                                                          value=parent_blog_url[0])
                    sub_node2 = self.create_new_field('subfield', code='w', \
                                                      value=parent_blog_recid)
                    new_node.appendChild(sub_node1)
                    new_node.appendChild(sub_node2)
                    self.marc_record.appendChild(new_node)


    def add_parent_post_recid(self):
        """
        Adds the recid of the parent post of a comment.
        """

        try:
            parent_post_url = self.get_fieldvalue(tag='773', code='o')
        except Exception, e: # comment coming without parent post url
            wp = self.get_fieldvalue(tag='99999', code='watchpointid')
            log_file = open(CFG_TMPDIR + "/log_file", "a")
            log_file.write("Not parent post url present in file %s, wp: %s. Error: %s\n" %
                            (self.file_name, wp, str(e)))
            log_file.close()
            raise Exception(str(e))

        if parent_post_url:
            parent_post_recid = search_pattern(p='520__u:' + parent_post_url)
            if parent_post_recid:
                for tag in self.marc_record.getElementsByTagName('datafield'):
                    if tag.getAttribute('tag') == '773':
                        tag.appendChild(self.create_new_field('subfield', code="w", \
                                                              value=parent_post_recid[0]))


    def clean_html(self, content):
        """
        HTML cleaner.
        """

        # read content as BeautifulSoup object with utf-8 encoding
        text = BeautifulSoup(content)
        text.encode("utf-8")
        # with BeautifulSoup: Remove tags in tag_black_list, destroy contents
        try:
            for tag in tag_black_list:
                l = text.findAll(tag)
                for item in l:
                    item.decompose()
            # prettify- a BeautifulSoup operation to correctly indent the mark-up
            # with Bleach: remove tags and attributes not in whitelists, leave tag contents
            cleaned = bleach.clean(text.prettify(), strip="TRUE", \
                                   attributes=attr_white_list, tags=tag_white_list)
        except AttributeError, e:
            # TODO: write down this url to fetch this record again
            wrong_html_file = open(CFG_TMPDIR + "/wrong_html_file_%s" % self.file_name, "w")
            wrong_html_file.write(content.encode('utf8'))
            wrong_html_file.close()
            wp = self.get_fieldvalue(tag='99999', code='watchpointid')
            log_file = open(CFG_TMPDIR + "/log_file", "a")
            log_file.write("AttributeError in file %s, wp: %s. Error: %s\n" %
                            (self.file_name, wp, str(e)))
            log_file.close()
            # something is wrong with the HTML of the record, so let's stop this bibupload task
            # and notified this to the spider
            raise Exception(str(e))

        return cleaned


    def clean_marc_record_content(self):
        """
        Cleans the HTML content (values of MARC tags 520__a
        and 520__b) of the record.
        """

        for tag in self.marc_record.getElementsByTagName('datafield'):
            if tag.getAttribute('tag')=='520':
                for subfield in tag.getElementsByTagName('subfield'):
                    if subfield.getAttribute('code')=='a' or \
                        subfield.getAttribute('code')=='b':
                        try:
                            subfield.firstChild.data = self.clean_html(subfield.firstChild.data)
                        except:
                            pass


    def transform_marc(self, node, schema=""):
        """
        This function transforms the given MARC record
        to get it compatible with Invenio if schema is empty, or
        transforms the enriched MARC record
        to get it compatible with METS.
        """

        try:
            new_node = self.dom.createElement(schema + node.localName)
        except:
            pass

        if node.nodeType == 1:
            for attr in node._attrs:
                new_node.setAttribute(attr, node.getAttribute(attr))

            for sub_node in node.childNodes:
                new_node.appendChild(self.transform_marc(sub_node, schema))

        elif node.nodeType == 3:
            new_node = node.cloneNode(True)

        return new_node


    def transform_original_marc(self):
        """
        This function transforms the given MARC record
        to get it compatible with Invenio.
        """

        self.marc_record = self.transform_marc(self.find_marc_node())


    def transform_enriched_marc(self):
        """
        This function transforms the enriched MARC record
        to get it compatible with METS.
        """

        self.marc_in_mets_record = self.transform_marc(self.marc_record, schema="marc:")


    def generate_final_mets(self):
        """
        Updates the final METS with the MARC generated
        at pre-ingestion time.
        """

        for dmdSec in self.dom.firstChild.childNodes:
            if dmdSec.localName == 'dmdSec':
                for mdWrap in dmdSec.childNodes:
                    if mdWrap.localName == 'mdWrap':
                        for xmlData in mdWrap.childNodes:
                            if xmlData.localName == 'xmlData':
                                for record in xmlData.childNodes:
                                    if record.localName == 'record':
                                        xmlData.replaceChild(self.marc_in_mets_record, record)


    def enrich_original_marc(self):
        """
        This function extracts the MARC record coming inside
        the given METS file and transforms it to get it compatible
        with Invenio. The record is enriched with the recid, submission_id,
        parent recid and parent visibility.
        The HTML coming in tag 520__a is also cleaned.
        """

        # transforms MARC to MARC record compatible with Invenio
        self.transform_original_marc()
        # let's add the controlfield tags: recid and submission id
        self.add_controlfield_tags()
        # let's add the FFT tags with the attached files of the record
        self.add_fft_nodes()
        # let's get the record type
        self.get_record_type()
        # let's add the parent recid depending on the record type
        if self.record_type in ['BLOGPOST', 'COMMENT']:
            # cleans HTML content
            self.clean_marc_record_content()
            self.detect_language()
            self.replace_empty_author()
            self.add_parent_blog_visibility()
            self.add_parent_blog_topics()
            self.add_posted_year()

            if self.record_type == 'BLOGPOST':
                self.add_parent_blog_recid()

            if self.record_type == 'COMMENT':
                self.add_parent_post_recid()
                self.add_parent_blog_info()

        # let's organize the MARC structure
        rec = create_record(self.marc_record.toxml())
        self.marc_record_xml = record_xml_output(rec[0])
        self.marc_record = parseString(self.marc_record_xml).firstChild


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
    # under /files/file_name, while the extracted MARC will be
    # under /metadata/replace
    os.rename(file_path, m.mets_file_name)
    m.enrich_original_marc()
    # let's keep the final enriched MARC xml
    marc_file = open(m.file_path, 'w')
    marc_file.write(m.marc_record_xml)
    marc_file.close()
    # transforms the enriched MARC to the METS schema
    m.transform_enriched_marc()
    # store the enriched MARC into the original METS file
    m.generate_final_mets()
    # let's keep the final enriched METS xml
    mets_file = open(m.mets_file_name, 'w')
    mets_file.write(m.dom.toprettyxml().encode("utf-8"))
    mets_file.close()
    task_update_progress("Finished pre-processing record %s" % m.mets_file_name)

    return 1
