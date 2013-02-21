# $Id$

include ../../../config.mk

templatesdir = $(ETCDIR)/templates
templates_DATA = websearch_index.html websearch_col.html websearch_helpers.html
EXTRA_DIST = $(templates_DATA)
CLEANFILES = *~ *.tmp

all:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make all && cd .. ;)
	@echo "Done.  Please run make test now."

test:
	@echo "Not implemented."

install:
	$(INSTALL) $(templates_DATA) $(templatesdir)
	@echo "Done.  You may want to restart Apache now."