{{ bfe_topbanner(bfo, prefix='<div style="padding-left:10px;padding-right:10px">', suffix='</div><hr/>') }}

<div style="padding-left:10px;padding-right:10px">
{{ bfe_title(bfo, prefix="<center><big><big><strong>", separator="<br /><br />", suffix="</strong></big></big></center>") }}
<p align="center">
{{ bfe_authors(bfo, suffix="<br />", limit="25", interactive="yes", print_affiliations="yes", affiliation_prefix="<small> (", affiliation_suffix=")</small>") }}
{{ bfe_addresses(bfo, ) }}
{{ bfe_affiliation(bfo, ) }}
{{ bfe_date(bfo, prefix="<br />", suffix="<br />") }}
{{ bfe_publisher(bfo, prefix="<small>", suffix="</small>") }}
{{ bfe_place(bfo, prefix="<small>", suffix="</small>") }}
{{ bfe_isbn(bfo, prefix="<br />ISBN: ") }}
</p>

<p style="margin-left: 15%; width: 70%">

{{ bfe_abstract(bfo, prefix_en="<small><strong>Abstract: </strong>", prefix_fr="<small><strong>Résumé: </strong>", suffix_en="</small><br />", suffix_fr="</small><br />") }}

{{ bfe_keywords(bfo, prefix="<br /><small><strong>Keyword(s): </strong></small>", keyword_prefix="<small>", keyword_suffix="</small>") }}

{{ bfe_notes(bfo, note_prefix="<br /><small><strong>Note: </strong>", note_suffix=" </small>", suffix="<br />") }}

{{ bfe_publi_info(bfo, prefix="<br /><br /><strong>Published in: </strong>") }}<br />
{{ bfe_doi(bfo, prefix="<small><strong>DOI: </strong>", suffix=" </small><br />") }}

{{ bfe_plots(bfo, width="200px", caption="no") }}

</div>

{{ bfe_appears_in_collections(bfo, prefix="<p style='margin-left: 10px;'><em>The record appears in these collections:</em><br />", suffix="</p>") }}

{# WebTags #}
{{ bfn_webtag_record_tags(record['recid'], current_user.get_id())|prefix('<hr />') }}