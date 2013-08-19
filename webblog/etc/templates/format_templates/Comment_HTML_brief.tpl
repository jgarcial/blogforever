<div class="span9">
        <div class="row">
                <div class="span9">
                        <p><span style="font-size:17.5px"><i class="icon-col-Comments"></i>
                        <strong>{{ bfe_title_brief(bfo) }}</strong></span>
                        </p>
                        <p>
                        {{ bfe_post_content_brief(bfo, limit="1", escape="4") }}
                        {{ bfe_authors(bfo) }}
                        {{ bfe_discussion(bfo) }}
                        {{ bfe_reviews(bfo) }}
                        </p>
                        {# WebTags #}
                        {{ bfn_webtag_record_tags(record['recid'], current_user.get_id()) }}
                </div>
        </div>
        <hr>
</div>
