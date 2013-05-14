from flask.ext.script import Manager

# sudo -u www-data  /opt/invenio/bin/inveniomanage blogforever load

manager = Manager(usage="Perform Blogforever operations")


@manager.command
def load():
    from invenio.bibupload_preprocess import bp_pre_ingestion
    from invenio.bibtask import task_low_level_submission
    from invenio.config import CFG_PREFIX
    import os

    print ">>> Going to load demo records..."
    run_sql("TRUNCATE schTASK")

    path_metadata = bp_pre_ingestion.path_metadata
    list_mets_files = os.listdir(path_metadata)
    blogs = []
    posts = []
    comments = []
    for mets_file in list_mets_files:
        if mets_file.find("Blog") > -1:
            blogs.append(mets_file)
        elif mets_file.find("Post") > -1:
            posts.append(mets_file)
        elif mets_file.find("Comment") > -1:
            comments.append(mets_file)

    sorted_list_mets_files = blogs + posts + comments

    for mets_file in sorted_list_mets_files:
        if os.path.exists(path_metadata + mets_file):
            task_low_level_submission('bibupload', 'batchupload', '-r', \
                                      path_metadata + mets_file, \
                                      '--pre-plugin=bp_pre_ingestion', \
                                      '--post-plugin=bp_post_ingestion')

#    os.system("%s/bin/bibupload %i" % (CFG_PREFIX, sorted_list_mets_files.index(mets_file) + 1))
#    for cmd in ["%s/bin/bibupload -u admin -i %s/var/tmp/demobibdata.xml" % (CFG_PREFIX, CFG_PREFIX),
#            "%s/bin/bibupload 1" % CFG_PREFIX,
#            "%s/bin/bibdocfile --textify --with-ocr --recid 97" % CFG_PREFIX,
#            "%s/bin/bibdocfile --textify --all" % CFG_PREFIX,
#            "%s/bin/bibindex -u admin" % CFG_PREFIX,
#            "%s/bin/bibindex 2" % CFG_PREFIX,
#            "%s/bin/bibreformat -u admin -o HB" % CFG_PREFIX,
#            "%s/bin/bibreformat 3" % CFG_PREFIX,
#            "%s/bin/webcoll -u admin" % CFG_PREFIX,
#            "%s/bin/webcoll 4" % CFG_PREFIX,
#            "%s/bin/bibrank -u admin" % CFG_PREFIX,
#            "%s/bin/bibrank 5" % CFG_PREFIX,
#            "%s/bin/bibsort -u admin -R" % CFG_PREFIX,
#            "%s/bin/bibsort 6" % CFG_PREFIX,
#            "%s/bin/oairepositoryupdater -u admin" % CFG_PREFIX,
#            "%s/bin/oairepositoryupdater 7" % CFG_PREFIX,
#            "%s/bin/bibupload 8" % CFG_PREFIX,]:
#    if os.system(cmd):
#        print "ERROR: failed execution of", cmd
#        sys.exit(1)

    print ">>> Demo records loaded successfully."

def main():
    from invenio.webinterface_handler_flask import create_invenio_flask_app
    app = create_invenio_flask_app()
    manager.app = app
    manager.run()

if __name__ == '__main__':
    main()
