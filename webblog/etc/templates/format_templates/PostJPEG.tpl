{#
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
#}
{% extends 'page_jpeg.html' %}
{% block body %}
    <div class="row">
        <div class="span4">
            <h4>Author(s)</h4>
            <span>
                {{ bfe_authors(bfo) }}
            </span>
        </div>
        <div class="span4">
            {{ bfe_record_dates(bfo, display_archived_date=False) }}
        </div>
        <div class="span4">
            {{ bfe_record_dates(bfo, display_posted_date=False) }}
        </div>
    </div>
    <div class="row" style="margin-top: 10px">
        <div class="span12">
            {{ bfe_abstract(bfo, escape="0") }}
        </div>
    </div>
    <div class="row" style="margin-top: 10px">
        <div class="span12">
            {{ bfe_post_comments(bfo, latest_comment_number=0, use_format="JPEGB") }}
        </div>
    </div>
{% endblock %}
