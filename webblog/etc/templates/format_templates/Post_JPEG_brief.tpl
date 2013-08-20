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
<div class="span12">
    <div class="row">
        <div class="span11" style="font-size:17.5px">
            <i class="icon-col-Posts"></i>
            <strong>{{ bfe_title_brief(bfo) }}</strong>
        </div>
    </div>
    <div class="row" style="padding:5px 0px">
        <div class="span11">
            {{ bfe_authors(bfo) }} | {{ bfe_post_posted_date(bfo) }}
            {{ bfe_post_comments_brief(bfo) }}
            {{ bfe_tags_brief(bfo) }}
            {{ bfe_reviews(bfo) }}
        </div>
    </div>
    <div class="row">
        <div class="span11">
            {{ bfe_abstract(bfo, escape="0") }}
        </div>
    </div>
    <hr>
</div>
