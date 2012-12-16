# $Id$

include ../../../config.mk

templates_DATA = websearch_index.html
CLEANFILES = *~ *.tmp


all:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make all && cd .. ;)
	@echo "Done.  Please run make test now."

test:
	@echo "Not implemented."

install:
	$(INSTALL) $(templates_DATA)
	@echo "Done.  You may want to restart Apache now."