
<div class="to-be-translated">
	{{ bfe_translate(bfo) }}
<div class="translate-link"></div>

<br />

<div class="bfe-disclaimer">
	{{ bfe_disclaimer(bfo) }}
</div>

<div class="bfe-post-header">
	{{ bfe_post_header(bfo) }}
</div>

<div class="row">

	<div class="text span9 pull-right">
		{{ bfe_title(bfo, prefix='<h1 class="articleTitle">', suffix='</h1>') }}

		<div class="post-text">
			{{ bfe_abstract(bfo, escape="0",
				prefix_en='<div class="highlightable" style="margin-right:20px;"><span>',
				suffix_en='</span></div><br />') }}
		</div>

		<div class="bfe-citation-box">
			{{ bfe_citation_box(bfo) }}
		</div> <!-- end bfe-citation-box -->

		<div class="bfe-post-comments">
			{{ bfe_post_comments(bfo) }}
		</div> <!-- end bfe-post-comments -->

	</div>

	<div class="span3 associated-content pull-left">
		<div class="post-extra-data left-menu-well">
			{{ bfe_authors(bfo) }}
			<br />
			{{ bfe_record_dates(bfo) }}
			<br />
			{{ bfe_topic(bfo) }}
			<br />
			{{ bfe_tags(bfo) }}
			<br />
			{# WebTags #}
			{{ bfn_webtag_record_tags(record['recid'], current_user.get_id()) }}
			<br />
			{{ bfe_license(bfo) }}
			<br />
			{{ bfe_doi(bfo, prefix='<small><strong>DOI: </strong>', suffix='</small><br />') }}
		</div>

		<div class="bfe-blog-navigation">
			{{ bfe_blog_navigation_menu(bfo) }}
		</div> <!-- end bfe-blog-navigation -->

		<div class="bfe-actions">
			{{ format_record(recid, 'HDACT', ln=g.ln) }}
		</div>

		<div class="bfe-links-menu">
			{{ bfe_links_menu(bfo) }}
		</div>

 	</div>

</div> <!-- end row -->

<div id="bottom">  </div> <! -- end bottom -->
