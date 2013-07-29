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


import time
import collections
from lxml import etree
from invenio.search_engine import get_creation_date,\
                            perform_request_search,\
                            get_record
from invenio.bibrecord import record_xml_output
from invenio.webblog_utils import transform_format_date
from invenio.config import CFG_TMPDIR


def get_blog_citation_network(marcXML=""):
    """Generates a network of connected Blogs"""

    if not marcXML:
        # let's create the MARCXML of all the blog and
        # post records present in the repository
        marcXML = ""
        blog_and_posts_recids = perform_request_search(p="980__a:BLOG or 980__a:BLOGPOST")
        for recid in blog_and_posts_recids:
            r = get_record(recid)
            record_xml = record_xml_output(r)
            marcXML = marcXML + record_xml

    marcXML_path = CFG_TMPDIR + "/set_marcxml_records_to_cmx.xml"
    marcxml_output = """<collection xmlns="http://www.loc.gov/MARC21/slim">\n"""
    marcxml_output += marcXML
    marcxml_output += '\n</collection>\n'
    f = open(marcXML_path, "w")
    f.write(marcxml_output)
    f.close()
    # Read the document tree
    tree = etree.parse(marcXML_path)
    # Necessary collectors
    nodes = []
    linkevents = []
    uriRecipients = dict()
    networkNodeIDs = dict()
    # Set access expressions
    record_expr = "//xm:record[xm:datafield[@tag='980']]"
    blogRecordsExpr = "//xm:record[xm:datafield[@tag='980' and xm:subfield[@code='a']='BLOG']]"
    idExpr = "./xm:controlfield[@tag='001']/text()"
    uriExpr = "./xm:datafield[@tag='520']/xm:subfield[@code='u']/text()"
    titleExpr = "./xm:datafield[@tag='245']/xm:subfield[@code='a']/text()"
    platformExpr = "./xm:datafield[@tag='781']/xm:subfield[@code='a']/text()"
    # let's check the total number of records. We need at least 100 records to generate the network
    records = tree.xpath(record_expr, namespaces={'xm':'http://www.loc.gov/MARC21/slim'})
    if len(records) > 100:
        # Create List of nodes from BlogRecords
        blogs = tree.xpath(blogRecordsExpr, namespaces={'xm':'http://www.loc.gov/MARC21/slim'})
        for blog in blogs:
            identifier = blog.xpath(idExpr,\
                                    namespaces={'xm':'http://www.loc.gov/MARC21/slim'})[0]
            uri = blog.xpath(uriExpr,\
                            namespaces={'xm':'http://www.loc.gov/MARC21/slim'})[0]
            title = blog.xpath(titleExpr,\
                               namespaces={'xm':'http://www.loc.gov/MARC21/slim'})[0]
            try:
                platform = blog.xpath(platformExpr,\
                                      namespaces={'xm':'http://www.loc.gov/MARC21/slim'})[0]
            except:
                platform = ""

            newNode = NetworkNode(identifier, uri, title, platform, None, None)
            nodes.append(newNode)
            uriRecipients[uri] = identifier
            networkNodeIDs[identifier] = newNode

        # Add the blog posts to the list of recipients
        blogpostRecordsExpr = "//xm:record[xm:datafield[@tag='980' and xm:subfield[@code='a']='BLOGPOST']]"
        parentBlogExpr = "./xm:datafield[@tag='760']/xm:subfield[@code='w']/text()"
        # Create list of linkevents
        linksExpr = "./xm:datafield[@tag='856' and @ind2='0']/xm:subfield[@code='u']/text()"
        timestampExpr = "./xm:datafield[@tag='269']/xm:subfield[@code='c']/text()"
        linkeventCounter = 1
        blogposts = tree.xpath(blogpostRecordsExpr,\
                               namespaces={'xm':'http://www.loc.gov/MARC21/slim'})
        for post in blogposts:
            postid = post.xpath(idExpr,\
                                namespaces={'xm':'http://www.loc.gov/MARC21/slim'})[0]
            # Read ID of the Blog
            try:
                identifier = post.xpath(parentBlogExpr,\
                                        namespaces={'xm':'http://www.loc.gov/MARC21/slim'})[0]
            except:
                identifier = ""

            # Does the sender belong to a Blog/Network-Node?
            if not networkNodeIDs.has_key(identifier):
                continue
            else:
                senderID = identifier

            # Read URI
            uri = post.xpath(uriExpr, namespaces={'xm':'http://www.loc.gov/MARC21/slim'})[0]
            uriRecipients[uri] = identifier

            # Examine the links from the sender post
            for links in post.xpath(linksExpr,\
                                    namespaces={'xm':'http://www.loc.gov/MARC21/slim'}):
                # Does the link destination URL exist in the recipientsList?
                if uriRecipients.has_key(links):
                    # Read timestamp
                    timestamp = post.xpath(timestampExpr,\
                                           namespaces={'xm':'http://www.loc.gov/MARC21/slim'})[0]
                    # HACK
                    if timestamp.find("ERROR") > -1:
                        timestamp = get_creation_date(postid)
                        timestamp = time.strptime(timestamp, "%Y-%m-%d")
                    else:
                        timestamp = time.strptime(transform_format_date(timestamp,\
                                                                        format="%Y/%m/%d %H:%M:%S"),\
                                                                        "%Y/%m/%d %H:%M:%S")
                    # Create new linkevent and add it to the list
                    newLinkevent = LinkEvent(linkeventCounter, timestamp, networkNodeIDs.get(senderID),\
                                             networkNodeIDs.get(uriRecipients.get(links)),\
                                             None, None, None, None, None)
                    linkeventCounter += 1
                    linkevents.append(newLinkevent)

    return Network(nodes, linkevents)


