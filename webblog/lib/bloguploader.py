# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2012 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
Blog Uploader:

Usage: /opt/invenio/bin/bloguploader [mode option]

Blog uploader mode options:
    Commands:
        NOTE: Options -i, -d and -U are mutually exclusive (XOR)!
        -i, --blog_insert      Insert a list of blogs
        -d, --blog_delete      Delete a list of blogs
        -U, --blog_update      Update a list of blogs

Examples:
    $ bloguploader -i list_new_blogs.xml
    $ bloguploader -d list_blogs_to_delete.xml
    $ bloguploader -U list_blogs_to_update.xml

"""

__revision__ = "$Id$"

import csv
import os
import time
from invenio.bibtask import task_init, task_update_progress, write_message, \
    fix_argv_paths, task_low_level_submission, task_get_option, task_set_option
from invenio.webblog_utils import get_blog_descendants
from invenio.webbasket import url_is_valid
from invenio.search_engine_utils import get_fieldvalues
from invenio.search_engine import perform_request_search


def _write_xml_file(blogs_xml, mode):
    """
    @param blogs_xml: the final marcxml output containing all
    the records to be inserted, deleted or updated by bibupload
    @type blogs_xml: string
    @param mode: insert, delete or update
    @type mode: string
    @return: final xml file which will be the input to bibupload
    @rtype: xml file
    """

    file_path = '/tmp/blogs_to_%s_%s.xml' % (mode, time.strftime("%Y%m%d_%H%M%S"))
    xml_file = open(file_path, 'w')
    xml_file.write(blogs_xml.encode('utf-8'))
    xml_file.close()
    return file_path


def _topic_is_valid(topic):
    """
    @param topic: blog topic
    @type topic: string
    @return: True if the given topic is valid, otherwise
    returns False
    @rtype: boolean
    """
    
    valid_topics = ["topic1", "topic2", "topic3"]
    return topic in valid_topics


def _license_is_valid(license):
    """
    @param license: blog license
    @type license: string
    @return: True if the given license is valid, otherwise
    returns False
    @rtype: boolean
    """

    valid_licenses = ["license1", "license2", "license3"]
    return license in valid_licenses


def _get_records_to_delete(blog_list):
    """
    @param blog_list: list of blogs to delete from the archive
    @type blog_list: list of lists where each individual list is
    a blog url
    @return: list of all the descendants of all the blogs the
    user wants to delete included the blogs themselfs
    @rtype: list of recids
    """

    records_to_delete = []
    for blog in blog_list:
        blog_url = blog[0]
        # search for the recid of the blog we want to delete
        list_recid = perform_request_search(p='520__u:"%s"' % blog_url)
        if list_recid:
            blog_recid = list_recid[0]
            # search for all the children recid's
            records_to_delete += get_blog_descendants(blog_recid)
            records_to_delete.append(blog_recid)
        else:
            raise Exception("Blog with the url '" + str(blog_url) +\
                            "' does not seem to exist in the archive")

    return records_to_delete


def _create_marcxml_header():
    """
    @return: the marcxml header
    @rtype: string
    """

    marcxml_output = '<?xml version="1.0" encoding="UTF-8"?>\n'
    marcxml_output += '<collection xmlns="http://www.loc.gov/MARC21/slim">'
    return marcxml_output


def _create_marcxml_footer(marcxml_output):
    """
    @param marcxml_output: the final marcxml output
    @type param: string
    @return: the final marcxml output plus marcxml footer
    @rtype: string
    """

    marcxml_output += '\n</collection>\n'
    return marcxml_output


def _create_marcxml_record_template(mode):
    """
    @param mode: insert, delete or update
    @type mode: string
    @return: the marcxml template for a record which 
    will be different depending on the input mode
    @rtype: string
    """

    record_template = """
    <record>"""
    
    if mode in ["update", "insert"]:
        if mode == "update":
            record_template += """
        <controlfield tag="001">%(recid)s</controlfield>"""

        if mode == "insert":
            record_template += """
        <datafield tag="520" ind1=" " ind2=" ">
            <subfield code="u">%(url)s</subfield>
        </datafield>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="a">%(coll)s</subfield>
        </datafield>"""
        
        record_template += """
        <datafield tag="245" ind1=" " ind2=" ">
            <subfield code="a">%(title)s</subfield>
        </datafield>
        <datafield tag="542" ind1="" ind2="">
            <subfield code="a">%(license)s</subfield>
        </datafield>
        <datafield tag="650" ind1="1" ind2="4">
            <subfield code="a">%(topic)s</subfield>
        </datafield>"""

    elif mode == "delete":
        record_template += """
        <controlfield tag="001">%(recid)s</controlfield>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="c">DELETED</subfield>
        </datafield>"""

    record_template += """
    </record>"""

    return record_template


def _transform_bloglist_to_marcxml(blog_list, mode):
    """
    @param blog_list: list of lists where each individual
    list is representing the blog the user wants to insert,
    delete or update
    @type blog_list: list of lists
    @param mode: insert, delete or update
    @type mode: string
    @return: the final marcxml output containing all
    the records to be inserted, deleted or updated by bibupload
    @rtype: string
    """

    marcxml_output = _create_marcxml_header()
    record_template = _create_marcxml_record_template(mode)

    if mode == "insert":
        for blog in blog_list:
            blog_url = blog[0]
            blog_title = blog[1]
            blog_topic = blog[2]
            blog_license = blog[3]
            record = record_template % {'coll': 'INITIALBLOG',
                                        'title': blog_title,
                                        'url': blog_url,
                                        'topic': blog_topic,
                                        'license': blog_license}
            marcxml_output += record

    elif mode == "update":
        for blog in blog_list:
            blog_url = blog[0]
            blog_title = blog[1]
            blog_topic = blog[2]
            blog_license = blog[3]
            list_recid = perform_request_search(p='520__u:"%s"' % blog_url)
            if list_recid:
                blog_recid = list_recid[0]
                record = record_template % {'recid': blog_recid,
                                            'title': blog_title,
                                            'topic': blog_topic,
                                            'license': blog_license}
                marcxml_output += record
            else:
                raise Exception("Blog with the url '" + str(blog_url) + "' does not seem to exist in the archive")

    elif mode == "delete":
        for recid in blog_list:
            record = record_template % {'recid': recid}
            marcxml_output += record

    marcxml_output = _create_marcxml_footer(marcxml_output)
    return marcxml_output


def _check_input_blogs(blog_list, mode):
    """
    @param blog_list: list of lists where each individual
    list is representing the blog the user wants to insert,
    delete or update
    @type blog_list: list of lists
    @param mode: insert, delete or update
    @type mode: string
    @return: False if any or some of the given
    blogs is/are not valid,
    or True if all of them are valid
    @rtype: tuple (False/True, error_message/ok_message)
    """

    result = ""
    if mode in ["insert", "update"]:
        for blog in blog_list:
            if len(blog) == 4:
                if not url_is_valid(blog[0])[0]:
                    result += "The given url '%s' is not valid. \n" % blog[0]
                # blog[1] is not mandatory
                if not _topic_is_valid(blog[2]):
                    result += "The given topic '%s' is not valid. \n" % blog[2]

                if not _license_is_valid(blog[3]):
                    result += "The given license '%s' is not valid. \n" % blog[3]
            else:
                write_message("Please check that the given file follows the established format: 'blog_url,[blog_name],blog_topic,blog_license'.")
                raise Exception("Please check that the given file follows the established format: 'blog_url,[blog_name],blog_topic,blog_license'.")

    elif mode == "delete":
        for blog in blog_list:
            if len(blog) == 1:
                if not url_is_valid(blog[0])[0]:
                    result += "The given url '%s' is not valid. \n" % blog[0]
            else:
                write_message("Please check that the given file follows the established format: 'blog_url'.")
                raise Exception("Please check that the given file follows the established format: 'blog_url'.")

    if result:
        return (False, result)
    else:
        return (True, "All input blogs are valid.")


def _get_blog_list(file_path):
    """
    @param file_path: file containing the list of blogs to 
    insert/delete/update in the archive.
    @type file_path: it is a csv file 
    @return: list of lists where each individual
    list is representing the blog the user wants to insert,
    delete or update
    @rtype: list of lists
    E.g:
    if "insert" or "update":
    blog_list = [['http://blogforever.eu', 'BlogForever', 'topic1', 'license1'], 
                ['http://phys.org/', 'Phys', 'topic2', 'license2']]
    if "delete":
    blog_list = [['http://blogforever.eu'], [http://phys.org/]]
    """
    
    fd = open(file_path, 'r')
    csv_file = csv.reader(fd, delimiter = ',')
    blog_list = [line for line in csv_file]
    fd.close()
    return blog_list


def _update_blogs(file_path):
    """
    @param file_path: file containing the list of blogs to update
    in the archive. Each blog is represented by its url, [title],
    topic and license.
    E.g: "blogs_to_update.csv"
    http://blogforever.eu,BlogForever,topic2,license2
    http://blogs.physicstoday.org/,Physicstoday,topic1,license2
    @type file_path: it is a csv file where the elements of
    each row (blog elements) are separated by commas.
    """

    blog_list = _get_blog_list(file_path)
    mode = "update"
    if blog_list:
        res = _check_input_blogs(blog_list, mode)
        if res[0]:
            updated_blogs_xml = _transform_bloglist_to_marcxml(blog_list, mode)
            xml_file = _write_xml_file(updated_blogs_xml, mode)
            task_low_level_submission('bibupload', 'webblog', '-c', xml_file)
        else:
            write_message(str(res[1]))
            raise Exception(res[1])
    else:
        write_message("There are not blogs to "+ str(mode))
        raise Exception("There are not blogs to "+ str(mode))


def _delete_blogs(file_path):
    """
    @param file_path: file containing the list of blogs to delete
    from the archive. Each blog is represented just by its url.
    E.g: "blogs_to_delete.csv"
    http://blogforever.eu
    http://blogs.physicstoday.org/
    @type file_path: it is a csv file where each row is the url of
    a blog to delete.
    """

    blog_list = _get_blog_list(file_path)
    mode = "delete"
    if blog_list:
        res = _check_input_blogs(blog_list, mode)
        if res[0]:
            records_to_delete = _get_records_to_delete(blog_list)
            deleted_blogs_xml = _transform_bloglist_to_marcxml(records_to_delete, mode)
            xml_file = _write_xml_file(deleted_blogs_xml, mode)
            task_low_level_submission('bibupload', 'webblog', '-c', xml_file)
        else:
            write_message(str(res[1]))
            raise Exception(res[1])
    else:
        write_message("There are not blogs to "+ str(mode))
        raise Exception("There are not blogs to " + str(mode))


def _insert_blogs(file_path):
    """
    @param file_path: file containing the list of blogs to insert
    in the archive. Each blog is represented by its url, [title],
    topic and license.
    E.g: "blogs_to_insert.csv"
    http://blogforever.eu,BlogForever,topic1,license1
    http://blogs.physicstoday.org/,Physicstoday,topic1,license3
    @type file_path: it is a csv file where the elements of
    each row (blog elements) are separated by commas.
    """

    blog_list = _get_blog_list(file_path)
    mode = "insert"
    if blog_list:
        res = _check_input_blogs(blog_list, mode)
        if res[0]:
            new_blogs_xml = _transform_bloglist_to_marcxml(blog_list, mode)
            xml_file = _write_xml_file(new_blogs_xml, mode)
            task_low_level_submission('bibupload', 'webblog', '-i', xml_file)
        else:
            write_message(str(res[1]))
            raise Exception(res[1])
    else:
        write_message("There are not blogs to "+ str(mode))
        raise Exception("There are not blogs to "+ str(mode))


def _bloguploader_task_run_core():
    """
     Run Blog Uploader Task
    """

    if task_get_option('file_path') is not None:
        if task_get_option("mode") == "blog_insert":
            task_update_progress("Uploading new blogs")
            write_message("Uploading new blogs started")
            _insert_blogs(task_get_option('file_path'))
            write_message("Uploading new blogs finished")
        elif task_get_option("mode") == "blog_delete":
            task_update_progress("Deleting blogs")
            write_message("Deleting blogs started")
            _delete_blogs(task_get_option('file_path'))
            write_message("Deleting blogs finished")
        elif task_get_option("mode") == "blog_update":
            task_update_progress("Updating blogs")
            write_message("Updating blogs started")
            _update_blogs(task_get_option('file_path'))
            write_message("Updating blogs finished")

        task_update_progress("Done.")
        return True
    else:
        return False


def _bloguploader_task_submit_check_options():
    """
    Checking options before submitting the task.
    It returns False if there are errors in the options.
    """

    if task_get_option('mode') is None:
        write_message("Please specify at least one mode!")
        return False

    if task_get_option('file_path') is None:
        write_message("Missing filename! -h for help.")
        return False
    elif not os.path.isfile(task_get_option('file_path')):
        write_message("No such file: '" + str(task_get_option('file_path'))+"'")
        return False

    return True


def _bloguploader_elaborate_submit_parameter(key, value, opts, args):
    """
    Elaborate task submission parameter. See bibtask's
    task_submit_elaborate_specific_parameter_fnc for help.
    """

    if key in ("-i", "--blog_insert"):
        task_set_option('mode', 'blog_insert')
    elif key in ("-d", "--blog_delete"):
        task_set_option('mode', 'blog_delete')
    elif key in ("-U", "--blog_update"):
        task_set_option('mode', 'blog_update')

    fix_argv_paths([args[0]])
    task_set_option('file_path', os.path.abspath(args[0]))

    return True


def main():
    """
    Main
    """

    task_init(authorization_action='runbloguploader',
              authorization_msg="Blog Uploader Task Submission",
              help_specific_usage=__doc__,
              version=__revision__,
              specific_params=("idU",
                               ["blog_insert",
                                "blog_delete",
                                "blog_update"]),
              task_submit_elaborate_specific_parameter_fnc=_bloguploader_elaborate_submit_parameter,
              task_submit_check_options_fnc=_bloguploader_task_submit_check_options,
              task_run_fnc=_bloguploader_task_run_core)

if __name__ == '__main__':
 main()
 