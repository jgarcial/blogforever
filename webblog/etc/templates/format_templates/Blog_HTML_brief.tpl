<div class="row">
        <div class="span2">
           {{ bfe_thumbnail_brief(bfo) }}
        </div>
        <div class="span10">
                <p>
                  <span style="font-size:17.5px"><i class="icon-col-Blogs"></i>
                <strong>{{ bfe_title_brief(bfo) }}</strong></span>
                </p>
                <p>
                  <i class="icon-col-Posts"></i> {{ bfe_blog_posts_brief(bfo) }}
                  {{ bfe_topic_brief(bfo) }}
                  {{ bfe_discussion(bfo) }}
                  {{ bfe_reviews(bfo) }}
                </p>
                {# WebTags #}
                {{ bfn_webtag_record_tags(record['recid'], current_user.get_id()) }}
        </div>
</div>
<hr>