def get_author_citation_network(marcXML=""):
    """Generates a network of connected Authors"""

    if not marcXML:
        # let's create the MARCXML of all the blog and
        # post records present in the repository
        marcXML = ""
        posts_and_comments_recids = perform_request_search(p="980__a:BLOGPOST or 980__a:COMMENT")
        for recid in posts_and_comments_recids:
            r = get_record(recid)
            record_xml = record_xml_output(r)
            marcXML = marcXML + record_xml

    marcxml_output = """<collection xmlns="http://www.loc.gov/MARC21/slim">\n"""
    marcxml_output += marcXML
    marcxml_output += '\n</collection>\n'
    marcXML_path = CFG_TMPDIR + "/set_marcxml_records_to_gexf.xml"
    f = open(marcXML_path, "w")
    f.write(marcxml_output)
    f.close()
    # Read the document tree
    tree = etree.parse(marcXML_path)
    # Necessary collectors
    nodes = []
    linkevents = []
    authorNames = set()
    authorNameNodes = dict()
    record_expr = "//xm:record[xm:datafield[@tag='980']]"
    # Create List of author names
    allAuthorsExpr = "//xm:datafield[@tag='100']/xm:subfield[@code='a']/text()"
    # let's check the total number of records. We need at least 100 records to generate the network
    records = tree.xpath(record_expr, namespaces={'xm':'http://www.loc.gov/MARC21/slim'})
    if len(records) > 100:
        authors = tree.xpath(allAuthorsExpr, namespaces={'xm':'http://www.loc.gov/MARC21/slim'})
        for authorName in authors:
            authorNames.add(authorName)

        # Create Create author node list
        authorNodeIDCounter = 1
        for authorName in authorNames:
            newAuthorNode = NetworkNode(authorNodeIDCounter, authorName,\
                                        None, None, None, None)
            authorNameNodes[authorName] = newAuthorNode
            nodes.append(newAuthorNode)
            authorNodeIDCounter += 1

        # Preparation for Linkevent-Creation
        timestampExpr = "./../../xm:datafield[@tag='269']/xm:subfield[@code='c']/text()"
        idExpr = "./xm:controlfield[@tag='001']/text()"
        linkeventCounter = 1
        # Check if the links of an author go to another blog or post
        for senderAuthorName in authorNames:
            # Search links of the author
            linksOfAuthorExpr = "//xm:record[xm:datafield[@tag='100' and xm:subfield[@code='a']='" +\
            senderAuthorName + "']]/xm:datafield[@tag='856' and @ind2='0']/xm:subfield[@code='u']/text()"
            try:
                links_of_authors = tree.xpath(linksOfAuthorExpr, namespaces={'xm':'http://www.loc.gov/MARC21/slim'})
            except:
                pass
            for link in links_of_authors:
                # Search link destination
                recipientAuthorExpr = "//xm:record[xm:datafield[@tag='520' and xm:subfield[@code='u']='" + link + "']]/xm:datafield[@tag='100']/xm:subfield[@code='a']"
                for recipientAuthor in tree.xpath(recipientAuthorExpr,\
                                                  namespaces={'xm':'http://www.loc.gov/MARC21/slim'}):
                    # Read timestamp
                    timestamp = recipientAuthor.xpath(timestampExpr,\
                                                      namespaces={'xm':'http://www.loc.gov/MARC21/slim'})[0]
                    # HACK
                    if timestamp.find("ERROR") > -1:
                        postid = recipientAuthor.xpath(idExpr,\
                                                       namespaces={'xm':'http://www.loc.gov/MARC21/slim'})[0]
                        timestamp = get_creation_date(postid)
                        timestamp = time.strptime(timestamp, "%Y-%m-%d")
                    else:
                        timestamp = time.strptime(transform_format_date(timestamp,\
                                                                        format="%Y/%m/%d %H:%M:%S"),\
                                                                        "%Y/%m/%d %H:%M:%S")
                    # Create new linkevent and add it to the list
                    linkevents.append(LinkEvent(linkeventCounter,\
                                                timestamp, authorNameNodes.get(senderAuthorName),\
                                                authorNameNodes.get(recipientAuthor.text),\
                                                None, None, None, None, None))
                    linkeventCounter += 1

    return Network(nodes, linkevents)


