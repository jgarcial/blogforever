# $Id$

include ../../config.mk

bin_SCRIPTS = bloguploader


all:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make all && cd .. ;)
	@echo "Done.  Please run make test now."

test:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make test && cd .. ;)
	python $(LIBDIR)/python/invenio/template.py --check-custom-templates -v3
	@echo "Done.  Please run make install now."

install:
	install -g www-data -m 755 $(bin_SCRIPTS) $(BINDIR)
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make install && cd .. ;)
	@echo "Done.  You may want to restart Apache now."