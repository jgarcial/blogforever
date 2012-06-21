# $Id$

include ../../../config.mk

LIBFILES = Check_URL.py

all:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make all && cd .. ;)
	#@echo "Done.  Please run make test now."

test:
	@echo "Done.  Please run make install now."

install:
	$(INSTALL) $(LIBFILES) $(LIBDIR)/python/invenio/websubmit_functions
	#$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make install && cd .. ;)
	@echo "Done.  You may want to restart Apache now."