def get_author_cocitation_network(marcXML=""):
    """Generates a network of connected Authors
    based on Co-Citations"""

    if not marcXML:
        # let's create the MARCXML of all the blog and
        # post records present in the repository
        marcXML = ""
        posts_and_comments_recids = perform_request_search(p="980__a:BLOGPOST or 980__a:COMMENT")
        for recid in posts_and_comments_recids:
            r = get_record(recid)
            record_xml = record_xml_output(r)
            marcXML = marcXML + record_xml

    marcxml_output = """<collection xmlns="http://www.loc.gov/MARC21/slim">\n"""
    marcxml_output += marcXML
    marcxml_output += '\n</collection>\n'
    marcXML_path = CFG_TMPDIR + "/set_marcxml_records_to_gexf.xml"
    f = open(marcXML_path, "w")
    f.write(marcxml_output)
    f.close()
    # Read the document tree
    tree = etree.parse(marcXML_path)
    # Necessary collectors
    nodes = []
    linkevents = []
    authorNames = set()
    authorNameNetworkNodes = dict()
    record_expr = "//xm:record[xm:datafield[@tag='980']]"
    # Create List of author names
    allAuthorsExpr = "//xm:datafield[@tag='100']/xm:subfield[@code='a']/text()"
    # let's check the total number of records. We need at least 100 records to generate the network
    records = tree.xpath(record_expr, namespaces={'xm':'http://www.loc.gov/MARC21/slim'})
    if len(records) > 100:
        authors = tree.xpath(allAuthorsExpr, namespaces={'xm':'http://www.loc.gov/MARC21/slim'})
        for authorName in authors:
            authorNames.add(authorName)

        # Create Create author node list
        authorNodeIDCounter = 1
        for authorName in authorNames:
            newAuthorNode = NetworkNode(authorNodeIDCounter,\
                                        authorName, None, None, None, None)
            authorNameNetworkNodes[authorName] = newAuthorNode
            nodes.append(newAuthorNode)
            authorNodeIDCounter += 1

        # Identify unique links
        linksExpr = "//xm:datafield[@tag='856' and @ind2='0']/xm:subfield[@code='u']/text()"
        uniqueLinkList = set(tree.xpath(linksExpr, namespaces={'xm':'http://www.loc.gov/MARC21/slim'}))
        # Create Linkevents for Co-Citations
        timestampExpr = "./xm:datafield[@tag='269']/xm:subfield[@code='c']/text()"
        authorOfRecordExpr = "./xm:datafield[@tag='100']/xm:subfield[@code='a']/text()"
        idExpr = "./xm:controlfield[@tag='001']/text()"
        linkeventIDCounter = 1
        for link in uniqueLinkList:
            recordOfLinkExpr = "//xm:record[xm:datafield[@tag='856' and @ind2='0' and xm:subfield[@code='u']='" + link + "']]"
            try:
                duplicates = tree.xpath(recordOfLinkExpr,\
                                        namespaces={'xm':'http://www.loc.gov/MARC21/slim'})
            except:
                duplicates = []

            if len(duplicates) > 1:
                # Create Co-Citation Linkevents for Links that occur in more then one record
                duplicatedLinkRecords = list()
                for duplicate in duplicates:
                    timestamp = duplicate.xpath(timestampExpr,\
                                                namespaces={'xm':'http://www.loc.gov/MARC21/slim'})[0]
                    # HACK
                    if timestamp.find("ERROR") > -1:
                        postid = duplicate.xpath(idExpr,\
                                                 namespaces={'xm':'http://www.loc.gov/MARC21/slim'})[0]
                        timestamp = get_creation_date(postid)
                        timestamp = time.strptime(timestamp, "%Y-%m-%d")
                    else:
                        timestamp = time.strptime(transform_format_date(timestamp,\
                                                                        format="%Y/%m/%d %H:%M:%S"),\
                                                                        "%Y/%m/%d %H:%M:%S")
                    duplicatedLinkRecords.append((time.mktime(timestamp), duplicate))

                duplicatedLinkRecords.sort()
                targetAuthorNodes = set()
                for record in duplicatedLinkRecords:
                    if len(targetAuthorNodes) == 0 and len(record[1].xpath(authorOfRecordExpr,\
                                                                           namespaces={'xm':'http://www.loc.gov/MARC21/slim'})) > 0:
                        # The first author who used the link is not a sender
                        targetAuthorNodes.add(authorNameNetworkNodes.get(record[1].xpath(authorOfRecordExpr,\
                                                                                         namespaces={'xm':'http://www.loc.gov/MARC21/slim'})[0]))
                    elif len(record[1].xpath(authorOfRecordExpr, namespaces={'xm':'http://www.loc.gov/MARC21/slim'})) > 0:
                        # Creating linkevents for each repeated occurence of the link
                        newLinkevent = LinkEvent(linkeventIDCounter, time.localtime(record[0]),
                                                authorNameNetworkNodes.get(record[1].xpath(authorOfRecordExpr,\
                                                                                           namespaces={'xm':'http://www.loc.gov/MARC21/slim'})[0]),
                                                list(targetAuthorNodes), None, None, None, None, None)
                        linkevents.append(newLinkevent)
                        linkeventIDCounter += 1
                        targetAuthorNodes.add(authorNameNetworkNodes.get(record[1].xpath(authorOfRecordExpr,\
                                                                                         namespaces={'xm':'http://www.loc.gov/MARC21/slim'})[0]))
                    else:
                        recordIDExpr = "./xm:controlfield[@tag='001']/text()"
                        print "No author found for record",\
                        record[1].xpath(recordIDExpr,\
                        namespaces={'xm':'http://www.loc.gov/MARC21/slim'})[0]

    return Network(nodes, linkevents)


