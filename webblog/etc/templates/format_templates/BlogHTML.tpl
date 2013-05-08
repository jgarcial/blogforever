
<div class="to-be-translated">
	{{ bfe_translate(bfo) }}
<div class="translate-link"></div>

<br />

<div class="bfe-disclaimer">
	{{ bfe_disclaimer(bfo) }}
</div>

<div class="row blog-record-page">
	<div class="span12">
		{{ bfe_title(bfo, prefix='<h2 class="articleTitle"> <i class="icon-col-Blogs"></i>', suffix='</h2>') }}
	</div>

	<div class="text span9 pull-right">
		<div class="bfe-blog-url-link">
			{{ bfe_blog_url_link(bfo) }}
		</div>

		<div style="padding-top:50px;">
			{{ bfe_citation_box(bfo) }}
		</div>

		<div class="bfe-blog-timeline">
			<div id="tl"
				data-source="{{ bfe_xtl_url(bfo) }}"
				data-initial-date="{{ bfe_last_post_date(bfo) }}"
				class="timeline-default dark-theme"
				style="height: 350px; margin: 2em;">
			</div>
		</div>

		<div class="bfe-blog-posts">
			{{ bfe_blog_posts(bfo) }}
		</div>
	</div> <!-- end text span9 -->

	<div class="span3">

		<div class="bfe-snapshot">
			{{ bfe_snapshot(bfo) }}
		</div> <!-- end bfe-snapshot -->

		<div class="post-extra-data">
			{{ bfe_record_dates(bfo) }}
			<br />
			{{ bfe_tags(bfo) }}
			<br />
			{{ bfe_license(bfo) }}
			<br />
			{{ bfe_doi(bfo, prefix='<small><strong>DOI: </strong>', suffix='</small><br />') }}
		</div>

		<div class="bfe-actions">
			{{ format_record(recid, 'HDACT', ln=g.ln) }}
		</div>

	</div>
	<div id="bottom">  </div>

</div> <!-- end blog-record-page -->

