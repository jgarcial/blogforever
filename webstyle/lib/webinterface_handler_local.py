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

def customize_app(app):

    Menu = type(app.config['menubuilder_map']['main'])
    submit = Menu('main.submit', 'Submit a Blog', 'submit', 2)
    app.config['menubuilder_map']['main'].children['submit'] = submit

    @app.context_processor
    def record_context():
    	from invenio.bibedit_utils import get_bibrecord
    	from invenio.bibrecord import record_get_field_value
        return dict(get_bibrecord=get_bibrecord, record_get_field_value=record_get_field_value)   
