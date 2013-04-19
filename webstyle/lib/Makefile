# $Id$

include ../../config.mk

LIBFILES = webinterface_handler_local.py

all:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make all && cd .. ;)
	@echo "Done.  Please run make test now."

test:
	@echo "Not implemented."

install:
	$(INSTALL) $(LIBFILES) $(LIBDIR)/python/invenio
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make install && cd .. ;)
	@echo "Done.  You may want to restart Apache now."