def write_CMXXML(network):
    """Creates a XML representation for Commetrix(CMX-XML)
    from the (generated) network"""

    if not isinstance(network, Network):
        return "Parameter is not from class Network"

    root = etree.Element("Network")

    # Add Nodes to the CMX-XML output
    for node in network.nodes:
        newNode = etree.SubElement(root,"Node", NodeID=str(node.identifier))
        if not node.detail1 == None:
            detail = etree.SubElement(newNode,"Detail1")
            detail.text = node.detail1
        if not node.detail2 == None:
            detail = etree.SubElement(newNode,"Detail2")
            detail.text = node.detail2
        if not node.detail3 == None:
            detail = etree.SubElement(newNode,"Detail3")
            detail.text = node.detail3
        if not node.detail4 == None:
            detail = etree.SubElement(newNode,"Detail4")
            detail.text = node.detail4
        if not node.detail5 == None:
            detail = etree.SubElement(newNode,"Detail5")
            detail.text = node.detail5

    # Add Linkevents to the CMX-XML output
    for linkevent in network.linkevents:
        newLinkevent = etree.SubElement(root,"Linkevent",\
                                        LinkeventID=str(linkevent.identifier),\
                                        LinkeventDate=time.strftime("%Y-%m-%d %H:%M:%S",\
                                                                    linkevent.timestamp))
        if not linkevent.sender == None:
            sender = etree.SubElement(newLinkevent, "LinkeventSender")
            sender.text = str(linkevent.sender.identifier)
        if not linkevent.recipients == None:
            if isinstance(linkevent.recipients, NetworkNode):
                recipientNode = etree.SubElement(newLinkevent, "LinkeventRecipient")
                recipientNode.text = str(linkevent.recipients.identifier)
            elif isinstance(linkevent.recipients, collections.MutableSequence):
                for recipient in linkevent.recipients:
                    recipientNode = etree.SubElement(newLinkevent,\
                                                     "LinkeventRecipient")
                    recipientNode.text = str(recipient.identifier)
        if not linkevent.detail1 == None:
            detail = etree.SubElement(newLinkevent,"Detail1")
            detail.text = linkevent.detail1
        if not linkevent.detail2 == None:
            detail = etree.SubElement(newLinkevent,"Detail2")
            detail.text = linkevent.detail2
        if not linkevent.detail3 == None:
            detail = etree.SubElement(newLinkevent,"Detail3")
            detail.text = linkevent.detail3
        if not linkevent.detail4 == None:
            detail = etree.SubElement(newLinkevent,"Detail4")
            detail.text = linkevent.detail4
        if not linkevent.detail5 == None:
            detail = etree.SubElement(newLinkevent,"Detail5")
            detail.text = linkevent.detail5

    return etree.tostring(root, pretty_print=True)


