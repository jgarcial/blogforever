div class="span9">
        <div class="row">
                <div class="span9">
                        <span style="font-size:17.5px"><i class="icon-col-Posts"></i>
                        <strong>{{ bfe_title_brief(bfo) }}</strong></span>
                        <p>
                        {{ bfe_post_content_brief(bfo, limit="1", escape="4") }}
                        </p>
                        <p>
                        {{ bfe_authors(bfo) }}
                        | {{ bfe_post_posted_date(bfo) }}
                        {{ bfe_post_comments_brief(bfo) }}
                        {{ bfe_discussion(bfo) }}
                        {{ bfe_reviews(bfo) }}
                        </p>
                </div>
        </div>
        <hr>
</div>
