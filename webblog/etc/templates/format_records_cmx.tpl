{#-
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
-#}

{% set final_MARCXML = "" %}
{% for recid in recids %}
{% set r = get_record(recid) %}
{% set record_xml = record_xml_output(r) %}
{% set final_MARCXML = final_MARCXML + record_xml%}
{% endfor %}
{% set network = get_blog_citation_network(final_MARCXML) %}
{{ write_CMXXML(network) }}