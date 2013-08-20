# -*- coding: utf-8 -*-
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

"""
BlogForever local customization of Flask application
"""

from flask import current_app
from invenio.config import CFG_BLOG_TOPICS, CFG_SITE_SECURE_URL
from invenio.search_engine import get_nicely_ordered_collection_list

def customize_app(app):

    Menu = type(app.config['menubuilder_map']['main'])

    # menu for submission
    submit = Menu('main.submit', 'Submit a Blog', 'submit', 2)
    app.config['menubuilder_map']['main'].children['submit'] = submit

    # menu for collections
    collections = Menu('main.collections', 'Collections', 'search.index', 3)
    app.config['menubuilder_map']['main'].children['collections'] = collections
    collections.children = {}
    try:
        coll_list = get_nicely_ordered_collection_list()
    except:
        coll_list = []
    colls_nicely_ordered = [c[0] for c in reversed(coll_list)]
    for i, c in enumerate(colls_nicely_ordered):
        collections.children[c] = Menu('main.collections.'+c, c,
                                       'collection.'+c, i)

    # menu for topics
    valid_topics = CFG_BLOG_TOPICS.split(",")
    topics = Menu('main.collections', 'Topics', '', 11)
    app.config['menubuilder_map']['main'].children['topics'] = topics
    topics.children = {}
    for i, t in enumerate(valid_topics):
        search_topic_url = CFG_SITE_SECURE_URL + '/search?p=654__a:"%s"' % t
        topics.children[t] = Menu('main.topics.'+t, t,
                                  search_topic_url, i)

    @app.context_processor
    def record_context():
        from invenio.bibedit_utils import get_bibrecord
        from invenio.bibrecord import record_get_field_value
        from invenio.search_engine import get_record
        from invenio.bibrecord import record_xml_output
        from invenio.blog_network_generator import get_blog_citation_network, \
                                                    write_CMXXML, write_GEXF, \
                                                    get_author_citation_network, \
                                                    get_author_cocitation_network

        return dict(get_bibrecord=get_bibrecord,
                    record_get_field_value=record_get_field_value,
                    get_record=get_record,
                    record_xml_output=record_xml_output,
                    get_blog_citation_network=get_blog_citation_network,
                    get_author_citation_network=get_author_citation_network,
                    get_author_cocitation_network=get_author_cocitation_network,
                    write_CMXXML=write_CMXXML,
                    write_GEXF=write_GEXF
                    )