def write_GEXF(network):
    """Creates a XML representation for Gephi(GEXF)
    from the (generated) network"""

    if not isinstance(network, Network):
        return "Parameter is not from class Network"

    # Create the root node
    root = etree.Element("gexf", xmlns="http://www.gexf.net/1.2draft",\
                         version="1.2",
                         nsmap={"xsi":"http://www.w3.org/2001/XMLSchema-instance"},\
                         attrib={"{http://www.w3.org/2001/XMLSchema-instance}schemaLocation":"http://www.gexf.net/1.2draft http://www.gexf.net/1.2draft/gexf.xsd"})
    # Create metadata node
    metaNode = etree.SubElement(root, "meta", lastmodifieddate=time.strftime("%Y-%m-%d"))
    etree.SubElement(metaNode, "creator").text = "BlogForever Network Generator"
    # Add the graph branch
    graphNode = etree.SubElement(root, "graph", defaultedgetype="directed")
    # Add the nodes branch
    nodesNode = etree.SubElement(graphNode, "nodes", count=str(len(network.nodes)))
    # Add Nodes to the nodes branch
    for networkNode in network.nodes:
        newNode = etree.SubElement(nodesNode, "node", id=str(networkNode.identifier))
        if not networkNode.detail1 == None:
            newNode.set("label",networkNode.detail1)
        else: newNode.set("label","/")
    # Transform the linkevent structure to a flat edge structure
    edges = dict()
    for linkevent in network.linkevents:
        if edges.has_key(linkevent.sender.identifier):
            edgeTargets = edges.get(linkevent.sender.identifier)
            if not isinstance(edgeTargets, dict):
                print "Error: edgeTargets is not of type dictionary..."
                continue
            if isinstance(linkevent.recipients, NetworkNode):
                if edgeTargets.has_key(linkevent.recipients.identifier):
                    edgeTargets[linkevent.recipients.identifier] =\
                    edgeTargets.get(linkevent.recipients.identifier) + 1
                else:
                    edgeTargets[linkevent.recipients.identifier] = 1
            elif isinstance(linkevent.recipients, collections.MutableSequence):
                for recipient in linkevent.recipients:
                    if edgeTargets.has_key(recipient.identifier):
                        edgeTargets[recipient.identifier] =\
                        edgeTargets.get(recipient.identifier) + 1
                    else:
                        edgeTargets[recipient.identifier] = 1
        else:
            if isinstance(linkevent.recipients, NetworkNode):
                edgeTargets = {linkevent.recipients.identifier : 1}
            elif isinstance(linkevent.recipients, collections.MutableSequence):
                edgeTargets = dict()
                for recipient in linkevent.recipients:
                    edgeTargets[recipient.identifier] = 1
            edges[linkevent.sender.identifier] = edgeTargets

    # Add the edges branch
    edgesNode = etree.SubElement(graphNode, "edges")
    # Add Edges to the edges branch
    edgeIDCounter = 1
    for edgeSender, edgeTargets in edges.iteritems():
        for edgeRecipient, edgeWeight in edgeTargets.iteritems():
            etree.SubElement(edgesNode, "edge", id=str(edgeIDCounter),\
                             source=str(edgeSender), target=str(edgeRecipient),\
                             weight=str(edgeWeight))
            edgeIDCounter += 1

    return etree.tostring(root, pretty_print=True)


class NetworkNode:
    """Node in the generated Network"""

    def __init__(self, identifier, detail1, detail2,\
                 detail3, detail4, detail5):
        self.identifier = identifier
        self.detail1 = detail1
        self.detail2 = detail2
        self.detail3 = detail3
        self.detail4 = detail4
        self.detail5 = detail5


class LinkEvent:
    """Link event in the generated Network"""

    def __init__(self, identifier, timestamp, sender, recipients,\
                 detail1, detail2, detail3, detail4, detail5):
        self.identifier = identifier
        self.timestamp = timestamp
        self.sender = sender
        self.recipients = recipients
        self.detail1 = detail1
        self.detail2 = detail2
        self.detail3 = detail3
        self.detail4 = detail4
        self.detail5 = detail5


class Network:
    """ Generated Network"""
    def __init__(self, nodes, linkevents):
        self.nodes = nodes
        self.linkevents = linkevents
