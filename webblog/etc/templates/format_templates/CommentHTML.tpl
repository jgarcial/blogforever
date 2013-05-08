
<div class="to-be-translated">
	{{ bfe_translate(bfo) }}
<div class="translate-link"></div>

<br />

<div class="bfe-disclaimer">
	{{ bfe_disclaimer(bfo) }}
</div>

<div class="bfe-comment-header">
	{{ bfe_comment_header(bfo) }}
</div>

<div class="row comment-record">

	<div class="span9 pull-right" >

		<div class="bfe-commment-author">
			{{ bfe_comment_author(bfo, prefix='<h4>', suffix='</h4>') }}
		</div>

		<div class="post-text">
			<i class="icon-col-Comments"></i>
			{{ bfe_abstract(bfo, escape='4',
				prefix_en='<div class="highlightable" style="margin-right:20px;"><span>',
				suffix_en='</span></div><br />') }}
		</div>

		<div class="bfe-citation-box">	
			{{ bfe_citation_box(bfo) }}
		</div>

	</div> <!-- end span9 -->

	<div class="span3 associated-content">

		<div class="post-extra-data">
			{{ bfe_authors(bfo) }}
			<br />
			{{ bfe_record_dates(bfo) }}
			<br />
			{{ bfe_tags(bfo) }}
			<br />
			{{ bfe_license(bfo) }}
			<br />
			{{ bfe_doi(bfo, prefix='<small><strong>DOI: </strong>', suffix='</small><br />') }}
		</div>

		<div class="bfe-comment-navigation">
			{{ bfe_comment_navigation_menu(bfo) }}
		</div>

		<div class="bfe-actions">
			{{ format_record(recid, 'HDACT', ln=g.ln) }}
		</div>

	</div>
	<div id="bottom">  </div>

</div> <!-- end blog-record-page -->
